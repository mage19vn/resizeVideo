# 🚀 HƯỚNG DẪN PHÁT HÀNH BẢN CẬP NHẬT TỰ ĐỘNG

> [!NOTE]
> Tài liệu này hướng dẫn cách bạn tung ra một phiên bản **ResizeVideo Pro** mới để tất cả người dùng hiện tại có thể tự động cập nhật phần mềm thông qua GitHub Releases.

---

## 🛠️ Bước 1: Cập nhật Code & Đóng gói (Trên máy tính của bạn)

1. Mở file `main.py` bằng trình soạn thảo (VSCode/Sublime...).
2. Tìm dòng số 16: `CURRENT_VERSION = "v1.0.0"`.
3. Sửa thông số này thành phiên bản mới tương ứng.
   > **Ví dụ:** Nâng cấp từ `v1.0.0` lên `v1.0.1` hoặc `v1.1.0`

4. Mở Terminal/CMD và chạy lệnh đóng gói ứng dụng:
   ```cmd
   pyinstaller main.spec
   ```
5. Đợi quá trình hoàn tất, bạn vào thư mục `dist` sẽ thấy file `main.exe` mới vừa được tạo ra.
6. *(Tùy chọn)* Đổi tên file `main.exe` này thành `ResizeVideo.exe` cho đẹp và chuyên nghiệp hơn.

---

## ☁️ Bước 2: Đẩy bản cập nhật lên GitHub (Phát hành)

1. Truy cập vào kho lưu trữ của bạn: [https://github.com/mage19vn/resizeVideo](https://github.com/mage19vn/resizeVideo)
2. Nhìn sang cột bên phải màn hình, click vào mục **Releases** -> Chọn **Draft a new release**.

> [!IMPORTANT]
> Tại ô **Choose a tag**, bạn **PHẢI** gõ **chính xác** cái tên phiên bản bạn vừa thiết lập ở Bước 1 (Ví dụ: `v1.0.1`). Nếu gõ sai, tính năng cập nhật sẽ không hoạt động.

3. Điền **Tiêu đề (Release title)** và **Mô tả (Describe this release)** để thông báo cho người dùng biết bản mới có tính năng gì nổi bật.
4. Tại khu vực **Attach binaries by dropping them here (Assets)**, hãy kéo và thả file `.exe` (đã đóng gói ở Bước 1) vào.
5. Đợi file tải lên xong 100%, nhấn nút màu xanh lá **Publish release**.

---

## 🎉 HOÀN TẤT!

> [!TIP]
> Ngay khi bạn nhấn Publish trên GitHub, những người dùng đang mở bản cũ sẽ lập tức thấy nút **"🎁 Cập nhật bản mới"** (màu cam) tự động hiện lên trên góc ứng dụng.
> 
> Họ chỉ cần click chuột, app sẽ tự tải file `.exe` mới từ GitHub về và âm thầm thay thế cho bản cũ một cách hoàn toàn tự động!
