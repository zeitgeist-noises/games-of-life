import pygame
import numpy as np
from engine.ca import CellularAutomaton
from engine.genome import Genome
import os
from datetime import datetime


class SimulationWindow:
    def __init__(self, ca: CellularAutomaton, cell_size: int = 4):
        self.ca = ca
        self.cell_size = cell_size

        self.screen_width = ca.width * cell_size
        self.screen_height = ca.height * cell_size

        pygame.init()
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Generalized Game of Life")
        self.clock = pygame.time.Clock()
        
        self.grid_surface = pygame.Surface((ca.width, ca.height))
        
        self.save_dir = "saved_genomes"
    
    def draw(self):
        rgb_grid = np.zeros((self.ca.width, self.ca.height, 3), dtype=np.uint8)
        rgb_grid[self.ca.grid.T == 1] = [255, 255, 255]
        
        pygame.surfarray.blit_array(self.grid_surface, rgb_grid)
        
        scaled_surface = pygame.transform.scale(self.grid_surface, (self.screen_width, self.screen_height))
        self.screen.blit(scaled_surface, (0, 0))
        pygame.display.flip()
    
    def run(self, fps: int = 30):
        running = True
        paused = False
        
        print("\n=== Controls ===")
        print("[space]  - Pause / Resume")
        print("[right]  - Step Sim (when paused)")
        print("[r]      - Reinitialize / Reset Grid")
        print("[n]      - New Genome")
        print("[s]      - Save Genome to JSON")
        print("[l]      - Load Genome from JSON")
        print("[esc]    - Exit")
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        paused = not paused
                    elif event.key == pygame.K_RIGHT and paused:
                        self.ca.step()
                        self.draw()
                    elif event.key == pygame.K_r:
                        self.ca.grid = self.ca.reset_grid()
                    elif event.key == pygame.K_n:
                        self.ca.genome = Genome.make_random()
                        self.ca.grid = self.ca.reset_grid()
                    elif event.key == pygame.K_s:
                        self.save_genome()
                    elif event.key == pygame.K_l:
                        self.load_genome()
                    elif event.key == pygame.K_ESCAPE:
                        running = False
            
            if not paused:
                self.ca.step()
            
            self.draw()
            self.clock.tick(fps)
        
        pygame.quit()
    
    def save_genome(self):
        print("\n--- Save Genome ---")
        filename_input = input("Enter filename (leave empty for timestamp): ").strip()
        
        if not filename_input:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"genome_{timestamp}.json"
        else:
            filename = filename_input
            if not filename.endswith(".json"):
                filename += ".json"
        
        filepath = os.path.join(self.save_dir, filename)
        try:
            self.ca.genome.save_to_file(filepath)
        except Exception as e:
            print(f"Failed to save genome: {e}")
        
    def load_genome(self):
        print("\n--- Load Genome ---")
        
        filename = input("Enter filename or full path: ").strip()
        
        if not filename:
            print("Load cancelled. Empty input.")
            return
        
        if not filename.endswith(".json"):
            filename += ".json"
        
        filepath = os.path.join(self.save_dir, filename)
        
        if not os.path.exists(filepath):
            filepath = filename
        
        if os.path.exists(filepath):
            print(f"Loading: {filepath}")
            try:
                self.ca.genome = Genome.load_from_file(filepath)
                self.ca.grid = self.ca.reset_grid()
            except Exception as e:
                print(f"Failed to load genome:  {e}")
        else:
            print(f"Error: File not found: '{filepath}'")
