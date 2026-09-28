import sys
from encoder import NQueensEncoder
from solver import SATSolverWrapper

sys.stdout.reconfigure(encoding='utf-8')

def run_benchmark():
    n = 8
    print(f"--- Đang test thuật toán cơ bản (Binomial) với N = {n} ---")
    
    encoder = NQueensEncoder(n)
    clauses, num_vars = encoder.generate_clauses()
    
    solver = SATSolverWrapper(clauses)
    is_sat, runtime = solver.solve('glucose3')
    
    print(f"Số biến: {num_vars} | Số mệnh đề: {len(clauses)}")
    print(f"Kết quả SAT: {is_sat} | Thời gian giải: {runtime:.6f}s")
    
    # TODO: Cần viết thêm các thuật toán AMO phức tạp hơn (Binary, Commander...)
    # TODO: Viết vòng lặp test nhiều N và lưu kết quả ra file CSV

if __name__ == "__main__":
    run_benchmark()