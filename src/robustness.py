import argparse
import csv
import os
import statistics
import sys

from encoder import NQueensEncoder
from solver import SATSolverWrapper

sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(PROJECT_ROOT, 'results')
ENCODINGS = ["binomial", "sequential", "binary", "commander", "product"]


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--sizes', type=int, nargs='+', default=[30, 50])
    parser.add_argument('--encodings', type=str, nargs='+', default=ENCODINGS)
    parser.add_argument('--seeds', type=int, default=10, help='Số bản CNF (seed 0 = gốc)')
    parser.add_argument('--timeout', type=float, default=60.0)
    parser.add_argument('--solver', type=str, default='glucose3')
    parser.add_argument('--out', type=str, default='robustness_shuffle.csv')
    return parser.parse_args()


def main():
    args = parse_args()
    os.makedirs(RESULTS_DIR, exist_ok=True)
    csv_path = os.path.join(RESULTS_DIR, args.out)
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Board_Size', 'Encoding', 'Solver', 'Seed', 'Variables', 'Clauses',
                         'Solve_Time(s)', 'Status', 'Solution_Valid'])
        for n in args.sizes:
            print(f"\n--- N = {n}, {args.seeds} seeds, timeout {args.timeout:g}s ---")
            for enc in args.encodings:
                encoder = NQueensEncoder(n)
                clauses, num_vars = encoder.generate_clauses(enc_type=enc)
                times, n_timeout = [], 0
                for seed in range(args.seeds):
                    solver = SATSolverWrapper(clauses, num_vars=num_vars, seed=seed)
                    is_sat, t = solver.solve(args.solver, time_limit_sec=args.timeout)
                    if solver.timed_out:
                        status, valid = 'TIMEOUT', ''
                        n_timeout += 1
                    else:
                        status = 'SAT' if is_sat else 'UNSAT'
                        valid = encoder.verify_solution(solver.get_model(), n) if is_sat else False
                    writer.writerow([n, enc.capitalize(), args.solver, seed, num_vars, len(clauses),
                                     f"{t:.6f}", status, valid])
                    f.flush()
                    times.append(t if not solver.timed_out else float('inf'))
                print(f"[{enc.capitalize():>10}] gốc: {times[0]:9.3f}s | trung vị: "
                      f"{statistics.median(times):9.3f}s | min: {min(times):8.3f}s | "
                      f"max: {max(times):9.3f}s | timeout: {n_timeout}/{args.seeds}")
    print(f"\n=> Đã lưu: {csv_path}")


if __name__ == '__main__':
    main()
