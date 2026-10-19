# N-Queens Problem: Exact SAT Solving vs Constraint Programming

[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![PySAT](https://img.shields.io/badge/PySAT-Glucose3-red.svg)](https://pysathq.github.io/)
[![OR-Tools](https://img.shields.io/badge/Google_OR--Tools-CP--SAT-green.svg)](https://developers.google.com/optimization/cp/cp_solver)

Dự án này là đồ án môn học nghiên cứu cách giải bài toán **N-Queens** bằng các phương pháp tối ưu hóa chính xác (Exact Optimization). Trọng tâm của dự án là **mô hình hóa bài toán sang Dạng chuẩn hội (CNF)** để giải bằng **SAT Solver**, đồng thời **đối chuẩn hiệu năng** với hai họ phương pháp chính xác khác là **Constraint Programming (CP)** và **Integer Linear Programming (ILP/MIP)**.

Mục tiêu của dự án không chỉ là "giải được" bài toán, mà là trả lời một câu hỏi nghiên cứu: **việc nén số lượng mệnh đề bằng biến phụ (auxiliary variables) có thực sự giúp bộ giải SAT nhanh hơn không?** Kết quả chính (trình bày đầy đủ trong báo cáo):

- CNF nhỏ hơn **không** đồng nghĩa với giải nhanh hơn: Binomial (không biến phụ, nhiều mệnh đề nhất) nhanh nhất trên thứ tự gốc tới $N=100$ và không timeout trong 10 thứ tự đã thử ở cả ba mốc $N=30,50,100$.
- Cả 5 encoding đều **đúng** và đều đạt **ACUP** (chứng minh cho mọi kích thước trong báo cáo; kiểm chứng tự động với AMO trên $m = 2..16$ biến) — khác biệt về tốc độ không đến từ sức mạnh lan truyền.
- Thời gian giải của CDCL **rất nhạy với thứ tự biến/mệnh đề**: ở $N=30$, độ chậm của Product, Binary, Commander giảm 1083×, 515×, 32× khi hoán vị CNF. Khác biệt thật chỉ xuất hiện ở $N$ lớn: tại $N=100$, Sequential/Binary/Product thất bại trên hầu hết hoán vị, còn Commander nhanh ngang Binomial.

> 📄 **Báo cáo khoa học đầy đủ** (định dạng Elsevier `cas-sc`): [`report/main.pdf`](report/main.pdf)

## 🌟 Phạm vi dự án

### Các chuẩn mã hóa At-Most-One (AMO) được nghiên cứu

Dự án cài đặt **thủ công** 5 chuẩn mã hóa ràng buộc AMO sang CNF, đại diện cho các đánh đổi khác nhau giữa số mệnh đề, số biến phụ và hiệu quả lan truyền đơn vị:

| Chuẩn | Ý tưởng | Biến phụ | Mệnh đề |
|---|---|---|---|
| Binomial (Pairwise) | Loại trừ lẫn nhau trên mọi cặp biến | 0 | $O(n^2)$ |
| Sequential Counter | Thanh ghi đếm tuần tự (Sinz) | $O(n)$ | $O(n)$ |
| Binary | Mã hóa chỉ số biến ở hệ nhị phân | $O(\log n)$ | $O(n\log n)$ |
| Commander | Chia nhóm, mỗi nhóm một "chỉ huy" | $O(\sqrt{n})$ | $O(n\sqrt{n})$ |
| Product | Ma trận 2D dòng × cột | $O(\sqrt{n})$ | $O(n)$ |

Ngoài bản tự cài đặt, dự án còn có module gọi trực tiếp các encoder chuẩn của thư viện **PySAT** (`pysat.card.CardEnc`) để **đối chiếu chéo tính đúng đắn logic**.

Tất cả encoding SAT đều áp dụng thêm **phá đối xứng (symmetry breaking)** — ấn định quân hậu ở hàng đầu nằm ở nửa trái bàn cờ — giúp cắt giảm một nửa không gian tìm kiếm.

### Các bộ giải đối chuẩn

| Họ phương pháp | Bộ giải |
|---|---|
| SAT Solving | Glucose3, Glucose4, CaDiCaL, MapleSAT, CryptoMiniSAT5 (qua PySAT) |
| Constraint Programming | CP-SAT (Google OR-Tools), CPLEX CP Optimizer (IBM) |
| Integer Linear Programming | CPLEX MIP (IBM), Gurobi |

## ⚙️ Đặc điểm kỹ thuật

- **Đo lường tách bạch**: thời gian sinh mệnh đề (`Gen_Time`) và thời gian giải (`Solve_Time`) được đo riêng, dùng `time.perf_counter()` để đạt độ phân giải micro giây.
- **Hậu kiểm nghiệm độc lập**: nghiệm của *toàn bộ* 9 phương pháp đều được kiểm chứng bằng một hàm dùng chung (`src/verify.py`: đủ $N$ quân, không trùng hàng/cột/chéo).
- **Kiểm chứng encoding**: test tự động duyệt vét cạn ngữ nghĩa AMO, kiểm tra ACUP, và so tập nghiệm của mọi encoding với brute-force cho $N \le 7$.
- **Độ bền theo thứ tự đầu vào**: `src/robustness.py` giải mỗi encoding trên nhiều CNF hoán vị (đổi tên biến, xáo mệnh đề) để đo phân phối thời gian thay vì một lần chạy.
- **Thống kê độ nhiễu**: kết quả ghi kèm độ lệch chuẩn và min/max qua nhiều lần lặp.
- **Timeout an toàn**: cơ chế ngắt qua đa tiến trình (multiprocessing), tránh kẹt GIL trên Windows với các solver C-extension. Đồng hồ timeout chỉ bắt đầu sau khi CNF đã được nạp vào solver; TIMEOUT, UNSAT và lỗi được phân biệt rõ.
- **So sánh công bằng**: mọi solver chạy đơn luồng; hỗ trợ chế độ `--first-solution` để MIP/CP dừng ngay tại nghiệm khả thi đầu tiên, ngang bằng tiêu chí dừng của SAT.

## 📁 Cấu trúc Dự án

```text
NQueens_SAT_Project/
├── src/
│   ├── encoder.py          # Chứa 5 thuật toán mã hóa AMO sang CNF (tự cài đặt)
│   ├── pysat_encoder.py    # Mã hóa AMO qua thư viện PySAT (pysat.card.CardEnc)
│   ├── solver.py           # Tích hợp PySAT (đa backend, alias CryptoMiniSAT5)
│   ├── cp_solver.py        # Tích hợp Google OR-Tools (CP-SAT)
│   ├── cplex_mip_solver.py # Tích hợp IBM CPLEX (MIP/ILP)
│   ├── cplex_cp_solver.py  # Tích hợp IBM CPLEX CP Optimizer (tự dò engine)
│   ├── gurobi_mip_solver.py # Tích hợp Gurobi (ILP)
│   ├── verify.py           # Bộ kiểm nghiệm nghiệm dùng chung cho mọi phương pháp
│   ├── verify_propagation.py # Kiểm chứng tính đúng AMO, ACUP và biến phụ của 5 encoding
│   ├── robustness.py       # Đo độ nhạy thời gian giải với hoán vị CNF
│   ├── noise_check.py      # Đo lặp CP-SAT, ghi thời gian từng lần chạy
│   ├── solver_stats.py     # Ghi số nút nhánh Gurobi và thời gian engine CPLEX CP
│   ├── plot_charts.py      # Vẽ toàn bộ biểu đồ từ CSV trong results/
│   ├── visualize.py        # In bàn cờ N-Queens trực quan ra terminal
│   └── benchmark.py        # Kịch bản chạy đo lường và vẽ biểu đồ tự động
├── results/            # Chứa file CSV và các biểu đồ PNG
│   ├── *.csv                 # Dữ liệu thực nghiệm thô (N=8..200, cross-solver, first-solution)
│   └── *.png                 # Biểu đồ số lượng mệnh đề và thời gian giải
├── tests/                    # Kiểm thử tự động (encoding & solvers)
├── report/
│   ├── main.tex              # Báo cáo học thuật LaTeX chuẩn Elsevier
│   └── main.pdf              # Báo cáo đã biên dịch
├── docs/
│   └── SETUP_CPLEX_CP.md     # Hướng dẫn cài engine CPLEX CP Optimizer
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

**Bước 2: Chạy thực nghiệm**

```bash
python src/benchmark.py
```

Kịch bản hỗ trợ tham số dòng lệnh để chạy chọn lọc:

| Tham số | Mặc định | Mô tả |
|---|---|---|
| `--sizes` | `10 15 20 25 30` | Các mốc $N$ cần chạy |
| `--methods` | cả 9 phương pháp | Các phương pháp cần chạy |
| `--repeats` | `3` | Số lần lặp mỗi cấu hình để lấy trung bình |
| `--timeout` | `100` | Giới hạn thời gian giải mỗi lần (giây) |
| `--solver` | `glucose3` | Bộ giải PySAT sử dụng |
| `--out` | `sat_vs_cp_benchmark.csv` | Tên file CSV đầu ra |
| `--no-append` | tắt | Ghi đè CSV thay vì ghép thêm dữ liệu cũ |
| `--first-solution` | tắt | Với CP/MIP: dừng ngay tại nghiệm khả thi đầu tiên |

**Đối chuẩn chéo nhiều bộ giải SAT:** dùng cú pháp `<solver>:<encoding>`, ví dụ:

```bash
python src/benchmark.py --sizes 30 --repeats 1 \
    --methods "glucose3:sequential" "cadical195:sequential" "cms:sequential" \
    --out cross_solver_benchmark.csv --no-append
```

**Thí nghiệm độ bền theo thứ tự đầu vào** (seed 0 = CNF gốc):

```bash
python src/robustness.py --sizes 30 50 100 --seeds 10 --timeout 60
```

**Kiểm thử và kiểm chứng encoding:**

```bash
python -m unittest discover -s tests -v
python src/verify_propagation.py
```

**Bước 3 (tùy chọn): Biên dịch báo cáo LaTeX**

Báo cáo dùng template Elsevier `cas-sc`, biên dịch bằng **XeLaTeX** hoặc **Tectonic**:

```bash
cd report
xelatex main.tex && xelatex main.tex   # chạy 2 lần để cập nhật tham chiếu chéo
# hoặc: tectonic -X compile report/main.tex --keep-logs
```

> 📖 Hướng dẫn cài engine CPLEX CP Optimizer: xem [`docs/SETUP_CPLEX_CP.md`](docs/SETUP_CPLEX_CP.md).

## 📚 Kết quả & Thảo luận

Toàn bộ số liệu thực nghiệm chi tiết, phân tích thắt cổ chai, đối chuẩn cross-solver và đánh giá tính công bằng được trình bày trong báo cáo khoa học:

- 📄 **[`report/main.pdf`](report/main.pdf)** — báo cáo đầy đủ (tiếng Anh, chuẩn Elsevier)
- 📊 **[`results/`](results/)** — dữ liệu thô (CSV) và biểu đồ (PNG)

## 📜 Giấy phép

Dự án phục vụ mục đích học thuật cho môn học.
