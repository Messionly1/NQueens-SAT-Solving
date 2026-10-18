import multiprocessing
import random
import time
from pysat.solvers import Solver

SOLVER_ALIASES = {
    'cryptosat': 'cms',
    'cryptominisat': 'cms',
    'cryptominisat5': 'cms',
    'cms5': 'cms',
}

LOAD_TIMEOUT_SEC = 600.0


def _normalize_solver_name(solver_name: str) -> str:
    return SOLVER_ALIASES.get(solver_name, solver_name)


def permute_cnf(clauses, num_vars: int, seed: int):
    if seed == 0:
        return clauses, None
    rng = random.Random(seed)
    perm = list(range(1, num_vars + 1))
    rng.shuffle(perm)
    forward = [0] + perm
    inverse = [0] * (num_vars + 1)
    for old, new in enumerate(forward):
        inverse[new] = old
    out = [[forward[l] if l > 0 else -forward[-l] for l in c] for c in clauses]
    for c in out:
        rng.shuffle(c)
    rng.shuffle(out)
    return out, inverse


def unpermute_model(model, inverse):
    if model is None or inverse is None:
        return model
    return [inverse[l] if l > 0 else -inverse[-l] for l in model]


def _solve_worker(solver_name, clauses, conn):
    try:
        solver = Solver(name=_normalize_solver_name(solver_name))
        start_load = time.perf_counter()
        solver.append_formula(clauses)
        conn.send(('loaded', time.perf_counter() - start_load))

        start_time = time.perf_counter()
        is_sat = solver.solve()
        end_time = time.perf_counter()

        model = solver.get_model() if is_sat else None
        solver.delete()
        conn.send(('done', (is_sat, model, end_time - start_time)))
    except Exception as exc:
        conn.send(('error', f"{type(exc).__name__}: {exc}"))


class SATSolverWrapper:
    def __init__(self, clauses: list, num_vars: int = 0, seed: int = 0):
        if seed and not num_vars:
            raise ValueError("num_vars là bắt buộc khi seed != 0")
        self.clauses, self._inverse = permute_cnf(clauses, num_vars, seed)
        self.model = None
        self.timed_out = False
        self.load_time = 0.0

    @staticmethod
    def _get(conn, p, timeout):
        if not conn.poll(timeout):
            return None
        try:
            return conn.recv()
        except EOFError:
            p.join()
            raise RuntimeError(f"Tiến trình SAT kết thúc bất thường (exitcode={p.exitcode})")

    def solve(self, solver_name: str = 'glucose3', time_limit_sec: float = 100.0):
        self.model, self.timed_out, self.load_time = None, False, 0.0
        ctx = multiprocessing.get_context('spawn')
        recv_conn, send_conn = ctx.Pipe(duplex=False)
        p = ctx.Process(target=_solve_worker, args=(solver_name, self.clauses, send_conn))
        p.start()
        send_conn.close()
        try:
            msg = self._get(recv_conn, p, LOAD_TIMEOUT_SEC)
            if msg is None:
                raise RuntimeError("Quá thời gian nạp CNF vào solver")
            if msg[0] == 'error':
                raise RuntimeError(msg[1])
            self.load_time = msg[1]

            msg = self._get(recv_conn, p, time_limit_sec)
            if msg is None:
                self.timed_out = True
                return False, time_limit_sec
            if msg[0] == 'error':
                raise RuntimeError(msg[1])
            is_sat, model, runtime = msg[1]
            self.model = unpermute_model(model, self._inverse)
            return is_sat, runtime
        finally:
            if p.is_alive():
                p.terminate()
            p.join()
            recv_conn.close()

    def get_model(self):
        return self.model
