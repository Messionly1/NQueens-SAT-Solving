import csv
import os
import sys
from encoder import NQueensEncoder
from solver import SATSolverWrapper

sys.stdout.reconfigure(encoding='utf-8')

def run_benchmark():
    board_sizes = [4, 8, 10, 12, 15] 
    encoding_methods = ["binomial", "sequential", "binary", "commander", "product"]
    
    os.makedirs('results', exist_ok=True)
    csv_file = 'results/sat_benchmark_results.csv'
    
    with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Board_Size', 'Encoding_Method', 'Variables', 'Clauses', 'Is_SAT', 'Runtime(s)'])
        
        for n in board_sizes:
            print(f"--- Đang kiểm thử N = {n} ---")
            for enc_name in encoding_methods:
                encoder = NQueensEncoder(n)
                clauses, num_vars = encoder.generate_clauses(enc_type=enc_name)
                
                solver = SATSolverWrapper(clauses)
                is_sat, runtime = solver.solve('glucose3')
                
                writer.writerow([n, enc_name.capitalize(), num_vars, len(clauses), is_sat, f"{runtime:.6f}"])
                print(f"[{enc_name.capitalize():>10}] Số biến: {num_vars:<5} | Mệnh đề: {len(clauses):<5} | SAT: {is_sat} | T.gian: {runtime:.6f}s")
                
    print(f"\n=> Thực nghiệm hoàn tất! Dữ liệu đã lưu tại: {csv_file}")

if __name__ == "__main__":
    run_benchmark()