import pygame
import glob
import os
import json
from ui.scenes.base_scene import Scene
from ui.scenes.evolution_scene import EvolutionScene
from ui.components.sim_panel import SimulationPanel
from ui.components.live_stats import LiveStats
from engine.genome import Genome


class MainScene(Scene):
    def __init__(self, app):
        super().__init__(app)
        self.paused = False
        
        # initial state
        self.show_genome_info = False
        self.info_font = pygame.font.SysFont('Consolas', 16)
        self.title_font = pygame.font.SysFont('Consolas', 24)
        
        self.sim_panel = SimulationPanel(
            x=0,
            y=0,
            ca=self.app.ca,
            cell_size=4
        )
        
        self.live_stats = LiveStats()
        
        self.commands_info = [
            "[spc]   pause/resume",
            "[->]    step (if paused)",
            "[r]     reset grid",
            "[n]     new random genome",
            "[alt+n] new genome (keep size)",
            "[m]     mutate genome",
            "[e]     evolution mode"
            "[g]     toggle genome info",
            "[s]     save to .json",
            "[l]     load from .json",
            "[i]     init from .txt"
        ]
        
        self._layout_components()
    
    def _layout_components(self):
        if self.show_genome_info:
            scale = 0.75
            available_w = int(self.app.screen_width * 0.75)
        else:
            scale = 1.0
            available_w = self.app.screen_width
        
        panel_w = self.app.ca.width * 4 * scale
        panel_h = self.app.ca.height * 4 * scale
        x = (available_w - panel_w) // 2
        y = 0
        
        self.sim_panel.set_geometry(x, y, panel_w, panel_h)

    def on_enter(self):
        self.app.terminal.set_commands_info(self.commands_info)
        self._update_title()

    def on_ca_changed(self):
        self.sim_panel.update_ca(self.app.ca)
        self.live_stats.reset()
        self._layout_components()
        self._update_title()

    def _update_title(self):
        k_size = self.app.ca.genome.kernel.shape[0]
        sparsity = self.app.ca.genome.sparsity
        pygame.display.set_caption(f"main mode | kernel: {k_size}x{k_size} | sparsity: {sparsity:.3f}")

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.paused = not self.paused
                self.app.terminal.log("paused" if self.paused else "resumed")
                
            elif event.key == pygame.K_RIGHT and self.paused:
                self.app.ca.step()
                
            elif event.key == pygame.K_r:
                self.app.ca.grid = self.app.ca.reset_grid()
                self.live_stats.reset()
                self.app.terminal.log("grid reset.")
                
            elif event.key == pygame.K_n:
                if event.mod & pygame.KMOD_ALT:
                    current_size = self.app.ca.genome.kernel.shape[0]
                    self.app.ca.genome = Genome.make_random(kernel_size=current_size)
                else:
                    self.app.ca.genome = Genome.make_random()
                self.app.ca.grid = self.app.ca.reset_grid()
                self.on_ca_changed()
                self.app.terminal.log("generated new random genome.")
                
            elif event.key == pygame.K_m:
                self.app.ca.genome = self.app.ca.genome.mutate()
                self.app.ca.grid = self.app.ca.reset_grid()
                self.on_ca_changed()
                self.app.terminal.log("genome mutated.")
                
            elif event.key == pygame.K_e:
                print("\n--- starting evolution mode ---")
                config_dir = "evolution_configs"
                os.makedirs(config_dir, exist_ok=True)
                
                # list available evolution configs
                files = [os.path.basename(f) for f in glob.glob(os.path.join(config_dir, "*.json"))]
                
                self.app.terminal.start_prompt(
                    prompt_text="enter evolution config filename (enter for default): ",
                    options=files,
                    callback=self._transition_to_evolution
                )
            
            elif event.key == pygame.K_g:
                self.show_genome_info = not self.show_genome_info
                self._layout_components()
                self.app.terminal.log(f"genome info panel {'opened' if self.show_genome_info else 'closed'}.")
                
            # global commands passed to app
            elif event.key == pygame.K_s:
                self.app.prompt_save_genome()
            elif event.key == pygame.K_l:
                self.app.prompt_load_genome()
            elif event.key == pygame.K_i:
                self.app.prompt_load_state()

    def update(self):
        if not self.paused:
            self.app.ca.step()
            self.live_stats.update(self.app.ca.grid)

    def draw(self, screen):
        self.sim_panel.draw(screen)
        
        if self.show_genome_info:
            self._draw_genome_info(screen)
            
            live_stats_y = self.sim_panel.y + self.sim_panel.pixel_h
            live_stats_h = self.app.terminal.rect.y - live_stats_y
            live_stats_w = int(self.app.screen_width * 0.75)
            
            self.live_stats.draw(screen, x=0, y=live_stats_y, w=live_stats_w, h=live_stats_h)
    
    def _draw_genome_info(self, screen):
        area_x = int(self.app.screen_width * 0.75)
        area_w = self.app.screen_width - area_x
        sim_h_space = self.app.screen_height - self.app.terminal.rect.height
        
        genome = self.app.ca.genome
        kernel = genome.kernel
        N = kernel.shape[0]
        
        # draw kernel
        max_draw_size = min(area_w - 40, sim_h_space // 2)
        k_cell = max(2, max_draw_size // max(N, 1))
        k_draw_w = N * k_cell
        
        # center it
        k_start_x = area_x + (area_w - k_draw_w) // 2
        k_start_y = 50
        
        screen.blit(self.title_font.render("kernel shape", True, (200, 200, 200)), (k_start_x, k_start_y - 35))
        
        for r in range(N):
            for c in range(N):
                if kernel[r, c] == 1:
                    rect = (k_start_x + c * k_cell, k_start_y + r * k_cell, k_cell, k_cell)
                    pygame.draw.rect(screen, (255, 255, 255), rect)
                    
        # outline box
        pygame.draw.rect(screen, (100, 100, 100), (k_start_x, k_start_y, k_draw_w, k_draw_w), 2)
        
        # draw rules table
        r_start_y = k_start_y + k_draw_w + 40
        screen.blit(self.title_font.render("rule table", True, (200, 200, 200)), (area_x + 20, r_start_y))
        
        birth_list = [i for i, val in enumerate(genome.rule_table[0]) if val == 1]
        survive_list = [i for i, val in enumerate(genome.rule_table[1]) if val == 1]

        def render_wrapped_text(title, num_list, x, y):
            screen.blit(self.info_font.render(title, True, (180, 180, 180)), (x, y))
            y += 25
            if not num_list:
                screen.blit(self.info_font.render("none", True, (150, 200, 255)), (x, y))
                return y + 35
                
            line = ""
            for num in num_list:
                test_line = line + str(num) + ", "
                # wrap text if need be
                if self.info_font.size(test_line)[0] < area_w - 10:
                    line = test_line
                else:
                    screen.blit(self.info_font.render(line.rstrip(", "), True, (150, 200, 255)), (x, y))
                    y += 25
                    line = str(num) + ", "
                    
            if line:
                screen.blit(self.info_font.render(line.rstrip(", "), True, (150, 200, 255)), (x, y))
                y += 25
                
            return y + 10

        y_offset = r_start_y + 40
        y_offset = render_wrapped_text("survive:", survive_list, area_x + 20, y_offset)
        render_wrapped_text("birth:", birth_list, area_x + 20, y_offset)
    
    def _transition_to_evolution(self, config_file):
        config_dir = "evolution_configs"
        config = {
            "num_children": 8,
            "grid_size": [130, 100],
            "kernel_mutation_expected_value": 1.0,
            "rule_mutation_expected_value": 0.5,
            "growth_threshold": 0.2,
            "mutation_rate_sparsity": 0.05,
            "fitness_function": "activity",
        }
        
        if config_file:
            if not config_file.endswith(".json"):
                config_file += ".json"
            filepath = os.path.join(config_dir, config_file)
            
            if os.path.exists(filepath):
                try:
                    with open(filepath, 'r') as f:
                        config.update(json.load(f))
                    self.app.terminal.log(f"loaded evolution config: {config_file}")
                except Exception as e:
                    self.app.terminal.log(f"error loading config, using default: {e}")
            else:
                self.app.terminal.log(f"config '{config_file}' not found. Using default.")
        else:
            self.app.terminal.log("using default evolution configuration.")

        self.app.scenes["EVO"] = EvolutionScene(self.app, config)
        self.app.change_scene("EVO")
