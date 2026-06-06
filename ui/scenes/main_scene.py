import pygame
from ui.scenes.base_scene import Scene
from ui.components.sim_panel import SimulationPanel
from engine.genome import Genome


class MainScene(Scene):
    def __init__(self, app):
        super().__init__(app)
        self.paused = False
        
        # create centered sim panel
        sim_h_space = self.app.screen_height - self.app.terminal.rect.height
        
        self.sim_panel = SimulationPanel(
            x=(self.app.screen_width - (self.app.ca.width * 4)) // 2,
            y=(sim_h_space - (self.app.ca.height * 4)) // 2,
            ca=self.app.ca,
            cell_size=4
        )
        
        self.commands_info = [
            "[spc]   pause/resume",
            "[->]    step (if paused)",
            "[r]     reset grid",
            "[n]     new random genome",
            "[alt+n] new genome (keep size)",
            "[m]     mutate genome",
            "[s]     save to .json",
            "[l]     load from .json",
            "[i]     init from .txt"
        ]

    def on_enter(self):
        # tell teminal to show options
        self.app.terminal.set_commands_info(self.commands_info)
        self._update_title()

    def on_ca_changed(self):
        self.sim_panel.update_ca(self.app.ca)
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

    def draw(self, screen):
        self.sim_panel.draw(screen)
