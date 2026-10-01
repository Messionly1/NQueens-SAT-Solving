import time
from docplex.mp.model import Model

class CplexMIPSolver:
    def __init__(self, n: int):
        self.n = n
        self.solution = None
        self.timed_out = False
        self.model = Model(name="NQueens_MIP")

        # Variables: x[i, j] = 1 if queen at row i, col j
        self.x = self.model.binary_var_matrix(keys1=range(n), keys2=range(n), name="q")

        # Constraints:
        # 1. Exactly one queen per row
        for i in range(n):
            self.model.add_constraint(self.model.sum(self.x[i, j] for j in range(n)) == 1)

        # 2. Exactly one queen per column
        for j in range(n):
            self.model.add_constraint(self.model.sum(self.x[i, j] for i in range(n)) == 1)

        # 3. At most one queen per major diagonal (row - col = const)
        for k in range(-n + 1, n):
            cells = [(i, i - k) for i in range(max(0, k), min(n, n + k))]
            if len(cells) > 1:
                self.model.add_constraint(
                    self.model.sum(self.x[i, j] for i, j in cells) <= 1)

        # 4. At most one queen per minor diagonal (row + col = const)
        for k in range(2 * n - 1):
            cells = [(i, k - i) for i in range(max(0, k - n + 1), min(n, k + 1))]
            if len(cells) > 1:
                self.model.add_constraint(
                    self.model.sum(self.x[i, j] for i, j in cells) <= 1)

    def solve(self, time_limit_sec: float = 100.0):
        self.model.parameters.timelimit = time_limit_sec
        self.model.parameters.threads = 1
        self.model.set_log_output(None)

        start_time = time.time()
        solution = self.model.solve(log_output=False)
        end_time = time.time()

        runtime = end_time - start_time
        is_sat = solution is not None

        if is_sat:
            self.solution = [
                next(j for j in range(self.n) if self.x[i, j].solution_value > 0.5)
                for i in range(self.n)
            ]
        else:
            self.solution = None

        self.timed_out = (not is_sat) and runtime >= time_limit_sec

        return is_sat, runtime

    def get_model(self):
        return self.solution

    def verify_solution(self) -> bool:
        q = self.solution
        if not q or len(q) != self.n:
            return False
        return (len(set(q)) == self.n
                and len({q[i] - i for i in range(self.n)}) == self.n
                and len({q[i] + i for i in range(self.n)}) == self.n)

if __name__ == "__main__":
    solver = CplexMIPSolver(8)
    is_sat, runtime = solver.solve()
    print(f"CPLEX MIP SAT={is_sat}, Runtime={runtime:.6f}, Valid={solver.verify_solution()}")
