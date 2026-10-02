# Hướng dẫn cài đặt IBM ILOG CPLEX Optimization Studio (CP Optimizer)

Để chạy được thuật toán `CPLEX-CP` (IBM CP Optimizer) trong công cụ benchmark này, hệ thống cần file thực thi `cpoptimizer.exe` từ bản quyền của IBM. Gói `cplex` trên PyPI chỉ bao gồm thư viện MIP chứ không bao gồm CP Optimizer.

## Các bước cài đặt:

1. **Đăng nhập IBM SkillsBuild (Academic Initiative):**
   - Truy cập: https://academic.ibm.com/a2e/software
   - Sử dụng email sinh viên (ví dụ đuôi `.edu.vn`) để đăng ký và đăng nhập.

2. **Tải phần mềm:**
   - Tại thanh tìm kiếm, gõ **CPLEX**.
   - Chọn **ILOG CPLEX Optimization Studio**.
   - Tải xuống phiên bản dành cho **Windows** (dung lượng khoảng gần 1GB).

3. **Cài đặt:**
   - Chạy file vừa tải về và chọn Next theo cấu hình mặc định.
   - Khi hoàn tất, thư viện `docplex` trong mã nguồn sẽ **tự động dò tìm** được file thực thi tại `C:\Program Files\IBM\ILOG\...` nhờ hàm `_find_cpoptimizer()` đã được cài cắm sẵn.

4. **Kiểm tra chạy thử:**
   Sau khi cài đặt xong, bạn có thể kiểm tra xem hệ thống đã nhận diện được engine chưa bằng lệnh:
   ```bash
   python src/benchmark.py --sizes 8 --methods cplex-cp --repeats 1
   ```
   Nếu màn hình báo chạy thành công thay vì `MISSING_ENGINE`, chúc mừng bạn đã cấu hình xong!
