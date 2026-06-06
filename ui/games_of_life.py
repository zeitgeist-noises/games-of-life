import pygame
import os
import glob
from datetime import datetime
from engine.ca import CellularAutomaton
from engine.genome import Genome
from ui.components.terminal import Terminal
from ui.scenes.main_scene import MainScene

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800

MAIN_SIM_WIDTH = 200
MAIN_SIM_HEIGHT = 120

TERMINAL_HEIGHT = 200


class GamesOfLife:
    def __init__(self):
        pygame.init()
        self.screen_width = SCREEN_HEIGHT
        self.screen_height = SCREEN_HEIGHT
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Games of Life")
        self.clock = pygame.time.Clock()
        self.running = True

        # global directories
        self.save_dir = "saved_genomes"
        self.states_dir = "grid_states"
        os.makedirs(self.save_dir, exist_ok=True)
        os.makedirs(self.states_dir, exist_ok=True)

        # initialize saved_genomes
        initial_genome = Genome.make_conway()
        self.ca = CellularAutomaton(initial_genome, grid_size=(MAIN_SIM_WIDTH, MAIN_SIM_HEIGHT))

        # ui Components
        self.terminal = Terminal(x=0, y=self.screen_height - TERMINAL_HEIGHT, w=self.screen_width, h=TERMINAL_HEIGHT)

        # Scenes
        self.scenes = {
            "MAIN": MainScene(self)
        }
        self.current_scene = self.scenes["MAIN"]
    
    def change_scene(self, scene_name):
        self.current_scene = self.scenes[scene_name]
        self.current_scene.on_enter()
    
    def run(self):
        self.current_scene.on_enter()
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                # terminal ingests event
                consumed_by_terminal = self.terminal.handle_event(event)
                
                if not consumed_by_terminal:
                    # terminal passes event to current scene
                    self.current_scene.handle_event(event)

            self.current_scene.update()
            
            # render
            self.screen.fill((20, 20, 20))  # background color
            self.current_scene.draw(self.screen)
            self.terminal.draw(self.screen)
            
            pygame.display.flip()
            self.clock.tick(30)
            
        pygame.quit()
        
    # ==========================================
    # global commands
    # ==========================================
    
    def prompt_save_genome(self):
        self.terminal.start_prompt(
            prompt_text="save genome as (leave empty for timestamp): ",
            options=[],
            callback=self._do_save_genome
        )

    def _do_save_genome(self, filename):
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"genome_{timestamp}"
        if not filename.endswith(".json"):
            filename += ".json"
            
        filepath = os.path.join(self.save_dir, filename)
        try:
            self.ca.genome.save_to_file(filepath)
            self.terminal.log(f"saved successfully: {filename}")
        except Exception as e:
            self.terminal.log(f"error saving: {e}")

    def prompt_load_genome(self):
        # fetch options for autocomplete
        files = [os.path.basename(f) for f in glob.glob(os.path.join(self.save_dir, "*.json"))]
        self.terminal.start_prompt(
            prompt_text="load genome: ",
            options=files,
            callback=self._do_load_genome
        )

    def _do_load_genome(self, filename):
        if not filename:
            self.terminal.log("load cancelled.")
            return
        if not filename.endswith(".json"):
            filename += ".json"
            
        filepath = os.path.join(self.save_dir, filename)
        if os.path.exists(filepath):
            try:
                self.ca.genome = Genome.load_from_file(filepath)
                self.ca.grid = self.ca.reset_grid()
                self.terminal.log(f"loaded genome: {filename}")
                self.current_scene.on_ca_changed()
            except Exception as e:
                self.terminal.log(f"error loading: {e}")
        else:
            self.terminal.log(f"file not found: {filename}")

    def prompt_load_state(self):
        files = [os.path.basename(f) for f in glob.glob(os.path.join(self.states_dir, "*.txt"))]
        self.terminal.start_prompt(
            prompt_text="load grid state (.txt): ",
            options=files,
            callback=self._do_load_state
        )

    def _do_load_state(self, filename):
        if not filename:
            self.terminal.log("load cancelled.")
            return
        if not filename.endswith(".txt"):
            filename += ".txt"
            
        filepath = os.path.join(self.states_dir, filename)
        if os.path.exists(filepath):
            try:
                self.ca.load_custom_grid(filepath)
                self.terminal.log(f"loaded initial state: {filename}")
            except Exception as e:
                self.terminal.log(f"error loading state: {e}")
        else:
            self.terminal.log(f"file not found: {filename}")
