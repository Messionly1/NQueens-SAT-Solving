import time
from docplex.cp.model import CpoModel

def _engine_available() -> bool:
    try:
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

        # Variables: q[i] is the column of the queen in row i
        self.q = self.model.integer_var_list(n, 0, n - 1, "q")

        # Constraints:
        self.model.add(self.model.all_diff(self.q))
        self.model.add(self.model.all_diff([self.q[i] - i for i in range(n)]))
        self.model.add(self.model.all_diff([self.q[i] + i for i in range(n)]))

    def solve(self, time_limit_sec: float = 100.0):
        if not _engine_available():
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
