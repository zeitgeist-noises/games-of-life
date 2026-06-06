import pygame
import numpy as np


class SimulationPanel:
    def __init__(self, x, y, ca, cell_size=4):
        self.x = x
        self.y = y
        self.ca = ca
        self.cell_size = cell_size
        
        self.pixel_w = ca.width * cell_size
        self.pixel_h = ca.height * cell_size
        
        self.surface = pygame.Surface((self.pixel_w, self.pixel_h))
        self.grid_surface = pygame.Surface((ca.width, ca.height))

    def update_ca(self, new_ca):
        self.ca = new_ca

    def draw(self, screen):
        # convert ca state to rgb
        rgb_grid = np.zeros((self.ca.width, self.ca.height, 3), dtype=np.uint8)
        rgb_grid[self.ca.grid.T == 1] = [255, 255, 255]
        
        # pixel transfer
        pygame.surfarray.blit_array(self.grid_surface, rgb_grid)
        
        # scale to match cell size
        pygame.transform.scale(self.grid_surface, (self.pixel_w, self.pixel_h), self.surface)
        
        # blit to main screen
        screen.blit(self.surface, (self.x, self.y))
        
        # border
        pygame.draw.rect(screen, (50, 50, 50), (self.x, self.y, self.pixel_w, self.pixel_h), 1)
