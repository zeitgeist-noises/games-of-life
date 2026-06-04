import numpy as np
from scipy.ndimage import convolve
from engine.genome import Genome


class CellularAutomaton:
    def __init__(self, genome: Genome, grid_size: tuple[int, int]):
        self.genome = genome
        self.width, self.height = grid_size
        self.grid = self.reset_grid()

    def reset_grid(self) -> np.ndarray:
        return (np.random.random((self.height, self.width)) < self.genome.sparsity).astype(np.uint8)
    
    def step(self):
        num_neighbors = convolve(self.grid, self.genome.kernel, mode='wrap')
        self.grid = self.genome.rule_table[self.grid, num_neighbors]
