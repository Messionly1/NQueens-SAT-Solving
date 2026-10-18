import argparse
import csv
import os
import statistics
import sys

from cp_solver import CPQueensSolver

sys.stdout.reconfigure(encoding='utf-8')

RESULTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'results')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--sizes', type=int, nargs='+', default=[8, 30, 50])
    parser.add_argument('--repeats', type=int, default=10)
    parser.add_argument('--out', type=str, default='cpsat_noise_per_run.csv')
    args = parser.parse_args()

    os.makedirs(RESULTS_DIR, exist_ok=True)
    path = os.path.join(RESULTS_DIR, args.out)
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Board_Size', 'Run', 'Solve_Time(s)', 'Solution_Valid'])
        for n in args.sizes:
            times = []
            for run in range(1, args.repeats + 1):
                solver = CPQueensSolver(n)
                is_sat, t = solver.solve(time_limit_sec=60.0)
                writer.writerow([n, run, f"{t:.6f}", is_sat and solver.verify_solution()])
                times.append(t)
            rest = times[1:]
            print(f"N={n}: mean={statistics.mean(times):.4f}s  CV={statistics.stdev(times) / statistics.mean(times):.1%}  "
                  f"run1={times[0]:.4f}s  mean(run2..)={statistics.mean(rest):.4f}s  "
                  f"min={min(times):.4f}s  max={max(times):.4f}s")
    print(f"=> Đã lưu: {path}")


if __name__ == '__main__':
    main()
