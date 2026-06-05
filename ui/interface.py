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
        self.states_dir = "grid_states"
    
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
        
        print("\n=== controls ===")
        print("[space]  - pause / resume")
        print("[right]  - step (when paused)")
        print("[r]      - reset grid")
        print("[n]      - new random genome")
        print("[alt+n]  - new random genome (keep kernel size)")
        print("[m]      - mutate genome")
        print("[s]      - save genome to .json")
        print("[l]      - load genome from .json")
        print("[i]      - initialize grid from .txt")
        print("[esc]    - exit")
        
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
                        
                        if event.mod & pygame.KMOD_ALT:
                            current_size = self.ca.genome.kernel.shape[0]
                            self.ca.genome = Genome.make_random(kernel_size=current_size)
                        else:
                            self.ca.genome = Genome.make_random()
                            current_size = self.ca.genome.kernel.shape[0]
                            
                        current_sparsity = self.ca.genome.sparsity
                        pygame.display.set_caption(f"kernel_size: {current_size}\tsparsity: {current_sparsity}")
                        self.ca.grid = self.ca.reset_grid()
                        
                    elif event.key == pygame.K_m:
                        self.ca.genome = self.ca.genome.mutate()
                        current_size = self.ca.genome.kernel.shape[0]
                        current_sparsity = self.ca.genome.sparsity
                        pygame.display.set_caption(f"kernel_size: {current_size}\tsparsity: {current_sparsity}")
                        self.ca.grid = self.ca.reset_grid()
                        
                    elif event.key == pygame.K_s:
                        self.save_genome()
                        
                    elif event.key == pygame.K_l:
                        self.load_genome()
                    
                    elif event.key == pygame.K_i:
                        print("--- load initial state ---")
                        os.makedirs(self.states_dir, exist_ok=True)
                        filename = input(f"enter state filename from '{self.states_dir}': ").strip()
                        
                        if filename:
                            if not filename.endswith(".txt"):
                                filename += ".txt"
                            
                            filepath = os.path.join(self.states_dir, filename)
                            if not os.path.exists(filepath):
                                filepath = filename
                                
                            if os.path.exists(filepath):
                                try:
                                    self.ca.load_custom_grid(filepath)
                                    print(f"loaded initial state from {filepath}")
                                except Exception as e:
                                    print(f"failed to load state: {e}")
                            else:
                                print(f"file not found: {filepath}")
                        
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
