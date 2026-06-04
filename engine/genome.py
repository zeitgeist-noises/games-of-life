import numpy as np

MAX_KERNEL_SIZE = 100


class Genome:
    def __init__(self, kernel: np.ndarray, rule_table: np.ndarray, sparsity: float):
        self.kernel = np.array(kernel, dtype=np.uint8)
        self.rule_table = np.array(rule_table, dtype=np.uint8)
        self.sparsity = sparsity

    @classmethod
    def make_conway(cls):
        kernel = np.array([
            [1, 1, 1],
            [1, 0, 1],
            [1, 1, 1]
        ], dtype=np.uint8)
        
        rule_table = np.zeros((2, 9), dtype=np.uint8)
        rule_table[0, 3] = 1
        rule_table[1, 2] = 1
        rule_table[1, 3] = 1
        
        return cls(kernel, rule_table, sparsity=0.2)
    
    @classmethod
    def make_random(cls, kernel_size: int = np.random.randint(2, MAX_KERNEL_SIZE+1), sparsity: float = np.random.random()):
        kernel = np.random.choice([0, 1], size=(kernel_size, kernel_size), p=[0.4, 0.6]).astype(np.uint8)
        
        kernel[kernel_size // 2, kernel_size // 2] = 0
        
        S = int(np.sum(kernel))
        rule_table = np.random.choice([0, 1], size=(2, S+1), p=[0.75, 0.25]).astype(np.uint8)
        
        return cls(kernel, rule_table, sparsity)
