import csv
import os
import sys
import time
import matplotlib.pyplot as plt
import pandas as pd

from encoder import NQueensEncoder
from solver import SATSolverWrapper
from cp_solver import CPQueensSolver

sys.stdout.reconfigure(encoding='utf-8')

def run_benchmark():
    board_sizes = [10, 15, 20, 25, 30]
    encoding_methods = ["binomial", "sequential", "binary", "commander", "product", "cp-sat"]
    
    os.makedirs('results', exist_ok=True)
    csv_file = 'results/sat_vs_cp_benchmark.csv'
    results = []

    with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Board_Size', 'Algorithm', 'Variables', 'Clauses', 'Is_SAT', 'Runtime(s)'])
        
        for n in board_sizes:
            print(f"\n--- Đang kiểm thử N = {n} ---")
            for enc_name in encoding_methods:
                if enc_name == "cp-sat":
                    cp_solver = CPQueensSolver(n)
                    is_sat, runtime = cp_solver.solve()
                    num_vars, num_clauses = 0, 0 
                    writer.writerow([n, "CP-SAT", num_vars, num_clauses, is_sat, f"{runtime:.6f}"])
                    results.append({'N': n, 'Algorithm': 'CP-SAT', 'Vars': num_vars, 'Clauses': num_clauses, 'Time': runtime})
                    print(f"[    CP-SAT] T.gian: {runtime:.6f}s")
                else:
                    encoder = NQueensEncoder(n)
                    
                    start_gen = time.time()
                    clauses, num_vars = encoder.generate_clauses(enc_type=enc_name)
                    gen_time = time.time() - start_gen
                    
                    num_clauses = len(clauses)
                    solver = SATSolverWrapper(clauses)
                    is_sat, runtime = solver.solve('glucose3')
                    
                    total_time = runtime + gen_time
                    
                    writer.writerow([n, enc_name.capitalize(), num_vars, num_clauses, is_sat, f"{total_time:.6f}"])
                    results.append({'N': n, 'Algorithm': enc_name.capitalize(), 'Vars': num_vars, 'Clauses': num_clauses, 'Time': total_time})
                    print(f"[{enc_name.capitalize():>10}] Biến: {num_vars:<6} | Mệnh đề: {num_clauses:<8} | T.gian: {total_time:.6f}s")
                    
    print(f"\n=> Thực nghiệm hoàn tất! Dữ liệu lưu tại: {csv_file}")
    plot_charts(results)

def plot_charts(results):
    df = pd.DataFrame(results)
    
    plt.figure(figsize=(10, 6))
    for alg in df['Algorithm'].unique():
        subset = df[df['Algorithm'] == alg]
        plt.plot(subset['N'], subset['Time'], marker='o', label=alg, linewidth=2)
    plt.title('Runtime Comparison (SAT vs CP-SAT)')
    plt.xlabel('Board Size (N)')
    plt.ylabel('Runtime (seconds)')
    plt.legend()
    plt.grid(True)
    plt.savefig('results/chart_runtime_comparison.png')
    plt.close()
    
    df_sat = df[df['Algorithm'] != 'CP-SAT']
    plt.figure(figsize=(10, 6))
    for alg in df_sat['Algorithm'].unique():
        subset = df_sat[df_sat['Algorithm'] == alg]
        plt.plot(subset['N'], subset['Clauses'], marker='s', label=alg, linewidth=2)
    plt.title('Clauses Generation Comparison (SAT Encodings)')
    plt.xlabel('Board Size (N)')
    plt.ylabel('Number of Clauses')
    plt.legend()
    plt.grid(True)
    plt.savefig('results/chart_clauses_comparison.png')
    plt.close()
    
    print("=> Đã sinh thành công biểu đồ PNG tại thư mục results/")

if __name__ == "__main__":
    run_benchmark()