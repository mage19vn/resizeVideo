import customtkinter as ctk
from tkinter import filedialog
from tkinter.messagebox import showinfo, askyesno
import threading
from proglog import ProgressBarLogger
import random
import os
import sys
import subprocess
import json
import urllib.request
import zipfile
import tempfile
import shutil
from moviepy import VideoFileClip

# CẤU HÌNH PHIÊN BẢN (AUTO UPDATE)
CURRENT_VERSION = "v1.0.0"
REPO_URL = "https://api.github.com/repos/mage19vn/resizeVideo/releases/latest"

# ==========================================
# CẤU HÌNH GIAO DIỆN HIỆN ĐẠI
# ==========================================
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("green") # Sử dụng màu xanh làm màu chủ đạo (Accent color)

class MyTkLogger(ProgressBarLogger):
    def __init__(self, progress_bar, root):
        super().__init__()
        self.progress_bar = progress_bar
        self.root = root

    def bars_callback(self, bar, attr, value, old_value=None):
        total = self.bars[bar]['total']
        if total > 0:
            percent = value / total # CustomTkinter progress bar takes 0.0 to 1.0
            self.progress_bar.set(percent)
            self.root.update_idletasks()

class GUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title('ResizeVideo Pro (Modern UI)')
        self.geometry('750x650')
        self.resizable(False, False)
        
        # Set icon
        icon_path = os.path.join(os.path.dirname(__file__) if '__file__' in locals() else os.getcwd(), "app_icon.ico")
        if os.path.exists(icon_path):
            self.iconbitmap(icon_path)
            
        # --- Khởi tạo các biến mặc định ---
        self.fileNameInput = ''
        self.fileNameOutput = 'United'
        self.scaleOutput = (1920, 1080) # Default 1080p
        self.crfOutput = 28
        self.speedOutput = 1.0  
        self.vcodecOutput = "libx264"
        self.dot = '.mp4'
        self.original_duration = 0.0
        
        self.setup_ui()
        
        # Chạy kiểm tra version ngầm
        threading.Thread(target=self.check_for_updates, daemon=True).start()
        
    def setup_ui(self):
        # ==========================================
        # KHỐI HEADER
        # ==========================================
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", pady=(20, 10))
        
        ctk.CTkLabel(header_frame, text="RESIZE VIDEO PRO", font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"), text_color="#2fd09b").pack()
        
        version_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        version_frame.pack()
        
        ctk.CTkLabel(version_frame, text="Powered by Mage__", font=ctk.CTkFont(family="Segoe UI", size=12, slant="italic")).pack(side="left", padx=5)
        ctk.CTkLabel(version_frame, text=f"|  {CURRENT_VERSION}", font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold")).pack(side="left")
        
        self.btn_check_update = ctk.CTkButton(version_frame, text='🔄 Kiểm tra cập nhật', font=ctk.CTkFont(family="Segoe UI", size=12), 
                                              width=130, height=28, fg_color="transparent", border_width=1,
                                              command=self.manual_check_update)
        self.btn_check_update.pack(side="left", padx=15)

        self.btn_update = ctk.CTkButton(version_frame, text='🎁 Có bản mới! Cập nhật ngay', font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), 
                                        fg_color="#f39c12", hover_color="#d68910", text_color="#1e1e1e",
                                        command=self.prompt_update, height=28)
        # Nút này chỉ pack khi có update (ở hàm check_for_updates)

        # ==========================================
        # KHỐI CHÍNH (CHIA 2 CỘT: TRÁI - INPUT, PHẢI - SETTINGS)
        # ==========================================
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # --- CỘT TRÁI: ĐẦU VÀO (INPUT) ---
        left_frame = ctk.CTkFrame(main_frame, corner_radius=10)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        ctk.CTkLabel(left_frame, text="📥 Input Video", font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold")).pack(pady=(15, 5))

        self.choiceFileButton = ctk.CTkButton(left_frame, text='📂 Chọn File Video', font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"), 
                                              command=self.choiceFILE, height=40)
        self.choiceFileButton.pack(pady=15, padx=20, fill="x")

        self.labelTextinfomation = ctk.CTkLabel(left_frame, text="Chưa có file nào được chọn.", 
                                                font=ctk.CTkFont(family="Segoe UI", size=13), justify='left')
        self.labelTextinfomation.pack(anchor="w", padx=20, pady=5)

        # --- CỘT PHẢI: CẤU HÌNH (SETTINGS) ---
        right_frame = ctk.CTkFrame(main_frame, corner_radius=10)
        right_frame.grid(row=0, column=1, sticky="nsew")
        right_frame.columnconfigure(1, weight=1)
        
        ctk.CTkLabel(right_frame, text="⚙️ Output Settings", font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold")).grid(row=0, column=0, columnspan=2, pady=(15, 10))

        # Tên file xuất
        ctk.CTkLabel(right_frame, text="Tên file:", font=ctk.CTkFont(size=13)).grid(row=1, column=0, sticky="w", padx=20, pady=5)
        self.textBoxOutName = ctk.CTkEntry(right_frame, font=ctk.CTkFont(size=13))
        self.textBoxOutName.insert(0, self.fileNameOutput)
        self.textBoxOutName.grid(row=1, column=1, padx=(0, 20), pady=5, sticky="ew")

        # Định dạng (Format)
        self.LISTCANSAVE = [".mp4", ".avi", ".mov", ".mkv", ".gif"]
        ctk.CTkLabel(right_frame, text="Định dạng:", font=ctk.CTkFont(size=13)).grid(row=2, column=0, sticky="w", padx=20, pady=5)
        self.format_cb = ctk.CTkComboBox(right_frame, values=self.LISTCANSAVE, state="readonly", command=lambda e: [setattr(self, 'dot', e), self.update_estimate()])
        self.format_cb.set(self.dot)
        self.format_cb.grid(row=2, column=1, padx=(0, 20), pady=5, sticky="ew")

        # Độ phân giải (Scale)
        self.scale_map = {"2160p (4K)": (3840, 2160), "1440p (2K)": (2560, 1440), "1080p (FHD)": (1920, 1080), 
                          "720p (HD)": (1280, 720), "480p (SD)": (854, 480), "360p": (640, 360), "240p": (426, 240)}
        ctk.CTkLabel(right_frame, text="Độ phân giải:", font=ctk.CTkFont(size=13)).grid(row=3, column=0, sticky="w", padx=20, pady=5)
        self.scale_cb = ctk.CTkComboBox(right_frame, values=list(self.scale_map.keys()), state="readonly", command=lambda e: [setattr(self, 'scaleOutput', self.scale_map[e]), self.update_estimate()])
        self.scale_cb.set("1080p (FHD)")
        self.scale_cb.grid(row=3, column=1, padx=(0, 20), pady=5, sticky="ew")

        # CRF (Chất lượng)
        self.crf_map = {"18 (Chất lượng cao)": 18, "23 (Chất lượng TB)": 23, "28 (Chất lượng thấp)": 28}
        ctk.CTkLabel(right_frame, text="Chất lượng (CRF):", font=ctk.CTkFont(size=13)).grid(row=4, column=0, sticky="w", padx=20, pady=5)
        self.crf_cb = ctk.CTkComboBox(right_frame, values=list(self.crf_map.keys()), state="readonly", command=lambda e: [setattr(self, 'crfOutput', self.crf_map[e]), self.update_estimate()])
        self.crf_cb.set("28 (Chất lượng thấp)")
        self.crf_cb.grid(row=4, column=1, padx=(0, 20), pady=5, sticky="ew")

        # VCODEC
        self.codec_map = {
            "H.264 / AVC (Phổ biến nhất, khuyên dùng)": "libx264",
            "H.265 / HEVC (Nén cực tốt, file siêu nhẹ)": "libx265",
            "VP9 (Chuẩn YouTube, chất lượng cao)": "libvpx-vp9",
            "VP8 (Chuẩn WebM cơ bản)": "libvpx",
            "MPEG-4 (Định dạng cũ, nén kém)": "mpeg4"
        }
        ctk.CTkLabel(right_frame, text="Bộ mã hóa (Codec):", font=ctk.CTkFont(size=13)).grid(row=5, column=0, sticky="w", padx=20, pady=5)
        self.codec_cb = ctk.CTkComboBox(right_frame, values=list(self.codec_map.keys()), state="readonly", command=lambda e: [setattr(self, 'vcodecOutput', self.codec_map[e]), self.update_estimate()])
        self.codec_cb.set("H.264 / AVC (Phổ biến nhất, khuyên dùng)")
        self.codec_cb.grid(row=5, column=1, padx=(0, 20), pady=5, sticky="ew")
        
        # Speed 
        self.LISTSPEED = ["0.25", "0.5", "0.75", "1.0", "1.25", "1.5", "1.75", "2.0"]
        ctk.CTkLabel(right_frame, text="Tốc độ:", font=ctk.CTkFont(size=13)).grid(row=6, column=0, sticky="w", padx=20, pady=5)
        # CustomTkinter ko cho tự do gõ vào OptionMenu, nên ta dùng ComboBox
        self.speed_cb = ctk.CTkComboBox(right_frame, values=self.LISTSPEED, command=self.update_estimate)
        self.speed_cb.set(str(self.speedOutput))
        self.speed_cb.grid(row=6, column=1, padx=(0, 20), pady=5, sticky="ew")
        self.speed_cb.bind("<KeyRelease>", self.update_estimate)

        # Thời gian đích
        ctk.CTkLabel(right_frame, text="Thời gian đích (s):", font=ctk.CTkFont(size=13)).grid(row=7, column=0, sticky="w", padx=20, pady=5)
        self.targetTimeInput = ctk.CTkEntry(right_frame, font=ctk.CTkFont(size=13))
        self.targetTimeInput.grid(row=7, column=1, padx=(0, 20), pady=5, sticky="ew")
        self.targetTimeInput.bind("<KeyRelease>", self.update_estimate) 

        # Hiển thị dung lượng ước tính
        self.labelEstimate = ctk.CTkLabel(right_frame, text="Dung lượng ước tính: ~ MB", font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"))
        self.labelEstimate.grid(row=8, column=0, columnspan=2, pady=15)

        # ==========================================
        # KHỐI BOTTOM (RENDER & TIẾN TRÌNH)
        # ==========================================
        bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        bottom_frame.pack(fill="x", padx=20, pady=20)

        self.saveFileButton = ctk.CTkButton(bottom_frame, text='🚀 XUẤT VIDEO (RENDER)', font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"), 
                                            command=self.saveFILE, height=50)
        self.saveFileButton.pack(fill="x", pady=(0, 15))

        self.progressBar = ctk.CTkProgressBar(bottom_frame, height=15)
        self.progressBar.set(0)
        self.progressBar.pack(fill="x", pady=5)
        
        self.labelTextinfomation2 = ctk.CTkLabel(bottom_frame, text="", text_color="#2fd09b", font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"))
        self.labelTextinfomation2.pack()

    # ==========================================
    # KHỐI AUTO UPDATE (ZIP MODE)
    # ==========================================
    def manual_check_update(self):
        self.btn_check_update.configure(state="disabled", text="⏳ Đang kiểm tra...")
        threading.Thread(target=self.check_for_updates, args=(True,), daemon=True).start()

    def check_for_updates(self, manual=False):
        try:
            req = urllib.request.Request(REPO_URL, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                
            latest_version = data.get("tag_name", "")
            
            if latest_version and latest_version != CURRENT_VERSION:
                self.latest_version_data = data
                def show_update_btn():
                    self.btn_check_update.pack_forget()
                    self.btn_update.pack(side="left", padx=15)
                self.after(0, show_update_btn)
                if manual:
                    self.after(0, self.prompt_update)
            else:
                if manual:
                    self.after(0, lambda: showinfo("Cập nhật", "Bạn đang sử dụng phiên bản mới nhất!"))
                    self.after(0, lambda: self.btn_check_update.configure(state="normal", text="🔄 Kiểm tra cập nhật"))
        except Exception as e:
            if manual:
                self.after(0, lambda: showinfo("Lỗi", f"Không thể kiểm tra cập nhật: {e}"))
                self.after(0, lambda: self.btn_check_update.configure(state="normal", text="🔄 Kiểm tra cập nhật"))

    def prompt_update(self):
        latest_version = self.latest_version_data.get("tag_name", "")
        body = self.latest_version_data.get("body", "Không có mô tả chi tiết.")
        
        msg = f"Đã có phiên bản mới {latest_version}!\n\nNội dung cập nhật:\n{body}\n\nBạn có muốn tải và cài đặt ngay không?"
        if askyesno("Cập nhật phần mềm", msg):
            self.download_and_update()

    def download_and_update(self):
        assets = self.latest_version_data.get("assets", [])
        if not assets:
            showinfo("Lỗi", "Không tìm thấy file cài đặt trên GitHub Releases!")
            return
            
        download_url = None
        for asset in assets:
            if asset.get("name", "").endswith(".zip"):
                download_url = asset.get("browser_download_url")
                break
                
        if not download_url:
            showinfo("Lỗi", "Không tìm thấy file .zip phù hợp trên GitHub Releases!\nHãy đảm bảo bản release đã tải lên file ZIP.")
            return
            
        self.progressBar.set(0)
        self.labelTextinfomation2.configure(text=f"⏳ Đang tải bản cập nhật... Vui lòng không đóng app!")
        
        self.btn_update.pack_forget()
        self.saveFileButton.configure(state="disabled")
        self.choiceFileButton.configure(state="disabled")
        
        def download_thread():
            try:
                temp_dir = tempfile.gettempdir()
                zip_path = os.path.join(temp_dir, "ResizeVideo_Update.zip")
                extract_dir = os.path.join(temp_dir, "ResizeVideo_Update_Extracted")
                
                # Tải file zip
                req = urllib.request.Request(download_url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=15) as response, open(zip_path, 'wb') as out_file:
                    total_length = response.getheader('content-length')
                    
                    if total_length is None:
                        out_file.write(response.read())
                    else:
                        total_length = int(total_length)
                        downloaded = 0
                        chunk_size = 4096
                        while True:
                            data = response.read(chunk_size)
                            if not data:
                                break
                            downloaded += len(data)
                            out_file.write(data)
                            percent = downloaded / total_length
                            self.after(0, lambda p=percent: self.progressBar.set(p))
                
                self.after(0, lambda: self.labelTextinfomation2.configure(text="⏳ Đang giải nén file..."))
                
                # Giải nén
                if os.path.exists(extract_dir):
                    shutil.rmtree(extract_dir)
                os.makedirs(extract_dir)
                
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)
                
                self.after(0, lambda: self.labelTextinfomation2.configure(text="✅ Giải nén xong! Đang cài đặt..."))
                self.install_update(extract_dir)
                
            except Exception as e:
                self.after(0, lambda err=e: showinfo("Lỗi cập nhật", f"Lỗi: {err}"))
                self.after(0, lambda: self.labelTextinfomation2.configure(text="❌ Tải cập nhật thất bại!", text_color="red"))
                self.after(0, lambda: self.saveFileButton.configure(state="normal"))
                self.after(0, lambda: self.choiceFileButton.configure(state="normal"))
                
        threading.Thread(target=download_thread, daemon=True).start()

    def install_update(self, extract_dir):
        current_exe = sys.executable 
        
        if not current_exe.endswith(".exe") or "python" in current_exe.lower():
            self.after(0, lambda: showinfo("Môi trường Dev", "Đang chạy mã nguồn Python, không phải file .exe. Bỏ qua cập nhật thư mục."))
            self.after(0, lambda: self.saveFileButton.configure(state="normal"))
            self.after(0, lambda: self.choiceFileButton.configure(state="normal"))
            self.after(0, lambda: self.labelTextinfomation2.configure(text=""))
            return
            
        current_dir = os.path.dirname(current_exe)
        bat_path = os.path.join(current_dir, "update_script.bat")
        
        # Batch script để copy đè file từ thư mục giải nén sang thư mục app hiện tại, sau đó chạy lại exe
        bat_content = f'''@echo off
echo Dang cap nhat ResizeVideo Pro... Vui long doi giay lat...
timeout /t 3 /nobreak > NUL
xcopy /E /Y /C "{extract_dir}\\*" "{current_dir}\\"
start "" "{current_exe}"
del "%~f0"
'''
        with open(bat_path, "w", encoding="utf-8") as f:
            f.write(bat_content)
            
        subprocess.Popen(bat_path, shell=True, creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0)
        self.after(100, sys.exit)

    # ==========================================
    # CÁC HÀM XỬ LÝ CHÍNH
    # ==========================================
    def choiceFILE(self):
        self.fileNameInput = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4;*.avi;*.mov;*.mkv;*.gif")])
        if not self.fileNameInput:
            return
            
        filename = self.fileNameInput.split("/")[-1]
        try:
            file_size_bytes = os.path.getsize(self.fileNameInput)
            file_size_mb = round(file_size_bytes / (1024 * 1024), 2)
            
            clip = VideoFileClip(self.fileNameInput)
            self.original_duration = clip.duration
            
            info_text = f"🎥 File: {filename}\n\n⏱️ Time: {round(clip.duration, 2)} s\n\n📐 Kích thước: {clip.size[0]} x {clip.size[1]}\n\n🎞️ FPS: {round(clip.fps, 2)}\n\n💾 Dung lượng gốc: {file_size_mb} MB"
            self.labelTextinfomation.configure(text=info_text)
            
            self.targetTimeInput.delete(0, 'end')
            self.targetTimeInput.insert(0, str(round(self.original_duration, 2)))
            self.update_estimate()
            
            clip.close()
        except Exception as e:
            showinfo(title="Lỗi", message=f"Không thể đọc file: {e}")
    
    def randomS(self):
        r = ''
        for i in range(10):
            r += random.choice('qwertyuiopasdfghjklzxcvbnm1234567890')
        return r   
    
    def update_estimate(self, event=None):
        if self.original_duration == 0:
            return
            
        try:
            if event and hasattr(event, "widget") and event.widget == self.targetTimeInput:
                target_time = float(self.targetTimeInput.get())
                if target_time > 0:
                    self.speedOutput = round(self.original_duration / target_time, 2)
                    self.speed_cb.set(str(self.speedOutput))
            else:
                self.speedOutput = float(self.speed_cb.get())
                target_time = round(self.original_duration / self.speedOutput, 2)
                self.targetTimeInput.delete(0, 'end')
                self.targetTimeInput.insert(0, str(target_time))
                
            width = self.scaleOutput[0] if isinstance(self.scaleOutput, tuple) else 1920
            if width >= 3840: scale_mult = 3.5
            elif width >= 2560: scale_mult = 1.8
            elif width >= 1920: scale_mult = 1.0
            elif width >= 1280: scale_mult = 0.5
            elif width >= 854: scale_mult = 0.25
            else: scale_mult = 0.15
            
            crf = getattr(self, 'crfOutput', 28)
            if crf <= 18: crf_mult = 1.6
            elif crf <= 23: crf_mult = 1.0
            else: crf_mult = 0.6

            codec = getattr(self, 'vcodecOutput', 'libx264')
            if codec == "libx265": codec_mult = 0.5
            elif codec == "libvpx-vp9": codec_mult = 0.6
            elif codec == "libvpx": codec_mult = 1.2
            elif codec == "mpeg4": codec_mult = 1.5
            else: codec_mult = 1.0

            fmt = getattr(self, 'dot', '.mp4').lower()
            if fmt == ".gif":
                format_mult = 4.5
            else:
                format_mult = 1.0

            mb_per_second = 0.3 * scale_mult * crf_mult * codec_mult * format_mult
            estimated_mb = target_time * mb_per_second
            self.labelEstimate.configure(text=f"Dung lượng ước tính: ~ {round(estimated_mb, 2)} MB")
            
        except ValueError:
            pass
    
    def apply_resize(self, clip, scale_val):
        if isinstance(scale_val, tuple):
            return clip.resized(width=scale_val[0], height=scale_val[1])
        return clip.resized(scale_val)
        
    def saveFILE(self):
        if not self.fileNameInput:
            showinfo(title="Cảnh báo", message="Vui lòng chọn file video đầu vào trước!")
            return

        readentry = self.textBoxOutName.get().strip()
        self.fileNameOutput = readentry if len(readentry) > 0 else f'United_{self.randomS()}'
        
        folder = filedialog.askdirectory(title="Chọn thư mục lưu file")
        if not folder:
            return
            
        self.choiceFileButton.configure(state="disabled")
        self.saveFileButton.configure(state="disabled")
        self.textBoxOutName.configure(state="disabled")
        self.format_cb.configure(state="disabled")
        self.scale_cb.configure(state="disabled")
        self.crf_cb.configure(state="disabled")
        self.codec_cb.configure(state="disabled")
        self.speed_cb.configure(state="disabled")
        
        self.progressBar.set(0)
        self.labelTextinfomation2.configure(text="⏳ Đang xử lý... Vui lòng đợi!", text_color="#f39c12")
        self.update() 
        
        def render_thread():
            try:
                clip = VideoFileClip(self.fileNameInput)
                clip = self.apply_resize(clip, self.scaleOutput)
                    
                if self.speedOutput != 1.0:
                    clip = clip.with_speed_scaled(self.speedOutput)
                
                output_path = f"{folder}/{self.fileNameOutput}{self.dot}"
                my_logger = MyTkLogger(self.progressBar, self)
                
                if self.dot.lower() == '.gif':
                    clip.write_gif(output_path, fps=15, logger=my_logger)
                else:
                    clip.write_videofile(
                        output_path,
                        codec=self.vcodecOutput,
                        bitrate='800k',
                        preset='fast',
                        ffmpeg_params=['-crf', str(self.crfOutput)],
                        logger=my_logger
                    )
                
                out_info = f'✅ ĐÃ XUẤT THÀNH CÔNG: {self.fileNameOutput}{self.dot} | Time: {round(clip.duration, 2)}s | Size: {clip.size[0]}x{clip.size[1]}'
                self.after(0, lambda: self.labelTextinfomation2.configure(text=out_info, text_color="#2fd09b"))
                clip.close()
                
                self.after(0, lambda: showinfo(title="Hoàn tất", message="Đã xuất video thành công!"))
                
            except Exception as e:
                self.after(0, lambda err=e: showinfo(title="Lỗi xử lý", message=f"Đã có lỗi:\n{err}"))
                self.after(0, lambda: self.labelTextinfomation2.configure(text="❌ Xuất file thất bại!", text_color="red"))
            finally:
                def reset_ui():
                    self.choiceFileButton.configure(state="normal")
                    self.saveFileButton.configure(state="normal")
                    self.textBoxOutName.configure(state="normal")
                    self.format_cb.configure(state="normal")
                    self.scale_cb.configure(state="normal")
                    self.crf_cb.configure(state="normal")
                    self.codec_cb.configure(state="normal")
                    self.speed_cb.configure(state="normal")
                    self.progressBar.set(0)
                
                self.after(0, reset_ui)

        threading.Thread(target=render_thread, daemon=True).start()

if __name__ == "__main__":
    app = GUI()
    app.mainloop()