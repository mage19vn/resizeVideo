import os
import shutil
import subprocess
import sys
import zipfile

def build():
    print("Bat dau qua trinh dong goi ResizeVideo Pro...")
    
    # 1. Chạy PyInstaller
    # Đóng gói dạng thư mục (onedir), ẩn console (--noconsole), gán icon
    pyinstaller_cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=ResizeVideo",
        "--noconsole",
        "--icon=app_icon.ico",
        "--noconfirm", # Ghi đè thư mục cũ
        "main.py"
    ]
    
    print("Dang chay PyInstaller...")
    subprocess.run(pyinstaller_cmd, check=True)
    
    # 2. Tạo file ZIP từ thư mục dist/ResizeVideo
    dist_dir = os.path.join("dist", "ResizeVideo")
    zip_path = os.path.join("dist", "ResizeVideo_Release.zip")
    
    if os.path.exists(zip_path):
        os.remove(zip_path)
        
    print(f"Dang nen thu muc thanh {zip_path}...")
    
    # Nén toàn bộ thư mục ResizeVideo
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(dist_dir):
            for file in files:
                file_path = os.path.join(root, file)
                # Đường dẫn tương đối bên trong file zip (để khi giải nén ra sẽ nằm trong thư mục gốc hoặc theo đúng cấu trúc)
                # Ở đây ta nén các file BÊN TRONG thư mục ResizeVideo chứ không phải nén thư mục ResizeVideo
                arcname = os.path.relpath(file_path, dist_dir)
                zipf.write(file_path, arcname)
                
    print("HOAN TAT! File cap nhat cua ban la:", zip_path)
    print("Hay upload file nay len GitHub Releases de tu dong cap nhat cho nguoi dung.")

if __name__ == "__main__":
    build()
