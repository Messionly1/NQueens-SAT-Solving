import sys
from encoder import NQueensEncoder
from solver import SATSolverWrapper

# Ép console Windows dùng utf-8 khi print tiếng Việt
sys.stdout.reconfigure(encoding='utf-8')

def run_benchmark():
    n = 8
    encoding_methods = ["binomial", "sequential"]
    
    print(f"--- Đang test thuật toán với N = {n} ---")
    
    for enc_name in encoding_methods:
        encoder = NQueensEncoder(n)
        clauses, num_vars = encoder.generate_clauses(enc_type=enc_name)
        
        solver = SATSolverWrapper(clauses)
        is_sat, runtime = solver.solve('glucose3')
        
        print(f"[{enc_name.capitalize():>10}] Số biến: {num_vars:<5} | Mệnh đề: {len(clauses):<5} | SAT: {is_sat} | T.gian: {runtime:.6f}s")
        
    # TODO: Cần viết thêm Binary, Commander, Product...
    # TODO: Viết vòng lặp test nhiều N và lưu kết quả ra file CSV

if __name__ == "__main__":
    run_benchmark()