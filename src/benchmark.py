import argparse
import csv
import os
import statistics
import sys
import time
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
from encoder import NQueensEncoder
from solver import SATSolverWrapper
from cp_solver import CPQueensSolver
from cplex_mip_solver import CplexMIPSolver
from cplex_cp_solver import CplexCPSolver

sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(PROJECT_ROOT, 'results')

DEFAULT_SIZES = [10, 15, 20, 25, 30]
DEFAULT_METHODS = ["binomial", "sequential", "binary", "commander", "product", "cp-sat", "cplex-mip", "cplex-cp"]
CSV_COLUMNS = [
    'Board_Size', 'Algorithm', 'Variables', 'Clauses',
    'Gen_Time(s)', 'Solve_Time(s)', 'Runtime(s)', 'Is_SAT', 'Solution_Valid', 'Error',
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
    return parser.parse_args()

def record_result(writer, results, n, alg_label, num_vars, num_clauses,
                  gen_time, solve_time, total_time, is_sat, valid, error=""):
    writer.writerow([
        n, alg_label, num_vars, num_clauses,
        f"{gen_time:.6f}", f"{solve_time:.6f}", f"{total_time:.6f}",
        is_sat, valid, error,
    ])
    results.append({
        'N': n, 'Algorithm': alg_label, 'Vars': num_vars, 'Clauses': num_clauses,
        'Gen_Time': gen_time, 'Solve_Time': solve_time, 'Time': total_time,
        'Is_SAT': is_sat, 'Valid': valid, 'Error': error,
    })

def benchmark_sat(n, enc_name, solver_name, repeats):
    gen_times, solve_times = [], []
    num_vars = num_clauses = 0
    is_sat = None
    valid = None
    encoder = None
    solver = None
    for _ in range(repeats):
        encoder = NQueensEncoder(n)
        start_gen = time.time()
        clauses, num_vars = encoder.generate_clauses(enc_type=enc_name)
        gen_times.append(time.time() - start_gen)
        num_clauses = len(clauses)
        solver = SATSolverWrapper(clauses)
        is_sat, solve_time = solver.solve(solver_name)
        solve_times.append(solve_time)
        if not is_sat:
            break
    if is_sat and encoder is not None and solver is not None:
        valid = encoder.verify_solution(solver.get_model(), n)

    return (num_vars, num_clauses,
            statistics.mean(gen_times), statistics.mean(solve_times),
            is_sat, valid)

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
                else:
                    alg_label = enc_name.capitalize()
                
                try:
                    if enc_name in ["cp-sat", "cplex-mip", "cplex-cp"]:
                        gen_times, solve_times = [], []
                        is_sat, valid = None, None
                        timed_out = False
                        active_solver = None
                        for _ in range(args.repeats):
                            start_gen = time.time()
                            if enc_name == "cp-sat":
                                active_solver = CPQueensSolver(n)
                            elif enc_name == "cplex-mip":
                                active_solver = CplexMIPSolver(n)
                            elif enc_name == "cplex-cp":
                                active_solver = CplexCPSolver(n)

                            gen_times.append(time.time() - start_gen)
                            is_sat, solve_time = active_solver.solve(time_limit_sec=args.timeout)
                            solve_times.append(solve_time)
                            timed_out = getattr(active_solver, 'timed_out', False)
                            if not is_sat:
                                break
                        gen_time = statistics.mean(gen_times)
                        solve_time = statistics.mean(solve_times)
                        total_time = gen_time + solve_time
                        num_vars, num_clauses = 0, 0
                        if is_sat and active_solver is not None:
                            valid = active_solver.verify_solution()
                        error = "TIMEOUT" if timed_out else ""
                    else:
                        (num_vars, num_clauses, gen_time, solve_time,
                         is_sat, valid) = benchmark_sat(
                            n, enc_name, args.solver, args.repeats)
                        total_time = gen_time + solve_time
                        error = ""
                    record_result(writer, results, n, alg_label, num_vars, num_clauses,
                                  gen_time, solve_time, total_time, is_sat, valid, error)
                    print(f"[{alg_label:>10}] Biến: {num_vars:<6} | Mệnh đề: {num_clauses:<8} "
                          f"| Sinh: {gen_time:.6f}s | Giải: {solve_time:.6f}s "
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
    plot_charts(results)

def plot_charts(results):
    if not results:
        print("=> Không có dữ liệu để vẽ biểu đồ.")
        return
    os.makedirs(RESULTS_DIR, exist_ok=True)
    df = pd.DataFrame(results)
    df = df[df['Error'] == ""]
    if df.empty:
        print("=> Toàn bộ kết quả đều lỗi, bỏ qua bước vẽ biểu đồ.")
        return

    plt.figure(figsize=(10, 6))
    for alg in df['Algorithm'].unique():
        subset = df[df['Algorithm'] == alg].sort_values('N')
        plt.plot(subset['N'], subset['Time'], marker='o', label=alg, linewidth=2)
    plt.yscale('log')
    plt.title('Runtime Comparison (SAT vs CP vs MIP) — log scale')
    plt.xlabel('Board Size (N)')
    plt.ylabel('Runtime (seconds, log scale)')
    plt.legend()
    plt.grid(True, which='both', alpha=0.3)
    plt.savefig(os.path.join(RESULTS_DIR, 'chart_runtime_comparison.png'), dpi=150, bbox_inches='tight')
    plt.close()
    df_sat = df[~df['Algorithm'].isin(['CP-SAT', 'CPLEX-MIP', 'CPLEX-CP'])]
    if not df_sat.empty:
        plt.figure(figsize=(10, 6))
        for alg in df_sat['Algorithm'].unique():
            subset = df_sat[df_sat['Algorithm'] == alg].sort_values('N')
            plt.plot(subset['N'], subset['Clauses'], marker='s', label=alg, linewidth=2)
        plt.title('Clauses Generation Comparison (SAT Encodings)')
        plt.xlabel('Board Size (N)')
        plt.ylabel('Number of Clauses')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.savefig(os.path.join(RESULTS_DIR, 'chart_clauses_comparison.png'), dpi=150, bbox_inches='tight')
        plt.close()

    print("=> Đã sinh thành công biểu đồ PNG tại thư mục results/")

if __name__ == "__main__":
    run_benchmark(parse_args())