import sys
import os
import itertools
import math
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from pysat.solvers import Solver

from encoder import NQueensEncoder
from pysat_encoder import PySatNQueensEncoder
from solver import permute_cnf, unpermute_model
from verify import is_valid_placement, model_to_columns

ENC_TYPES = ["binomial", "sequential", "binary", "commander", "product"]


def brute_force_solutions(n):
    return {cols for cols in itertools.permutations(range(n))
            if is_valid_placement(list(cols), n) and cols[0] < math.ceil(n / 2)}


def enumerate_solutions(clauses, n):
    found = set()
    with Solver(name='glucose3', bootstrap_with=clauses) as s:
        while s.solve():
            cols = model_to_columns(s.get_model(), n)
            assert cols is not None
            found.add(tuple(cols))
            s.add_clause([-(r * n + c + 1) for r, c in enumerate(cols)])
    return found


class TestAMOEncodings(unittest.TestCase):
    def _amo(self, enc, m):
        e = NQueensEncoder(m)
        lits = list(range(1, m + 1))
        return getattr(e, "encode_amo_" + enc)(lits), lits

    def test_amo_semantics(self):
        for enc in ENC_TYPES:
            for m in range(1, 9):
                with self.subTest(enc=enc, m=m):
                    clauses, lits = self._amo(enc, m)
                    with Solver(name='glucose3', bootstrap_with=clauses) as s:
                        for bits in itertools.product([0, 1], repeat=m):
                            a = [l if b else -l for l, b in zip(lits, bits)]
                            self.assertEqual(s.solve(assumptions=a), sum(bits) <= 1)

    def test_amo_acup(self):
        for enc in ENC_TYPES:
            for m in range(2, 17):
                with self.subTest(enc=enc, m=m):
                    clauses, lits = self._amo(enc, m)
                    with Solver(name='glucose3', bootstrap_with=clauses) as s:
                        for k in lits:
                            ok, implied = s.propagate(assumptions=[k])
                            self.assertTrue(ok)
                            for j in lits:
                                if j != k:
                                    self.assertIn(-j, implied)


class TestNQueensEncoder(unittest.TestCase):
    def test_solution_sets_match_brute_force(self):
        for n in range(1, 8):
            expected = brute_force_solutions(n)
            for enc in ENC_TYPES:
                with self.subTest(n=n, enc=enc):
                    clauses, _ = NQueensEncoder(n).generate_clauses(enc_type=enc)
                    self.assertEqual(enumerate_solutions(clauses, n), expected)

    def test_pysat_cardenc_solution_sets(self):
        for n in (4, 5, 6):
            expected = brute_force_solutions(n)
            for enc in ENC_TYPES:
                with self.subTest(n=n, enc=enc):
                    clauses, _ = PySatNQueensEncoder(n, encoding=enc).generate_clauses()
                    self.assertEqual(enumerate_solutions(clauses, n), expected)

    def test_sequential_clause_count(self):
        for m in range(2, 12):
            e = NQueensEncoder(m)
            self.assertEqual(len(e.encode_amo_sequential(list(range(1, m + 1)))), 3 * m - 4)
            self.assertEqual(e.next_var - 1 - m * m, m - 1)

    def test_solution_verification(self):
        encoder = NQueensEncoder(n=4)
        self.assertTrue(encoder.verify_solution([2, 8, 9, 15], n=4))
        self.assertFalse(encoder.verify_solution([1, 2, 3, 4], n=4))
        self.assertFalse(encoder.verify_solution([2, 8, 9], n=4))
        self.assertFalse(encoder.verify_solution([2, 3, 8, 9, 15], n=4))
        self.assertTrue(is_valid_placement([1, 3, 0, 2], 4))
        self.assertFalse(is_valid_placement([0, 2, 4, 1], 4))

    def test_permutation_roundtrip(self):
        n = 6
        enc = NQueensEncoder(n)
        clauses, nvars = enc.generate_clauses(enc_type="product")
        for seed in (1, 2, 3):
            permuted, inverse = permute_cnf(clauses, nvars, seed)
            self.assertEqual(len(permuted), len(clauses))
            with Solver(name='glucose3', bootstrap_with=permuted) as s:
                self.assertTrue(s.solve())
                self.assertTrue(enc.verify_solution(unpermute_model(s.get_model(), inverse), n))


if __name__ == "__main__":
    unittest.main()
