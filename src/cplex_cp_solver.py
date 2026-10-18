import os
import glob
import time
from docplex.cp.model import CpoModel
from verify import is_valid_placement

def _find_cpoptimizer() -> str:
    roots = [
        r"C:\Program Files\IBM\ILOG",
        r"C:\Program Files (x86)\IBM\ILOG",
        os.environ.get("CPLEX_STUDIO_DIR", ""),
    ]
    for root in roots:
        if not root:
            continue
        pattern = os.path.join(root, "CPLEX_Studio*", "cpoptimizer", "bin", "*", "cpoptimizer.exe")
        hits = glob.glob(pattern)
        if hits:
            return hits[0]
    return ""

class CplexCPSolver:
    def __init__(self, n: int):
        self.n = n
        self.solution = None
        self.timed_out = False
        self.model = CpoModel(name="NQueens_CP")

        self.q = self.model.integer_var_list(n, 0, n - 1, "q")
        self.model.add(self.model.all_diff(self.q))
        self.model.add(self.model.all_diff([self.q[i] - i for i in range(n)]))
        self.model.add(self.model.all_diff([self.q[i] + i for i in range(n)]))

    def solve(self, time_limit_sec: float = 100.0, first_solution: bool = False):
        exe = _find_cpoptimizer()
        if not exe:
            raise RuntimeError("MISSING_ENGINE")

        exe_dir = os.path.dirname(exe)
        if exe_dir not in os.environ.get("PATH", "").split(os.pathsep):
            cplex_bin = exe_dir.replace("cpoptimizer", "cplex")
            os.environ["PATH"] = exe_dir + os.pathsep + cplex_bin + os.pathsep + os.environ.get("PATH", "")

        start_time = time.perf_counter()
        solution = self.model.solve(TimeLimit=time_limit_sec, Workers=1, LogVerbosity="Quiet", execfile=exe)
        end_time = time.perf_counter()

        runtime = end_time - start_time
        is_sat = bool(solution) and solution.is_solution()
        self.engine_time = solution.get_solve_time() if solution else None

        if is_sat:
            self.solution = [solution[self.q[i]] for i in range(self.n)]
        else:
            self.solution = None

        self.timed_out = (not is_sat) and runtime >= time_limit_sec

        return is_sat, runtime

    def get_model(self):
        return self.solution

    def verify_solution(self) -> bool:
        return is_valid_placement(self.solution, self.n)

if __name__ == "__main__":
    solver = CplexCPSolver(8)
    try:
        is_sat, runtime = solver.solve()
        print(f"CPLEX CP SAT={is_sat}, Runtime={runtime:.6f}, Valid={solver.verify_solution()}")
    except Exception as e:
        print(f"Lỗi: {e}")
