import sys
import time
from ortools.sat.python import cp_model

sys.stdout.reconfigure(encoding='utf-8')

class CPQueensSolver:
    def __init__(self, n: int):
        self.n = n
        self.model = cp_model.CpModel()
        
        self.queens = [self.model.NewIntVar(0, n - 1, f'q_{i}') for i in range(n)]
        
        self.model.AddAllDifferent(self.queens)
        self.model.AddAllDifferent([self.queens[i] - i for i in range(n)])
        self.model.AddAllDifferent([self.queens[i] + i for i in range(n)])

    def solve(self, time_limit_sec: float = 100.0):
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = time_limit_sec
        
        start_time = time.time()
        status = solver.Solve(self.model)
        end_time = time.time()
        
        runtime = end_time - start_time
        is_sat = (status == cp_model.OPTIMAL or status == cp_model.FEASIBLE)
        
        return is_sat, runtime

if __name__ == "__main__":
    n = 15
    print(f"--- Đang giải N-Queens bằng OR-Tools CP-SAT (N={n}) ---")
    cp_solver = CPQueensSolver(n)
    is_sat, runtime = cp_solver.solve()
    print(f"Kết quả: SAT={is_sat} | Thời gian: {runtime:.6f} giây")
