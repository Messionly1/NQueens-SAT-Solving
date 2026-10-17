import argparse
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pysat.solvers import Solver

from encoder import NQueensEncoder


def build_product(lits, e, bidirectional=False):
    if len(lits) <= 4:
        return e.encode_amo_binomial(lits), None

    p = math.ceil(math.sqrt(len(lits)))
    q = math.ceil(len(lits) / p)
    rows = e.get_new_vars(p)
    cols = e.get_new_vars(q)

    clauses = list(e.encode_amo_binomial(rows))
    clauses.extend(e.encode_amo_binomial(cols))

    grid = {}
    for i, lit in enumerate(lits):
        r, c = i // q, i % q
        grid[(r, c)] = lit
        clauses.append([-lit, rows[r]])
        clauses.append([-lit, cols[c]])

    if bidirectional:
        for r in range(p):
            cells = [grid[(r, c)] for c in range(q) if (r, c) in grid]
            if cells:
                clauses.append([-rows[r]] + cells)
        for c in range(q):
            cells = [grid[(r, c)] for r in range(p) if (r, c) in grid]
            if cells:
                clauses.append([-cols[c]] + cells)

    return clauses, rows[0]


def auxiliary_floats(clauses, aux_var, n_cells):
    solver = Solver(name='glucose3', bootstrap_with=clauses)
    solver.add_clause([aux_var])
    for cell in range(1, n_cells + 1):
        solver.add_clause([-cell])
    sat = solver.solve()
    solver.delete()
    return sat


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--size', type=int, default=12)
    args = parser.parse_args()

    if args.size <= 4:
        parser.error('--size must be greater than 4')

    n = args.size
    lits = list(range(1, n + 1))
    n_cells = n * n

    print('AMO over %d variables (cells occupy 1..%d)' % (n, n_cells))
    print('Auxiliary variables therefore start at %d\n' % (n_cells + 1))

    forward, aux_1way = build_product(lits, NQueensEncoder(n), bidirectional=False)
    twoway, aux_2way = build_product(lits, NQueensEncoder(n), bidirectional=True)

    for label, clauses, aux in [
        ('Product, forward-only (this repo)', forward, aux_1way),
        ('Product, bidirectional (Chen 2010)', twoway, aux_2way),
    ]:
        floats = auxiliary_floats(clauses, aux, n_cells)
        verdict = 'WEAK  (auxiliary is unconstrained)' if floats \
            else 'OK    (auxiliary is anchored to cells)'
        print('%-38s clauses=%-4d aux_var=%-5d -> %s'
              % (label, len(clauses), aux, verdict))

    print('\nInterpretation: forward-only Product lets a row/column auxiliary be')
    print('satisfied while no queen is placed, so unit propagation prunes less')
    print('than the original AMO constraint. Adding the converse implications')
    print('restores the anchoring at the cost of O(n) extra clauses.')


if __name__ == '__main__':
    main()
