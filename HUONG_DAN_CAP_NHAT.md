# HƯỚNG DẪN PHÁT HÀNH BẢN CẬP NHẬT TỰ ĐỘNG

Tài liệu này hướng dẫn cách bạn tung ra một phiên bản `ResizeVideo Pro` mới để tất cả người dùng hiện tại có thể tự động cập nhật phần mềm của họ thông qua GitHub.

## Các bước thực hiện (Mỗi khi có bản code mới)

### Bước 1: Cập nhật mã nguồn & Đóng gói (Làm trên máy của bạn)
1. Mở file `main.py` bằng trình soạn thảo code (VSCode/Sublime).
2. Tìm dòng số 16: `CURRENT_VERSION = "v1.0.0"`.
3. Sửa thông số này thành phiên bản mới tương ứng.
   * *Ví dụ: Nếu bản cũ là `v1.0.0`, bạn có thể nâng lên `v1.0.1` hoặc `v1.1.0`.*
4. Chạy lệnh đóng gói ứng dụng qua Terminal/CMD:
   ```cmd
   pyinstaller main.spec
   ```
5. Đợi quá trình hoàn tất, bạn vào thư mục `dist` sẽ thấy file `main.exe` mới vừa được tạo ra.
6. (Tùy chọn) Đổi tên file `main.exe` này thành `ResizeVideo.exe` cho chuyên nghiệp.

### Bước 2: Đẩy bản cập nhật lên GitHub
1. Truy cập vào kho lưu trữ mã nguồn của bạn: [https://github.com/mage19vn/resizeVideo](https://github.com/mage19vn/resizeVideo)
2. Ở cột bên phải màn hình, click vào mục **Releases** -> Chọn **Draft a new release**.
3. Tại ô **Choose a tag** (Rất quan trọng): Bạn phải gõ **chính xác** cái tên phiên bản bạn vừa cấu hình ở Bước 1. 
   * *Ví dụ: `v1.0.1`*
4. Ghi tiêu đề (Release title) và mô tả cập nhật (Describe this release) để thông báo cho người dùng biết bản mới có tính năng gì.
5. Tại khu vực **Attach binaries by dropping them here** (Assets), hãy kéo và thả file `.exe` vừa đóng gói ở bước trên vào đây.
6. Đợi file tải lên xong 100%, nhấn nút màu xanh lá **Publish release**.

---

## 🎉 Hoàn tất!
Ngay khi bạn nhấn Publish trên GitHub, tất cả những người dùng đang chạy bản cũ sẽ ngay lập tức nhìn thấy nút **"🎁 Cập nhật bản mới"** màu cam hiện lên trên góc ứng dụng của họ.

Họ chỉ cần bấm vào nút đó, ứng dụng sẽ tự động tải file `.exe` mới từ GitHub về và âm thầm ghi đè thay thế cho bản cũ. Khách hàng không cần phải tự tải file hay cài đặt bằng tay nữa!
