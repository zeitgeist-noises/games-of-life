import os
import json
import numpy as np

MAX_KERNEL_SIZE = 20
MAX_SPARSITY = 0.2


class Genome:
    def __init__(self, kernel: np.ndarray, rule_table: np.ndarray, sparsity: float):
        self.kernel = np.array(kernel, dtype=np.uint8)
        self.rule_table = np.array(rule_table, dtype=np.uint8)
        self.sparsity = sparsity

    def save_to_file(self, filepath: str):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        data = {
            "kernel": self.kernel.tolist(),
            "rule_table": self.rule_table.tolist(),
            "sparsity": float(self.sparsity)
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"Genome saved successfully to:  {filepath}")
    
    @classmethod
    def load_from_file(cls, filepath: str):
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"No genome file found at {filepath}")
        
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        return cls(
            kernel=np.array(data["kernel"], dtype=np.uint8),
            rule_table=np.array(data["rule_table"], dtype=np.uint8),
            sparsity=float(data["sparsity"])
        )

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
    def make_random(cls, kernel_size: int = None, sparsity: float = None):
        if kernel_size is None:
            kernel_size = np.random.randint(2, MAX_KERNEL_SIZE+1)
        
        if sparsity is None:
            sparsity = MAX_SPARSITY * np.random.random()
            
        kernel = np.random.choice([0, 1], size=(kernel_size, kernel_size), p=[0.4, 0.6]).astype(np.uint8)
        
        kernel[kernel_size // 2, kernel_size // 2] = 0
        
        S = int(np.sum(kernel))
        rule_table = np.random.choice([0, 1], size=(2, S+1), p=[0.75, 0.25]).astype(np.uint8)
        
        return cls(kernel, rule_table, sparsity)
