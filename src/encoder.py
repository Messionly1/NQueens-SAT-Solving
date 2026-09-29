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
        S = self.get_new_vars(len(lits) - 1)
        
        clauses.append([-lits[0], S[0]])
        for i in range(1, len(lits) - 1):
            clauses.append([-lits[i], S[i]])
            clauses.append([-S[i-1], S[i]])
            clauses.append([-lits[i], -S[i-1]])
        clauses.append([-lits[-1], -S[-1]])
        return clauses

    def encode_amo_binary(self, lits):
        if len(lits) <= 1:
            return []
        m = math.ceil(math.log2(len(lits)))
        V = self.get_new_vars(m)
        clauses = []
        for i, lit in enumerate(lits):
            b = format(i, f'0{m}b')
            for j in range(m):
                if b[j] == '1':
                    clauses.append([-lit, V[j]])
                else:
                    clauses.append([-lit, -V[j]])
        return clauses

    def encode_amo_commander(self, lits):
        if len(lits) <= 4:
            return self.encode_amo_binomial(lits)
        
        group_size = math.ceil(math.sqrt(len(lits)))
        groups = [lits[i:i + group_size] for i in range(0, len(lits), group_size)]
        commanders = self.get_new_vars(len(groups))
        
        clauses = []
        clauses.extend(self.encode_amo_binomial(commanders))
        
        for i, group in enumerate(groups):
            c = commanders[i]
            clauses.append([-c] + group)
            clauses.extend(self.encode_amo_binomial(group))
            for lit in group:
                clauses.append([-lit, c])
                
        return clauses

    def encode_amo_product(self, lits):
        if len(lits) <= 4:
            return self.encode_amo_binomial(lits)
        
        p = math.ceil(math.sqrt(len(lits)))
        q = math.ceil(len(lits) / p)
        
        R = self.get_new_vars(p)
        C = self.get_new_vars(q)
        
        clauses = []
        clauses.extend(self.encode_amo_binomial(R))
        clauses.extend(self.encode_amo_binomial(C))
        
        for i, lit in enumerate(lits):
            r_idx = i // q
            c_idx = i % q
            clauses.append([-lit, R[r_idx]])
            clauses.append([-lit, C[c_idx]])
            
        return clauses

    def verify_solution(self, model, n: int) -> bool:
        if not model:
            return False
        true_vars = {lit for lit in model if lit > 0}
        queens = [((v - 1) // n, (v - 1) % n) for v in true_vars if 1 <= v <= n * n]

        if len(queens) != n:
            return False
        rows = [r for r, _ in queens]
        cols = [c for _, c in queens]
        diag_main = [r - c for r, c in queens]
        diag_anti = [r + c for r, c in queens]

        return (len(set(rows)) == n and len(set(cols)) == n
                and len(set(diag_main)) == n and len(set(diag_anti)) == n)

    def generate_clauses(self, enc_type="binomial"):
        clauses = []
        n = self.n
        
        amo_func = {
            "binomial": self.encode_amo_binomial,
            "sequential": self.encode_amo_sequential,
            "binary": self.encode_amo_binary,
            "commander": self.encode_amo_commander,
            "product": self.encode_amo_product
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
