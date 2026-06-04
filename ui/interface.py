import pygame
import numpy as np
from engine.ca import CellularAutomaton
from engine.genome import Genome


class SimulationWindow:
    def __init__(self, ca: CellularAutomaton, cell_size: int = 4):
        self.ca = ca
        self.cell_size = cell_size

        self.screen_width = ca.width * cell_size
        self.screen_height = ca.height * cell_size

        pygame.init()
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Caption here")
        self.clock = pygame.time.Clock()
        
        self.grid_surface = pygame.Surface((ca.width, ca.height))
    
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
        print("[Space]  - Pause / Resume")
        print("[Right]  - Step Sim (when paused)")
        print("[R]      - Reinitialize / Reset Grid")
        print("[N]      - New Genome")
        print("[Escape] - Exit")
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE:
                        paused = not paused
                    elif event.key == pygame.K_r:
                        self.ca.grid = self.ca.reset_grid()
                    elif event.key == pygame.K_RIGHT and paused:
                        self.ca.step()
                        self.draw()
                    elif event.key == pygame.K_n:
                        self.ca.genome = Genome.make_random()
                        self.ca.grid = self.ca.reset_grid()
            
            if not paused:
                self.ca.step()
            
            self.draw()
            self.clock.tick(fps)
        
        pygame.quit()
