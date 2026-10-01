import time
from ortools.sat.python import cp_model

class CPQueensSolver:
    def __init__(self, n: int):
        self.n = n
        self.solution = None
        self.timed_out = False
        self.model = cp_model.CpModel()
        
        self.queens = [self.model.NewIntVar(0, n - 1, f'q_{i}') for i in range(n)]
        
        self.model.AddAllDifferent(self.queens)
        self.model.AddAllDifferent([self.queens[i] - i for i in range(n)])
        self.model.AddAllDifferent([self.queens[i] + i for i in range(n)])

    def solve(self, time_limit_sec: float = 100.0):
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = time_limit_sec
        solver.parameters.num_search_workers = 1
        
        start_time = time.time()
        status = solver.Solve(self.model)
        end_time = time.time()
        
        runtime = end_time - start_time
        is_sat = (status == cp_model.OPTIMAL or status == cp_model.FEASIBLE)
        
        self.solution = [solver.Value(self.queens[i]) for i in range(self.n)] if is_sat else None
        self.timed_out = (status == cp_model.UNKNOWN)
        
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
