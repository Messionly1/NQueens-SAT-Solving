import argparse
import csv
import os
import statistics
import sys
import time
from encoder import NQueensEncoder
from pysat_encoder import PySatNQueensEncoder
from solver import SATSolverWrapper
from cp_solver import CPQueensSolver
from cplex_mip_solver import CplexMIPSolver
from cplex_cp_solver import CplexCPSolver
from gurobi_mip_solver import GurobiMIPSolver

sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(PROJECT_ROOT, 'results')

AVAILABLE_SAT_SOLVERS = [
    'glucose3', 'glucose4', 'cadical153', 'cadical195',
    'lingeling', 'minisat22', 'maplesat', 'cms',
]
DEFAULT_SIZES = [10, 15, 20, 25, 30]
DEFAULT_METHODS = ["binomial", "sequential", "binary", "commander", "product", "cp-sat", "cplex-mip", "cplex-cp", "gurobi-mip"]
CSV_COLUMNS = [
    'Board_Size', 'Algorithm', 'Variables', 'Clauses',
    'Gen_Time(s)', 'Solve_Time(s)', 'Solve_Std(s)', 'Solve_Min(s)', 'Solve_Max(s)', 'Repeats_Done',
    'Runtime(s)', 'Is_SAT', 'Solution_Valid', 'Error',
]

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--sizes', type=int, nargs='+', default=DEFAULT_SIZES)
    parser.add_argument('--methods', type=str, nargs='+', default=DEFAULT_METHODS)
    parser.add_argument('--repeats', type=int, default=3)
    parser.add_argument('--timeout', type=float, default=100.0)
    parser.add_argument('--solver', type=str, default='glucose3')
    parser.add_argument('--out', type=str, default='sat_vs_cp_benchmark.csv')
    parser.add_argument('--no-append', action='store_true')
    parser.add_argument('--first-solution', action='store_true',
                        help='Với CP/MIP: dừng ngay tại nghiệm khả thi đầu tiên '
                             '(so sánh công bằng với SAT)')
    return parser.parse_args()

def record_result(writer, results, n, alg_label, num_vars, num_clauses,
                  gen_time, solve_time, total_time, is_sat, valid, error="",
                  solve_std=0.0, solve_min=0.0, solve_max=0.0, repeats_done=0):
    writer.writerow([
        n, alg_label, num_vars, num_clauses,
        f"{gen_time:.6f}", f"{solve_time:.6f}", f"{solve_std:.6f}",
        f"{solve_min:.6f}", f"{solve_max:.6f}", repeats_done,
        f"{total_time:.6f}",
        is_sat, valid, error,
    ])
    results.append({
        'N': n, 'Algorithm': alg_label, 'Vars': num_vars, 'Clauses': num_clauses,
        'Gen_Time': gen_time, 'Solve_Time': solve_time, 'Solve_Std': solve_std,
        'Solve_Min': solve_min, 'Solve_Max': solve_max, 'Repeats_Done': repeats_done,
        'Time': total_time,
        'Is_SAT': is_sat, 'Valid': valid, 'Error': error,
    })

def benchmark_sat(n, enc_name, solver_name, repeats, timeout_sec=100.0):
    effective_solver = solver_name
    if ':' in enc_name:
        solver_prefix, enc_name = enc_name.split(':', 1)
        if solver_prefix not in AVAILABLE_SAT_SOLVERS:
            raise ValueError(f"SAT solver không hỗ trợ: {solver_prefix}")
        effective_solver = solver_prefix

    use_pysat = enc_name.startswith('pysat-')
    base_enc = enc_name[6:] if use_pysat else enc_name

    gen_times, solve_times = [], []
    num_vars = num_clauses = 0
    is_sat = None
    valid = None
    encoder = None
    solver = None
    timed_out = False
    for _ in range(repeats):
        start_gen = time.perf_counter()
        if use_pysat:
            encoder = PySatNQueensEncoder(n, encoding=base_enc)
            clauses, num_vars = encoder.generate_clauses()
        else:
            encoder = NQueensEncoder(n)
            clauses, num_vars = encoder.generate_clauses(enc_type=base_enc)
        gen_times.append(time.perf_counter() - start_gen)
        num_clauses = len(clauses)
        solver = SATSolverWrapper(clauses)
        is_sat, solve_time = solver.solve(effective_solver, time_limit_sec=timeout_sec)
        solve_times.append(solve_time)
        timed_out = solver.timed_out
        if not is_sat:
            break
    if is_sat and encoder is not None and solver is not None:
        valid = encoder.verify_solution(solver.get_model(), n)

    solve_stats = _summarize(solve_times)
    error = "TIMEOUT" if timed_out else ""
    return (num_vars, num_clauses,
            statistics.mean(gen_times), solve_stats,
            is_sat, valid, error)

def _summarize(times):
    if not times:
        return (0.0, 0.0, 0.0, 0.0, 0)
    mean = statistics.mean(times)
    std = statistics.pstdev(times) if len(times) > 1 else 0.0
    return (mean, std, min(times), max(times), len(times))

def run_benchmark(args):
    os.makedirs(RESULTS_DIR, exist_ok=True)
    csv_path = os.path.join(RESULTS_DIR, args.out)
    file_exists = os.path.isfile(csv_path) and not args.no_append
    mode = 'a' if file_exists else 'w'

    results = []
    with open(csv_path, mode=mode, newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(CSV_COLUMNS)

        for n in args.sizes:
            print(f"\n--- Đang kiểm thử N = {n} (lặp {args.repeats} lần) ---")
            for enc_name in args.methods:
                if enc_name == "cp-sat":
                    alg_label = "CP-SAT"
                elif enc_name == "cplex-mip":
                    alg_label = "CPLEX-MIP"
                elif enc_name == "cplex-cp":
                    alg_label = "CPLEX-CP"
                elif enc_name == "gurobi-mip":
                    alg_label = "Gurobi-MIP"
                elif ":" in enc_name:
                    solver_prefix, enc_part = enc_name.split(":", 1)
                    enc_display = enc_part[6:].capitalize() if enc_part.startswith("pysat-") else enc_part.capitalize()
                    alg_label = f"{solver_prefix}-{enc_display}"
                elif enc_name.startswith("pysat-"):
                    alg_label = "PySAT-" + enc_name[6:].capitalize()
                else:
                    alg_label = enc_name.capitalize()

                if args.first_solution and enc_name in ["cp-sat", "cplex-mip", "cplex-cp", "gurobi-mip"]:
                    alg_label = alg_label + " (first-sol)"

                try:
                    if enc_name in ["cp-sat", "cplex-mip", "cplex-cp", "gurobi-mip"]:
                        gen_times, solve_times = [], []
                        is_sat, valid = None, None
                        timed_out = False
                        active_solver = None
                        for _ in range(args.repeats):
                            start_gen = time.perf_counter()
                            if enc_name == "cp-sat":
                                active_solver = CPQueensSolver(n)
                            elif enc_name == "cplex-mip":
                                active_solver = CplexMIPSolver(n)
                            elif enc_name == "cplex-cp":
                                active_solver = CplexCPSolver(n)
                            elif enc_name == "gurobi-mip":
                                active_solver = GurobiMIPSolver(n)

                            gen_times.append(time.perf_counter() - start_gen)
                            is_sat, solve_time = active_solver.solve(
                                time_limit_sec=args.timeout,
                                first_solution=args.first_solution)
                            solve_times.append(solve_time)
                            timed_out = getattr(active_solver, 'timed_out', False)
                            if not is_sat:
                                break
                        gen_time = statistics.mean(gen_times)
                        solve_time, solve_std, solve_min, solve_max, reps_done = _summarize(solve_times)
                        total_time = gen_time + solve_time
                        num_vars, num_clauses = 0, 0
                        if is_sat and active_solver is not None:
                            valid = active_solver.verify_solution()
                        error = "TIMEOUT" if timed_out else ""
                    else:
                        (num_vars, num_clauses, gen_time, solve_stats,
                         is_sat, valid, error) = benchmark_sat(
                            n, enc_name, args.solver, args.repeats, args.timeout)
                        solve_time, solve_std, solve_min, solve_max, reps_done = solve_stats
                        total_time = gen_time + solve_time
                    record_result(writer, results, n, alg_label, num_vars, num_clauses,
                                  gen_time, solve_time, total_time, is_sat, valid, error,
                                  solve_std, solve_min, solve_max, reps_done)
                    print(f"[{alg_label:>10}] Biến: {num_vars:<6} | Mệnh đề: {num_clauses:<8} "
                          f"| Sinh: {gen_time:.6f}s | Giải: {solve_time:.6f}s (std {solve_std:.6f}, "
                          f"n={reps_done}) "
                          f"| Tổng: {total_time:.6f}s | Nghiệm hợp lệ: {valid}"
                          + (f" | {error}" if error else ""))
                except RuntimeError as e:
                    if str(e) == "MISSING_ENGINE":
                        print(f"[{alg_label:>10}] BỎ QUA: Chưa cài engine CP Optimizer của IBM.")
                    else:
                        error_msg = f"{type(e).__name__}: {e}"
                        print(f"[{alg_label:>10}] LỖI: {error_msg}")
                        record_result(writer, results, n, alg_label, 0, 0, 0.0, 0.0, 0.0, "", None, error_msg)
                except Exception as exc:
                    error_msg = f"{type(exc).__name__}: {exc}"
                    print(f"[{alg_label:>10}] LỖI: {error_msg}")
                    record_result(writer, results, n, alg_label, 0, 0, 0.0, 0.0, 0.0,
                                  "", None, error_msg)

    print(f"\n=> Thực nghiệm hoàn tất! Dữ liệu lưu tại: {csv_path}")
    is_cross_solver = any(':' in m for m in args.methods)
    plot_charts([] if is_cross_solver else results)

def plot_charts(results):
    import plot_charts as charts
    charts.main()


if __name__ == "__main__":
    run_benchmark(parse_args())