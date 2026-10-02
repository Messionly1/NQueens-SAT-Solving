import time
import multiprocessing
from pysat.solvers import Solver

def _solve_worker(solver_name, clauses, result_queue):
    solver = Solver(name=solver_name)
    for clause in clauses:
        solver.add_clause(clause)
        
    start_time = time.time()
    is_sat = solver.solve()
    end_time = time.time()
    
    model = solver.get_model() if is_sat else None
    solver.delete()
    result_queue.put((is_sat, model, end_time - start_time))

class SATSolverWrapper:
    def __init__(self, clauses: list):
        self.clauses = clauses
        self.model = None

    def solve(self, solver_name: str = 'glucose3', time_limit_sec: float = 100.0):
        ctx = multiprocessing.get_context('spawn')
        q = ctx.Queue()
        p = ctx.Process(target=_solve_worker, args=(solver_name, self.clauses, q))
        
        start_time = time.time()
        p.start()
        
        try:
            import queue
            is_sat, self.model, runtime = q.get(timeout=time_limit_sec)
            p.join()
            return is_sat, runtime
        except queue.Empty:
            p.terminate()
            p.join()
            return False, time_limit_sec
        except Exception:
            p.terminate()
            p.join()
            return False, time.time() - start_time

    def get_model(self):
        return self.model