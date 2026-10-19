import argparse
import csv
import os
import sys

from cplex_cp_solver import CplexCPSolver
from gurobi_mip_solver import GurobiMIPSolver

sys.stdout.reconfigure(encoding='utf-8')

RESULTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'results')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--sizes', type=int, nargs='+', default=[8, 10, 15, 20, 25, 30, 40, 50])
    parser.add_argument('--out', type=str, default='solver_stats.csv')
    args = parser.parse_args()

    os.makedirs(RESULTS_DIR, exist_ok=True)
    path = os.path.join(RESULTS_DIR, args.out)
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Board_Size', 'Solver', 'Wall_Time(s)', 'Engine_Time(s)',
                         'Node_Count', 'Sol_Count', 'Obj_Val', 'Obj_Bound', 'Solution_Valid', 'Error'])
        for n in args.sizes:
            try:
                g = GurobiMIPSolver(n)
                is_sat, t = g.solve(time_limit_sec=60.0)
                m = g.model
                writer.writerow([n, 'Gurobi-MIP', f"{t:.6f}", f"{m.Runtime:.6f}", int(m.NodeCount),
                                 m.SolCount, m.ObjVal if m.SolCount else '', m.ObjBound if m.SolCount else '',
                                 is_sat and g.verify_solution(), ''])
            except Exception as exc:
                writer.writerow([n, 'Gurobi-MIP', '', '', '', '', '', '', '', f"{type(exc).__name__}: {exc}"])
            try:
                c = CplexCPSolver(n)
                is_sat, t = c.solve(time_limit_sec=60.0)
                writer.writerow([n, 'CPLEX-CP', f"{t:.6f}", c.engine_time, '', '', '', '',
                                 is_sat and c.verify_solution(), ''])
            except Exception as exc:
                writer.writerow([n, 'CPLEX-CP', '', '', '', '', '', '', '', f"{type(exc).__name__}: {exc}"])
            f.flush()
            print(f"N={n} xong")
    print(f"=> Đã lưu: {path}")


if __name__ == '__main__':
    main()
