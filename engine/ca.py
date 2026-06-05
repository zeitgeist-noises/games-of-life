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

    def load_custom_grid(self, filepath: str):
        with open(filepath, 'r') as f:
            lines = f.readlines()
        
        parsed_shape = []
        for line in lines:
            row = []
            for char in line.strip():
                if char == 'O':
                    row.append(1)
                else:
                    row.append(0)
            if row:
                parsed_shape.append(row)
        
        custom_state = np.array(parsed_shape, dtype=np.uint8)
        ch, cw = custom_state.shape
        
        new_grid = np.zeros((self.height, self.width), dtype=np.uint8)
        
        start_y = max(0, (self.height - ch) // 2)
        start_x = max(0, (self.width - cw) // 2)
        end_y = min(self.height, start_y + ch)
        end_x = min(self.width, start_x + cw)
        slice_y = end_y - start_y
        slice_x = end_x - start_x
        
        new_grid[start_y:end_y, start_x:end_x] = custom_state[:slice_y, :slice_x]
        self.grid = new_grid
