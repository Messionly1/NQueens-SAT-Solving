import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from encoder import NQueensEncoder
from pysat_encoder import PySatNQueensEncoder


class TestNQueensEncoder(unittest.TestCase):
    def test_handwritten_encodings(self):
        enc_types = ["binomial", "sequential", "binary", "commander", "product"]
        for enc_type in enc_types:
            encoder = NQueensEncoder(n=4)
            clauses, nvars = encoder.generate_clauses(enc_type=enc_type)
            self.assertGreater(len(clauses), 0)
            self.assertGreaterEqual(nvars, 16)

    def test_pysat_cardenc_encodings(self):
        enc_types = ["binomial", "sequential", "binary", "commander", "product"]
        for enc_type in enc_types:
            encoder = PySatNQueensEncoder(n=4, encoding=enc_type)
            clauses, nvars = encoder.generate_clauses()
            self.assertGreater(len(clauses), 0)
            self.assertGreaterEqual(nvars, 16)

    def test_solution_verification(self):
        encoder = NQueensEncoder(n=4)
        valid_model = [2, 8, 9, 15]
        invalid_model = [1, 2, 3, 4]

        self.assertTrue(encoder.verify_solution(valid_model, n=4))
        self.assertFalse(encoder.verify_solution(invalid_model, n=4))


if __name__ == "__main__":
    unittest.main()
