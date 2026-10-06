import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from encoder import NQueensEncoder
from solver import SATSolverWrapper


try:
    from cp_solver import CPQueensSolver
except ImportError:  # OR-Tools chưa được cài
    CPQueensSolver = None


class TestNQueensSolvers(unittest.TestCase):
    def test_sat_solver(self):
        encoder = NQueensEncoder(n=4)
        clauses, _ = encoder.generate_clauses(enc_type="sequential")
        solver = SATSolverWrapper(clauses)
        is_sat, solve_time = solver.solve(solver_name="glucose3", time_limit_sec=10.0)
        self.assertTrue(is_sat)
        self.assertGreaterEqual(solve_time, 0.0)
        model = solver.get_model()
        self.assertIsNotNone(model)
        self.assertTrue(encoder.verify_solution(model, n=4))

    @unittest.skipIf(CPQueensSolver is None, "Chưa cài đặt OR-Tools (ortools)")
    def test_cp_sat_solver(self):
        solver = CPQueensSolver(n=4)
        is_sat, solve_time = solver.solve(time_limit_sec=10.0)
        self.assertTrue(is_sat)
        self.assertGreaterEqual(solve_time, 0.0)
        self.assertTrue(solver.verify_solution())


if __name__ == "__main__":
    unittest.main()
