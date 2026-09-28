class NQueensEncoder:
    def __init__(self, n: int):
        self.n = n
        self.next_var = n * n + 1
        
    def var(self, r: int, c: int) -> int:
        return r * self.n + c + 1

    def encode_alo(self, lits):
        return [lits]

    def encode_amo_binomial(self, lits):
        clauses = []
        for i in range(len(lits)):
            for j in range(i + 1, len(lits)):
                clauses.append([-lits[i], -lits[j]])
        return clauses

    def generate_clauses(self):
        clauses = []
        n = self.n

        for r in range(n):
            lits = [self.var(r, c) for c in range(n)]
            clauses.extend(self.encode_alo(lits))
            clauses.extend(self.encode_amo_binomial(lits))
            
        for c in range(n):
            lits = [self.var(r, c) for r in range(n)]
            clauses.extend(self.encode_amo_binomial(lits))

        for d in range(-n + 1, n):
            lits = [self.var(r, r - d) for r in range(n) if 0 <= r - d < n]
            if len(lits) > 1:
                clauses.extend(self.encode_amo_binomial(lits))

        for d in range(2 * n - 1):
            lits = [self.var(r, d - r) for r in range(n) if 0 <= d - r < n]
            if len(lits) > 1:
                clauses.extend(self.encode_amo_binomial(lits))
                
        return clauses, self.next_var - 1
