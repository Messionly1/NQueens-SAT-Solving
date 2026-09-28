import math

class NQueensEncoder:
    def __init__(self, n: int):
        self.n = n
        self.next_var = n * n + 1
        
    def var(self, r: int, c: int) -> int:
        return r * self.n + c + 1
        
    def get_new_vars(self, count: int):
        start = self.next_var
        self.next_var += count
        return list(range(start, start + count))

    def encode_alo(self, lits):
        return [lits]

    def encode_amo_binomial(self, lits):
        clauses = []
        for i in range(len(lits)):
            for j in range(i + 1, len(lits)):
                clauses.append([-lits[i], -lits[j]])
        return clauses

    def encode_amo_sequential(self, lits):
        if len(lits) <= 1:
            return []
        clauses = []
        # Cần k - 1 biến phụ
        S = self.get_new_vars(len(lits) - 1)
        
        clauses.append([-lits[0], S[0]])
        for i in range(1, len(lits) - 1):
            clauses.append([-lits[i], S[i]])
            clauses.append([-S[i-1], S[i]])
            clauses.append([-lits[i], -S[i-1]])
        clauses.append([-lits[-1], -S[-1]])
        return clauses

    def generate_clauses(self, enc_type="binomial"):
        clauses = []
        n = self.n
        
        amo_func = {
            "binomial": self.encode_amo_binomial,
            "sequential": self.encode_amo_sequential
        }[enc_type]

        for r in range(n):
            lits = [self.var(r, c) for c in range(n)]
            clauses.extend(self.encode_alo(lits))
            clauses.extend(amo_func(lits))
            
        for c in range(n):
            lits = [self.var(r, c) for r in range(n)]
            clauses.extend(amo_func(lits))
            
        for d in range(-n + 1, n):
            lits = [self.var(r, r - d) for r in range(n) if 0 <= r - d < n]
            if len(lits) > 1:
                clauses.extend(amo_func(lits))
                
        for d in range(2 * n - 1):
            lits = [self.var(r, d - r) for r in range(n) if 0 <= d - r < n]
            if len(lits) > 1:
                clauses.extend(amo_func(lits))
                
        return clauses, self.next_var - 1
