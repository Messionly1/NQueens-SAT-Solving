# N-Queens Problem: Exact SAT Solving vs Constraint Programming

[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![PySAT](https://img.shields.io/badge/PySAT-Glucose3-red.svg)](https://pysathq.github.io/)
[![OR-Tools](https://img.shields.io/badge/Google_OR--Tools-CP--SAT-green.svg)](https://developers.google.com/optimization/cp/cp_solver)

Dự án này là đồ án môn học nhằm giải quyết bài toán N-Queens kinh điển bằng các phương pháp tối ưu hóa chính xác (Exact Optimization). Trọng tâm của đồ án là việc mô hình hóa bài toán sang Dạng chuẩn hội (CNF) để giải bằng **SAT Solver**, đồng thời đối chuẩn hiệu năng với mô hình **Constraint Programming (CP)**.

## 🌟 Tính năng nổi bật

Dự án triển khai và phân tích toán học 5 chuẩn mã hóa At-Most-One (AMO) khác nhau để chuyển đổi ràng buộc N-Queens sang logic mệnh đề:
1. **Binomial (Pairwise)**: Không dùng biến phụ, $O(n^2)$ mệnh đề.
2. **Sequential Counter**: Sinh $O(n)$ biến phụ, $O(n)$ mệnh đề.
3. **Binary**: Sinh $O(\log n)$ biến phụ.
4. **Commander**: Thuật toán chia nhóm, $O(\sqrt{n})$ biến phụ.
5. **Product**: Thuật toán ma trận 2D, $O(\sqrt{n})$ biến phụ.

Ngoài ra, dự án tích hợp bộ giải **CP-SAT** từ thư viện Google OR-Tools (sử dụng ràng buộc toàn cục `AddAllDifferent`) để chứng minh giới hạn (bottleneck) của các thuật toán SAT truyền thống.

## 📊 Kết quả Thực nghiệm

Dự án cung cấp công cụ benchmark tự động chạy từ $N=10$ đến $N=30$.

### 1. Sự bùng nổ mệnh đề (Clause Explosion)
Chuẩn Binomial phình to bộ nhớ cực nhanh theo hàm bậc hai, trong khi Sequential và Product giữ được số lượng mệnh đề rất nhỏ gọn nhờ các biến phụ.

![Clauses Comparison](results/chart_clauses_comparison.png)

### 2. Nghịch lý Thời gian giải (Runtime Bottleneck)
Mặc dù Product và Binary có rất ít mệnh đề, việc chèn thêm các "biến phụ" (auxiliary variables) làm nhiễu loạn nghiêm trọng hệ thống Heuristic của bộ giải SAT, khiến thời gian giải bùng nổ lên tới hơn 20 giây ở $N=30$. Ngược lại, Binomial không có biến phụ lại giải cực nhanh (0.04s). Cuối cùng, CP-SAT thống trị hoàn toàn bài toán với thời gian sát mức 0 giây.

![Runtime Comparison](results/chart_runtime_comparison.png)

## 📁 Cấu trúc Dự án

```text
NQueens_SAT_Project/
├── src/
│   ├── encoder.py      # Chứa 5 thuật toán mã hóa AMO sang CNF
│   ├── solver.py       # Tích hợp PySAT (Glucose3)
│   ├── cp_solver.py    # Tích hợp Google OR-Tools (CP-SAT)
│   └── benchmark.py    # Kịch bản chạy đo lường và vẽ biểu đồ tự động
├── results/            # Chứa file CSV và các biểu đồ PNG
├── report/
│   └── main.tex        # Báo cáo học thuật LaTeX chuẩn Elsevier
├── requirements.txt    
└── README.md           
```

## 🚀 Hướng dẫn Cài đặt & Sử dụng

**Bước 1: Cài đặt môi trường**
```bash
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

**Bước 2: Chạy Benchmark và sinh biểu đồ**
```bash
python src/benchmark.py
```
Dữ liệu sẽ được lưu tự động vào thư mục `results/`.
