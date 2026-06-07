import os
import json
import numpy as np

MAX_KERNEL_SIZE = 6
MAX_SPARSITY = 0.2


class Genome:
    def __init__(self, kernel: np.ndarray, rule_table: np.ndarray, sparsity: float):
        self.kernel = np.array(kernel, dtype=np.uint8)
        self.rule_table = np.array(rule_table, dtype=np.uint8)
        self.sparsity = sparsity
    
    def mutate(self, config: dict = None):
        # COMMENT_OUT_LATER
        if config is None:
            config = {}
        
        # obtain new kernel size
        N = self.kernel.shape[0]
        growth_pressure = np.sum(self.kernel) - np.sum(self.kernel[1:-1, 1:-1])
        perimeter_size = 4 * (N - 1)
        growth_threshold = config.get("growth_threshold", 0.2)
        
        if growth_pressure > growth_threshold * perimeter_size:
            new_kernel = np.zeros((N+2, N+2), dtype=np.uint8)
            new_kernel[1:-1, 1:-1] = self.kernel.copy()
        else:
            new_kernel = self.kernel.copy()
        
        # obtain new
        
        # find mutation counts with poisson distributions
        N = new_kernel.shape[0]
        
        kernel_mut_ev = config.get("kernel_mutation_expected_value", 1.0)
        rule_mut_ev = config.get("rule_mutation_expected_value", 0.5)
        
        num_mutations_kernel = 0
        num_mutations_rule = 0
        
        # ensure they aren't both 0'
        while num_mutations_kernel == 0 and num_mutations_rule == 0:
            num_mutations_kernel = np.random.poisson(kernel_mut_ev)
            num_mutations_rule = np.random.poisson(rule_mut_ev)
        
        num_mutations_kernel = min(num_mutations_kernel, N * N)
        
        # mutate kernel
        if num_mutations_kernel > 0:
            flat_indices = np.random.choice(N * N, size=num_mutations_kernel, replace=False)
            rows, cols = np.unravel_index(flat_indices, (N, N))
            new_kernel[rows, cols] = 1 - new_kernel[rows, cols]
        
        new_kernel[N // 2, N // 2] = 0
        
        # prune size if nothing in outer ring
        growth_pressure = np.sum(new_kernel) - np.sum(new_kernel[1:-1, 1:-1])
        if growth_pressure == 0:
            new_kernel = new_kernel[1:-1, 1:-1]
        
        # determine new rule_table size
        new_rule = self.rule_table.copy()
        S_new = int(np.sum(new_kernel))
        S_old = self.rule_table.shape[1] - 1
        
        if S_new > S_old:
            padding = np.zeros((2, S_new - S_old), dtype=np.uint8)
            new_rule = np.hstack((new_rule, padding))
        elif S_new < S_old:
            new_rule = new_rule[:, :S_new + 1]
        
        # mutate rules
        N = new_rule.shape[1]
        
        num_mutations_rule = np.random.poisson(rule_mut_ev)
        num_mutations_rule = min(num_mutations_rule, N)
        
        if num_mutations_rule > 0:
            flat_indices = np.random.choice(2 * N, size=num_mutations_rule, replace=False)
            rows, cols = np.unravel_index(flat_indices, (2, N))
            new_rule[rows, cols] = 1 - new_rule[rows, cols]
        
        # mutate sparsity
        new_sparsity = self.sparsity
        delta = (np.random.random() - 0.5) * config.get("mutation_rate_sparsity", 0.05)
        new_sparsity = max(self.sparsity + delta, 0.001)
        
        return self.__class__(new_kernel, new_rule, new_sparsity)

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
