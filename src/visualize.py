import argparse
import sys
from encoder import NQueensEncoder
from solver import SATSolverWrapper
from cp_solver import CPQueensSolver

def print_board(n: int, queens_positions: list):
    """
    In bàn cờ N-Queens ra Terminal.
    queens_positions là danh sách toạ độ cột của quân hậu tại từng hàng.
    """
    print(f"\n=== BÀN CỜ N-QUEENS (N={n}) ===")
    for r in range(n):
        row_str = ""
        for c in range(n):
            if queens_positions[r] == c:
                row_str += "[♛] "
            else:
                row_str += "[·] "
        print(row_str)
    print("=" * (n * 4))

def main():
    parser = argparse.ArgumentParser(description="Chạy và hiển thị trực quan bàn cờ N-Queens.")
    parser.add_argument("--size", type=int, default=8, help="Kích thước bàn cờ (N)")
    parser.add_argument("--method", type=str, default="cp", choices=["cp", "binomial", "sequential", "binary", "commander", "product"], help="Thuật toán muốn xem")
    args = parser.parse_args()

    n = args.size
    method = args.method.lower()

    print(f"Đang sinh bài toán N={n} bằng thuật toán: {method.upper()}...")
    
    if method == "cp":
        solver = CPQueensSolver(n)
        is_sat, runtime = solver.solve()
        if is_sat:
            solution = solver.get_model()
            print(f"Đã giải xong trong {runtime:.4f}s!")
            print_board(n, solution)
        else:
            print("Không tìm thấy nghiệm!")
    else:
        encoder = NQueensEncoder(n)
        clauses, num_vars = encoder.generate_clauses(enc_type=method)
        print(f"Đã sinh {len(clauses)} mệnh đề. Đang giải...")
        
        solver = SATSolverWrapper(clauses)
        is_sat, runtime = solver.solve()
        
        if is_sat:
            print(f"Đã giải xong trong {runtime:.4f}s!")
            model = solver.get_model()
            
            true_vars = [v for v in model if v > 0 and v <= n * n]
            
            queens_positions = [0] * n
            for v in true_vars:
                r = (v - 1) // n
                c = (v - 1) % n
                queens_positions[r] = c
                
            print_board(n, queens_positions)
        else:
            print("Không tìm thấy nghiệm!")

if __name__ == "__main__":
    main()
