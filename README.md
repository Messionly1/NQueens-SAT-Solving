# N-Queens SAT Project

Dự án Giải quyết bài toán N-Queens bằng phương pháp Quy về bài toán Thỏa mãn logic (SAT). Dự án này sử dụng thư viện `python-sat` để mã hóa và tìm nghiệm.

## Cấu trúc thư mục

*   `src/`: Chứa toàn bộ mã nguồn Python.
    *   `encoder.py`: Chứa class `NQueensEncoder` chuyển đổi luật chơi N-Queens thành các mệnh đề logic (CNF).
    *   `solver.py`: Wrapper xử lý giao tiếp với các bộ giải (Solver) như Glucose3, Cadical.
    *   `benchmark.py`: Tập lệnh tự động kiểm thử với các kích thước $N$ khác nhau và xuất kết quả.
*   `results/`: Thư mục lưu trữ kết quả benchmark dưới dạng CSV.
*   `report/`: Nơi lưu trữ mã nguồn LaTeX và file báo cáo bài tập lớn.

## Hướng dẫn cài đặt

1.  Tạo và kích hoạt môi trường ảo (khuyến nghị Python 3.12):
    ```bash
    py -3.12 -m venv venv
    .\venv\Scripts\activate
    ```
2.  Cài đặt các thư viện cần thiết:
    ```bash
    pip install -r requirements.txt
    ```

## Chạy Benchmark

Để chạy quá trình thực nghiệm, từ thư mục gốc hãy gõ lệnh:
```bash
python src/benchmark.py
```
Kết quả sẽ được tự động lưu vào file `results/sat_benchmark_results.csv`.
