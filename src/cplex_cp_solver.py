import os
import glob
import time
from docplex.cp.model import CpoModel

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

def _engine_available() -> bool:
    try:
        exe = _find_cpoptimizer()
        if exe:
            os.environ["PATH"] = os.path.dirname(exe) + os.pathsep + os.environ.get("PATH", "")
            model = CpoModel()
            ctx = model.get_cpo_context()
            ctx.solver.local.execfile = exe
            from docplex.cp.solver.solver_local import CpoSolverLocal
            CpoSolverLocal(None, ctx)
            return True

        from docplex.cp.solver.solver_local import CpoSolverLocal
        ctx = CpoModel().get_cpo_context()
        CpoSolverLocal(None, ctx)
        return True
    except Exception:
        return False

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

    def solve(self, time_limit_sec: float = 100.0):
        exe = _find_cpoptimizer()
        if exe:
            os.environ["PATH"] = os.path.dirname(exe) + os.pathsep + os.environ.get("PATH", "")
            ctx = self.model.get_cpo_context()
            ctx.solver.local.execfile = exe
        elif not _engine_available():
            raise RuntimeError("MISSING_ENGINE")

        start_time = time.time()
        solution = self.model.solve(TimeLimit=time_limit_sec, LogVerbosity="Quiet")
        end_time = time.time()

        runtime = end_time - start_time
        is_sat = bool(solution) and solution.is_solution()

        if is_sat:
            self.solution = [solution[self.q[i]] for i in range(self.n)]
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
    solver = CplexCPSolver(8)
    try:
        is_sat, runtime = solver.solve()
        print(f"CPLEX CP SAT={is_sat}, Runtime={runtime:.6f}, Valid={solver.verify_solution()}")
    except Exception as e:
        print(f"Lỗi: {e}")
