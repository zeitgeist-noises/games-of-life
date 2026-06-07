import pygame
import os
import math
import json
import numpy as np
from datetime import datetime
from ui.scenes.base_scene import Scene
from ui.components.sim_panel import SimulationPanel
from engine.ca import CellularAutomaton
from engine.genome import Genome


class EvolutionScene(Scene):
    def __init__(self, app, config):
        super().__init__(app)
        
        if config is None:
            self.config = {}
        else:
            self.config = config
        
        self.paused = False
        
        # state
        self.num_mutated_children = self.config.get("num_children", 8)
        self.total_panels = self.num_mutated_children + 1
        self.ca_shape = tuple(self.config.get("grid_size", [130, 100]))
        
        # undo history
        self.parent_history = []
        self.current_parent_genome = self.app.ca.genome
        
        # font
        self.label_font = pygame.font.SysFont('Consolas', 24)
        
        # children and panels
        self.children_ca = []
        self.sim_panels = []
        self.generate_generation(self.current_parent_genome)
        
        self.commands_info = [
            "[spc]   pause/resume",
            "[->]    step (if paused)",
            "[r]     reset grids",
            "[i]     init grids from .txt",
            "[c]     choose child",
            "[u]     undo (previous parent)",
            "[a]     auto-select",
            "[s]     save parent genome",
            "[esc]   exit evolution mode"
        ]

    def _calculate_grid_layout(self):
        W_box = self.app.screen_width
        H_box = self.app.screen_height - self.app.terminal.rect.height
        
        best_scale = 0
        best_layout = (1, self.total_panels)
        best_dims = (0, 0)
        
        ca_w, ca_h = self.ca_shape
        aspect = ca_w / ca_h
        
        # test all column counts for layout with largest panels
        for cols in range(1, self.total_panels + 1):
            rows = math.ceil(self.total_panels / cols)
            
            max_w = W_box / cols
            max_h = H_box / rows
            
            if max_w / aspect <= max_h:
                w_panel = max_w
                h_panel = max_w / aspect
            else:
                h_panel = max_h
                w_panel = max_h * aspect
                
            if w_panel > best_scale:
                best_scale = w_panel
                best_layout = (cols, rows)
                best_dims = (int(w_panel), int(h_panel))
                
        cols, rows = best_layout
        pw, ph = best_dims
        
        # centering offsets
        grid_w = cols * pw
        grid_h = rows * ph
        start_x = (W_box - grid_w) // 2
        start_y = (H_box - grid_h) // 2
        
        # apply geometries
        for i, panel in enumerate(self.sim_panels):
            r = i // cols
            c = i % cols
            x = start_x + c * pw
            y = start_y + r * ph
            panel.set_geometry(x, y, pw, ph)

    def generate_generation(self, parent_genome):
        self.children_ca = []
        self.sim_panels = []
        
        for i in range(self.total_panels):
            if i == 0:
                # child 0 is always the parent
                child_genome = parent_genome
            else:
                # other children are mutated
                child_genome = parent_genome.mutate(self.config)
                
            ca = CellularAutomaton(child_genome, self.ca_shape)
            panel = SimulationPanel(0, 0, ca)
            
            self.children_ca.append(ca)
            self.sim_panels.append(panel)
            
        self._calculate_grid_layout()

    def on_enter(self):
        self.app.terminal.set_commands_info(self.commands_info)
        pygame.display.set_caption("evolution mode")

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.paused = not self.paused
                self.app.terminal.log("paused" if self.paused else "resumed")
                
            elif event.key == pygame.K_ESCAPE:
                # return to main scene with child 0 genome
                self.app.ca.genome = self.children_ca[0].genome
                self.app.ca.grid = self.app.ca.reset_grid()
                self.app.change_scene("MAIN")
                
            elif event.key == pygame.K_RIGHT and self.paused:
                for ca in self.children_ca:
                    ca.step()
                    
            elif event.key == pygame.K_r:
                for ca in self.children_ca:
                    ca.grid = ca.reset_grid()
                self.app.terminal.log("all grids reset.")
                
            elif event.key == pygame.K_u:
                if self.parent_history:
                    self.current_parent_genome = self.parent_history.pop()
                    self.generate_generation(self.current_parent_genome)
                    self.app.terminal.log("reverted to previous generation parent.")
                else:
                    self.app.terminal.log("no undo history available.")
                    
            elif event.key == pygame.K_c:
                # select parent via terminal input
                self.app.terminal.start_prompt(
                    prompt_text="enter index of child to select (0-{}): ".format(self.total_panels - 1),
                    options=[str(i) for i in range(self.total_panels)],
                    callback=self._select_child
                )
                
            elif event.key == pygame.K_s:
                # save parent_genome (child 0)
                self.app.prompt_save_genome()
                
            elif event.key == pygame.K_i:
                # init all from text file
                import glob
                files = [os.path.basename(f) for f in glob.glob(os.path.join(self.app.states_dir, "*.txt"))] if hasattr(self.app, 'states_dir') else []
                # fallback pathing safely resolved inside GamesOfLife
                self.app.terminal.start_prompt(
                    prompt_text="load grid state to all (.txt): ",
                    options=files,
                    callback=self._do_load_state_all
                )
                
            elif event.key == pygame.K_a:
                self._run_auto_select()

    def _select_child(self, index_str):
        try:
            idx = int(index_str)
            if 0 <= idx < self.total_panels:
                # Store history for Undo
                self.parent_history.append(self.current_parent_genome)
                
                # Progress generation
                self.current_parent_genome = self.children_ca[idx].genome
                self.generate_generation(self.current_parent_genome)
                self.app.terminal.log(f"generation advanced using child {idx} as parent.")
            else:
                self.app.terminal.log("invalid index selection.")
        except ValueError:
            self.app.terminal.log("selection cancelled or invalid.")

    def _do_load_state_all(self, filename):
        if not filename:
            self.app.terminal.log("init cancelled.")
            return
        if not filename.endswith(".txt"):
            filename += ".txt"
            
        filepath = os.path.join(self.app.states_dir, filename)
        if os.path.exists(filepath):
            try:
                for ca in self.children_ca:
                    ca.load_custom_grid(filepath)
                self.app.terminal.log(f"loaded '{filename}' into all children.")
            except Exception as e:
                self.app.terminal.log(f"error initializing: {e}")
        else:
            self.app.terminal.log(f"file not found: {filename}")

    def _run_auto_select(self):
        fit_fn_name = self.config.get("fitness_function", "activity")
        self.app.terminal.log(f"evaluating fitness using: '{fit_fn_name}'...")
        
        best_idx = 0
        best_score = -float('inf')
        
        evaluators = {
            "activity": self._eval_activity,
        }
        
        eval_func = evaluators.get(fit_fn_name, self._eval_density)
        
        for idx, ca in enumerate(self.children_ca):
            # fast forward a clone to evaluate fitness
            temp_ca = CellularAutomaton(ca.genome, ca.grid.shape[::-1])
            temp_ca.grid = ca.grid.copy()
            
            # step forward for 50 steps
            history = []
            for _ in range(50):
                temp_ca.step()
                history.append(temp_ca.grid.copy())
                
            score = eval_func(temp_ca.grid, history)
            
            if score > best_score:
                best_score = score
                best_idx = idx
                
        self.app.terminal.log(f"auto-selected child {best_idx} (score: {best_score:.2f})")
        self._select_child(str(best_idx))

    def _eval_activity(self, final_grid, history):
        """Fitness: Measures persistent movement/oscillation over time."""
        changes = 0
        for i in range(1, len(history)):
            changes += np.sum(history[i] != history[i-1])
        return float(changes)

    def update(self):
        if not self.paused:
            for ca in self.children_ca:
                ca.step()

    def draw(self, screen):
        for i, panel in enumerate(self.sim_panels):
            panel.draw(screen)
            
            # draw child labels
            lbl_surf = self.label_font.render(f" {i} ", True, (255, 255, 255))
            
            # label background
            lbl_rect = lbl_surf.get_rect(topleft=(panel.x + 5, panel.y + 5))
            pygame.draw.rect(screen, (30, 30, 35), lbl_rect)
            pygame.draw.rect(screen, (100, 100, 100), lbl_rect, 1)
            
            screen.blit(lbl_surf, (panel.x + 5, panel.y + 5))
