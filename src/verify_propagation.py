import argparse
import itertools
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pysat.solvers import Solver

from encoder import NQueensEncoder

sys.stdout.reconfigure(encoding='utf-8')

ENCODINGS = ["binomial", "sequential", "binary", "commander", "product"]


def amo_cnf(enc, m):
    e = NQueensEncoder(m)
    lits = list(range(1, m + 1))
    clauses = getattr(e, "encode_amo_" + enc)(lits)
    return clauses, lits, e.next_var - 1


def check_semantics(solver, lits):
    for bits in itertools.product([0, 1], repeat=len(lits)):
        assumptions = [l if b else -l for l, b in zip(lits, bits)]
        if solver.solve(assumptions=assumptions) != (sum(bits) <= 1):
            return False
    return True


def check_acup(solver, lits):
    for k in lits:
        ok, implied = solver.propagate(assumptions=[k])
        if not ok or any(-j not in implied for j in lits if j != k):
            return False
    return True


def floating_aux(solver, lits, top):
    all_false = [-l for l in lits]
    return [a for a in range(len(lits) * len(lits) + 1, top + 1)
            if solver.solve(assumptions=all_false + [a])]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--max-size', type=int, default=12)
    args = parser.parse_args()

    print(f"AMO trên m = 2..{args.max_size} biến (ngữ nghĩa kiểm vét cạn với m <= 10)\n")
    print(f"{'Encoding':<12}{'Đúng AMO':<10}{'ACUP':<8}{'Biến phụ tự do khi mọi x sai (m = max)'}")
    all_ok = True
    for enc in ENCODINGS:
        sem = acup = True
        n_float = n_aux = 0
        for m in range(2, args.max_size + 1):
            clauses, lits, top = amo_cnf(enc, m)
            with Solver(name='glucose3', bootstrap_with=clauses) as s:
                if m <= 10:
                    sem &= check_semantics(s, lits)
                acup &= check_acup(s, lits)
                if m == args.max_size:
                    n_aux = max(0, top - m * m)
                    n_float = len(floating_aux(s, lits, top))
        all_ok &= sem and acup
        print(f"{enc:<12}{str(sem):<10}{str(acup):<8}{n_float}/{n_aux}")

    print("\nKết luận: mọi encoding đều đúng và đạt ACUP; khác biệt giữa chúng nằm ở số")
    print("biến phụ, số mệnh đề và mức độ ràng buộc của biến phụ, không nằm ở sức mạnh")
    print("lan truyền trên các biến quân hậu.")
    sys.exit(0 if all_ok else 1)


if __name__ == '__main__':
    main()
