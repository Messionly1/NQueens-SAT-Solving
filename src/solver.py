import time
from pysat.solvers import Solver

class SATSolverWrapper:
    def __init__(self, clauses: list):
        self.clauses = clauses
        self.model = None

    def solve(self, solver_name: str = 'glucose3'):
        solver = Solver(name=solver_name)
        for clause in self.clauses:
            solver.add_clause(clause)

        start_time = time.time()
        is_sat = solver.solve()
        end_time = time.time()

        runtime = end_time - start_time
        self.model = solver.get_model() if is_sat else None
        solver.delete()

        return is_sat, runtime

    def get_model(self):
        return self.model