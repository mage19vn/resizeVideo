from tkinter import *
from tkinter import filedialog
from tkinter.messagebox import showinfo, askyesno
from tkinter import ttk
import threading
from proglog import ProgressBarLogger
import random
import os
import sys
import subprocess
import json
import urllib.request
import urllib.error

# CẤU HÌNH PHIÊN BẢN (AUTO UPDATE)
CURRENT_VERSION = "v1.0.0"
REPO_URL = "https://api.github.com/repos/mage19vn/resizeVideo/releases/latest"

# Import MoviePy
from moviepy import VideoFileClip

# ==========================================
# CẤU HÌNH MÀU SẮC GIAO DIỆN (DARK THEME)
# ==========================================
BG_COLOR = "#1e1e1e"
FRAME_BG = "#2d2d2d"
TEXT_COLOR = "#ffffff"
SUB_TEXT = "#b3b3b3"
ACCENT_COLOR = "#2fd09b" # Màu xanh nguyên bản của bạn
ENTRY_BG = "#3c3f41"

class MyTkLogger(ProgressBarLogger):
    def __init__(self, progress_bar, root):
        super().__init__()
        self.progress_bar = progress_bar
        self.root = root

    def bars_callback(self, bar, attr, value, old_value=None):
        total = self.bars[bar]['total']
        if total > 0:
            percent = (value / total) * 100
            self.progress_bar['value'] = percent
            self.root.update_idletasks()

class GUI:
    def __init__(self, master):
        self.master = master
        
        # --- Khởi tạo các biến mặc định ---
        self.fileNameInput = ''
        self.fileNameOutput = 'United'
        self.scaleOutput = 0.5  
        self.crfOutput = 28
        self.speedOutput = 1.0  
        self.vcodecOutput = "libx264"
        self.dot = '.mp4'

        # ==========================================
        # SETUP STYLE CHO TTK (Làm đẹp Combobox, Progressbar)
        # ==========================================
        style = ttk.Style()
        style.theme_use('clam')
        
        # 1. Cấu hình màu thanh tiến trình
        style.configure("Horizontal.TProgressbar", troughcolor=ENTRY_BG, bordercolor=BG_COLOR, background=ACCENT_COLOR, thickness=15)

        # 2. Cấu hình màu cho ô Combobox đang hiển thị
        style.configure("TCombobox", fieldbackground=ENTRY_BG, background=FRAME_BG, foreground=TEXT_COLOR, borderwidth=0)
        
        # BẮT BUỘC: Ép màu chữ trắng sáng (TEXT_COLOR) khi ở trạng thái readonly
        style.map('TCombobox', 
                  fieldbackground=[('readonly', ENTRY_BG)], 
                  foreground=[('readonly', TEXT_COLOR)], # Giữ chữ màu trắng sáng
                  selectbackground=[('readonly', ACCENT_COLOR)], # Đổi màu nền khi bôi đen
                  selectforeground=[('readonly', BG_COLOR)])     # Đổi màu chữ khi bôi đen
        
        # 3. Cấu hình màu cho Danh sách xổ xuống (Popdown Listbox)
        self.master.option_add('*TCombobox*Listbox.background', ENTRY_BG)
        self.master.option_add('*TCombobox*Listbox.foreground', TEXT_COLOR)
        self.master.option_add('*TCombobox*Listbox.selectBackground', ACCENT_COLOR)
        self.master.option_add('*TCombobox*Listbox.selectForeground', BG_COLOR)
        self.master.option_add('*TCombobox*Listbox.font', ('Segoe UI', 10))
        
        # ==========================================
        # KHỐI HEADER
        # ==========================================
        header_frame = Frame(self.master, bg=BG_COLOR)
        header_frame.pack(fill=X, pady=(15, 5))
        
        Label(header_frame, text="RESIZE VIDEO PRO", font=('Segoe UI', 20, 'bold'), bg=BG_COLOR, fg=ACCENT_COLOR).pack()
        
        version_frame = Frame(header_frame, bg=BG_COLOR)
        version_frame.pack()
        
        Label(version_frame, text="Powered by Mage__", font=('Segoe UI', 10, 'italic'), bg=BG_COLOR, fg=SUB_TEXT).pack(side=LEFT, padx=5)
        Label(version_frame, text=f"|  {CURRENT_VERSION}", font=('Segoe UI', 10, 'bold'), bg=BG_COLOR, fg=SUB_TEXT).pack(side=LEFT)
        
        self.btn_update = Button(version_frame, text='🎁 Cập nhật bản mới', font=('Segoe UI', 9, 'bold'), 
                                 fg=BG_COLOR, bg="#f39c12", activebackground="#d68910", 
                                 relief=FLAT, cursor="hand2", command=self.prompt_update)
        
        # Chạy kiểm tra version ngầm
        threading.Thread(target=self.check_for_updates, daemon=True).start()
        
        # Khoảng trống dưới header
        Frame(self.master, bg=BG_COLOR, height=10).pack()

        # ==========================================
        # KHỐI CHÍNH (CHIA 2 CỘT: TRÁI - INPUT, PHẢI - SETTINGS)
        # ==========================================
        main_frame = Frame(self.master, bg=BG_COLOR)
        main_frame.pack(fill=BOTH, expand=True, padx=20)

        # --- CỘT TRÁI: ĐẦU VÀO (INPUT) ---
        left_frame = LabelFrame(main_frame, text=" 📥 Input Video ", font=('Segoe UI', 11, 'bold'), bg=FRAME_BG, fg=TEXT_COLOR, bd=1, padx=15, pady=15)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        self.choiceFileButton = Button(left_frame, text='📂 Chọn File Video', font=('Segoe UI', 11, 'bold'), 
                                       fg=BG_COLOR, bg=ACCENT_COLOR, activebackground="#25a87c", 
                                       relief=FLAT, cursor="hand2", command=self.choiceFILE, width=25)
        self.choiceFileButton.pack(pady=(0, 15))

        self.labelTextinfomation = Label(left_frame, text="Chưa có file nào được chọn.", 
                                         bg=FRAME_BG, fg=SUB_TEXT, font=('Segoe UI', 10), justify='left')
        self.labelTextinfomation.pack(anchor="w")

        # --- CỘT PHẢI: CẤU HÌNH (SETTINGS) ---
        right_frame = LabelFrame(main_frame, text=" ⚙️ Output Settings ", font=('Segoe UI', 11, 'bold'), bg=FRAME_BG, fg=TEXT_COLOR, bd=1, padx=15, pady=10)
        right_frame.grid(row=0, column=1, sticky="nsew")

        # Tên file xuất
        Label(right_frame, text="Tên file:", bg=FRAME_BG, fg=TEXT_COLOR, font=('Segoe UI', 10)).grid(row=0, column=0, sticky="w", pady=5)
        self.textBoxOutName = Entry(right_frame, bg=ENTRY_BG, fg=TEXT_COLOR, insertbackground=TEXT_COLOR, relief=FLAT, font=('Segoe UI', 10), width=22)
        self.textBoxOutName.insert(0, self.fileNameOutput)
        self.textBoxOutName.grid(row=0, column=1, pady=5, padx=5)

        # Định dạng (Format)
        self.LISTCANSAVE = [".mp4", ".avi", ".mov", ".mkv", ".gif"]
        Label(right_frame, text="Định dạng:", bg=FRAME_BG, fg=TEXT_COLOR, font=('Segoe UI', 10)).grid(row=1, column=0, sticky="w", pady=5)
        self.format_cb = ttk.Combobox(right_frame, values=self.LISTCANSAVE, state="readonly", width=20)
        self.format_cb.set(self.dot)
        self.format_cb.grid(row=1, column=1, pady=5, padx=5)
        self.format_cb.bind("<<ComboboxSelected>>", lambda e: [setattr(self, 'dot', self.format_cb.get()), self.update_estimate()])

        # Độ phân giải (Scale)
        self.scale_map = {"2160p (4K)": (3840, 2160), "1440p (2K)": (2560, 1440), "1080p (FHD)": (1920, 1080), 
                          "720p (HD)": (1280, 720), "480p (SD)": (854, 480), "360p": (640, 360), "240p": (426, 240)}
        Label(right_frame, text="Độ phân giải:", bg=FRAME_BG, fg=TEXT_COLOR, font=('Segoe UI', 10)).grid(row=2, column=0, sticky="w", pady=5)
        self.scale_cb = ttk.Combobox(right_frame, values=list(self.scale_map.keys()), state="readonly", width=20)
        self.scale_cb.set("1080p (FHD)") # Mặc định
        self.scaleOutput = self.scale_map["1080p (FHD)"]
        self.scale_cb.grid(row=2, column=1, pady=5, padx=5)
        self.scale_cb.bind("<<ComboboxSelected>>", lambda e: [setattr(self, 'scaleOutput', self.scale_map[self.scale_cb.get()]), self.update_estimate()])

        # CRF (Chất lượng)
        self.crf_map = {"18 (Chất lượng cao)": 18, "23 (Chất lượng TB)": 23, "28 (Chất lượng thấp)": 28}
        Label(right_frame, text="Chất lượng (CRF):", bg=FRAME_BG, fg=TEXT_COLOR, font=('Segoe UI', 10)).grid(row=3, column=0, sticky="w", pady=5)
        self.crf_cb = ttk.Combobox(right_frame, values=list(self.crf_map.keys()), state="readonly", width=20)
        self.crf_cb.set("28 (Chất lượng thấp)")
        self.crf_cb.grid(row=3, column=1, pady=5, padx=5)
        self.crf_cb.bind("<<ComboboxSelected>>", lambda e: [setattr(self, 'crfOutput', self.crf_map[self.crf_cb.get()]), self.update_estimate()])

        # VCODEC (Đã đổi tên hiển thị thân thiện với người dùng)
        self.codec_map = {
            "H.264 / AVC (Phổ biến nhất, khuyên dùng)": "libx264",
            "H.265 / HEVC (Nén cực tốt, file siêu nhẹ)": "libx265",
            "VP9 (Chuẩn YouTube, chất lượng cao)": "libvpx-vp9",
            "VP8 (Chuẩn WebM cơ bản)": "libvpx",
            "MPEG-4 (Định dạng cũ, nén kém)": "mpeg4"
        }
        Label(right_frame, text="Bộ mã hóa (Codec):", bg=FRAME_BG, fg=TEXT_COLOR, font=('Segoe UI', 10)).grid(row=4, column=0, sticky="w", pady=5)
        
        # Tăng width lên 28 để chữ không bị che khuất
        self.codec_cb = ttk.Combobox(right_frame, values=list(self.codec_map.keys()), state="readonly", width=28) 
        self.codec_cb.set("H.264 / AVC (Phổ biến nhất, khuyên dùng)") # Mặc định
        self.vcodecOutput = self.codec_map["H.264 / AVC (Phổ biến nhất, khuyên dùng)"]
        
        self.codec_cb.grid(row=4, column=1, pady=5, padx=5)
        # Khi chọn tên thân thiện -> Tự động lưu mã kỹ thuật ngầm và tính lại dung lượng
        self.codec_cb.bind("<<ComboboxSelected>>", lambda e: [setattr(self, 'vcodecOutput', self.codec_map[self.codec_cb.get()]), self.update_estimate()])
        
        # Speed (Sửa lại bind sự kiện)
        self.LISTSPEED = [0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0]
        Label(right_frame, text="Tốc độ:", bg=FRAME_BG, fg=TEXT_COLOR, font=('Segoe UI', 10)).grid(row=5, column=0, sticky="w", pady=5)
        self.speed_cb = ttk.Combobox(right_frame, values=[str(x) for x in self.LISTSPEED], width=20)
        self.speed_cb.set(str(self.speedOutput))
        self.speed_cb.grid(row=5, column=1, pady=5, padx=5)
        self.speed_cb.bind("<<ComboboxSelected>>", self.update_estimate)
        self.speed_cb.bind("<KeyRelease>", self.update_estimate) # Cho phép gõ số lẻ thủ công

        # THÊM MỚI: Nhập thời gian đích (Tự động tính tốc độ)
        Label(right_frame, text="Thời gian đích (s):", bg=FRAME_BG, fg=TEXT_COLOR, font=('Segoe UI', 10)).grid(row=6, column=0, sticky="w", pady=5)
        self.targetTimeInput = Entry(right_frame, bg=ENTRY_BG, fg=TEXT_COLOR, insertbackground=TEXT_COLOR, relief=FLAT, font=('Segoe UI', 10), width=22)
        self.targetTimeInput.grid(row=6, column=1, pady=5, padx=5)
        self.targetTimeInput.bind("<KeyRelease>", self.update_estimate) 

        # THÊM MỚI: Hiển thị dung lượng ước tính
        self.labelEstimate = Label(right_frame, text="Dung lượng ước tính: ~ MB", bg=FRAME_BG, fg="#f39c12", font=('Segoe UI', 10, 'bold'))
        self.labelEstimate.grid(row=7, column=0, columnspan=2, pady=10)
        
        # Biến lưu trữ thời lượng gốc
        self.original_duration = 0.0

        # ==========================================
        # KHỐI BOTTOM (RENDER & TIẾN TRÌNH)
        # ==========================================
        bottom_frame = Frame(self.master, bg=BG_COLOR)
        bottom_frame.pack(fill=X, padx=20, pady=20)

        self.saveFileButton = Button(bottom_frame, text='🚀 XUẤT VIDEO (RENDER)', font=('Segoe UI', 12, 'bold'), 
                                     fg=BG_COLOR, bg=ACCENT_COLOR, activebackground="#25a87c", 
                                     relief=FLAT, cursor="hand2", command=self.saveFILE)
        self.saveFileButton.pack(fill=X, pady=(0, 15))

        self.progressBar = ttk.Progressbar(bottom_frame, orient=HORIZONTAL, mode='determinate', style="Horizontal.TProgressbar")
        self.progressBar.pack(fill=X, pady=5)
        
        # Nhãn hiển thị kết quả xuất file
        self.labelTextinfomation2 = Label(bottom_frame, text="", bg=BG_COLOR, fg=ACCENT_COLOR, font=('Segoe UI', 10, 'bold'))
        self.labelTextinfomation2.pack()

    # ==========================================
    # KHỐI AUTO UPDATE
    # ==========================================
    def check_for_updates(self):
        try:
            req = urllib.request.Request(REPO_URL, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                
            latest_version = data.get("tag_name", "")
            
            if latest_version and latest_version != CURRENT_VERSION:
                self.latest_version_data = data
                self.master.after(0, lambda: self.btn_update.pack(side=LEFT, padx=15))
        except Exception:
            pass # Bỏ qua nếu lỗi mạng hoặc API

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
            if asset.get("name", "").endswith(".exe"):
                download_url = asset.get("browser_download_url")
                break
                
        if not download_url:
            showinfo("Lỗi", "Không tìm thấy file .exe phù hợp trên GitHub Releases!")
            return
            
        self.progressBar['value'] = 0
        self.labelTextinfomation2.config(text=f"⏳ Đang tải bản cập nhật... Vui lòng không đóng app!")
        
        self.btn_update.pack_forget()
        self.saveFileButton['state'] = "disabled"
        self.choiceFileButton['state'] = "disabled"
        
        def download_thread():
            try:
                import tempfile
                temp_dir = tempfile.gettempdir()
                new_exe_path = os.path.join(temp_dir, "ResizeVideo_Update.exe")
                
                req = urllib.request.Request(download_url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=10) as response, open(new_exe_path, 'wb') as out_file:
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
                            percent = int((downloaded / total_length) * 100)
                            self.master.after(0, lambda p=percent: self.progressBar.config(value=p))
                
                self.master.after(0, lambda: self.labelTextinfomation2.config(text="✅ Tải xong! Đang cài đặt..."))
                self.install_update(new_exe_path)
                
            except Exception as e:
                self.master.after(0, lambda err=e: showinfo("Lỗi cập nhật", f"Lỗi: {err}"))
                self.master.after(0, lambda: self.labelTextinfomation2.config(text="❌ Tải cập nhật thất bại!", fg="red"))
                self.master.after(0, lambda: self.saveFileButton.config(state="normal"))
                self.master.after(0, lambda: self.choiceFileButton.config(state="normal"))
                
        threading.Thread(target=download_thread, daemon=True).start()

    def install_update(self, new_exe_path):
        current_exe = sys.executable 
        
        if not current_exe.endswith(".exe") or "python" in current_exe.lower():
            self.master.after(0, lambda: showinfo("Môi trường Dev", "Đang chạy mã nguồn Python, không phải file .exe. Bỏ qua ghi đè."))
            self.master.after(0, lambda: self.saveFileButton.config(state="normal"))
            self.master.after(0, lambda: self.choiceFileButton.config(state="normal"))
            self.master.after(0, lambda: self.labelTextinfomation2.config(text=""))
            return
            
        current_dir = os.path.dirname(current_exe)
        current_exe_name = os.path.basename(current_exe)
        bat_path = os.path.join(current_dir, "update_script.bat")
        
        bat_content = f'''@echo off
echo Dang cap nhat ResizeVideo Pro...
timeout /t 3 /nobreak > NUL
del "{current_exe_name}"
move /Y "{new_exe_path}" "{current_exe_name}"
start "" "{current_exe_name}"
del "%~f0"
'''
        with open(bat_path, "w", encoding="utf-8") as f:
            f.write(bat_content)
            
        subprocess.Popen(bat_path, shell=True, creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0)
        self.master.after(100, sys.exit)

    # ==========================================
    # CÁC HÀM XỬ LÝ CHÍNH
    # ==========================================
    def choiceFILE(self):
        self.fileNameInput = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4;*.avi;*.mov;*.mkv;*.gif")])
        if not self.fileNameInput:
            return
            
        filename = self.fileNameInput.split("/")[-1]
        try:
            
            # Lấy dung lượng file đầu vào (MB)
            file_size_bytes = os.path.getsize(self.fileNameInput)
            file_size_mb = round(file_size_bytes / (1024 * 1024), 2)
            
            clip = VideoFileClip(self.fileNameInput)
            self.original_duration = clip.duration # Lưu thời lượng gốc
            
            # Thêm "💾 Size Gốc" vào text hiển thị
            info_text = f"🎥 File: {filename}\n\n⏱️ Time: {round(clip.duration, 2)} s\n\n📐 Kích thước: {clip.size[0]} x {clip.size[1]}\n\n🎞️ FPS: {round(clip.fps, 2)}\n\n💾 Dung lượng gốc: {file_size_mb} MB"
            self.labelTextinfomation.config(text=info_text)
            
            self.targetTimeInput.delete(0, END)
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
            # Nếu người dùng gõ vào ô "Thời gian đích" -> Suy ra tốc độ
            if event and event.widget == self.targetTimeInput:
                target_time = float(self.targetTimeInput.get())
                if target_time > 0:
                    self.speedOutput = round(self.original_duration / target_time, 2)
                    self.speed_cb.set(str(self.speedOutput))
                    
            # Nếu người dùng đổi "Tốc độ" -> Suy ra thời gian đích
            else:
                self.speedOutput = float(self.speed_cb.get())
                target_time = round(self.original_duration / self.speedOutput, 2)
                self.targetTimeInput.delete(0, END)
                self.targetTimeInput.insert(0, str(target_time))
                
            
            # 1. Hệ số theo độ phân giải (Dựa vào chiều rộng pixel)
            width = self.scaleOutput[0] if isinstance(self.scaleOutput, tuple) else 1920
            if width >= 3840: scale_mult = 3.5    # 4K
            elif width >= 2560: scale_mult = 1.8  # 2K
            elif width >= 1920: scale_mult = 1.0  # 1080p (Mốc chuẩn)
            elif width >= 1280: scale_mult = 0.5  # 720p
            elif width >= 854: scale_mult = 0.25  # 480p
            else: scale_mult = 0.15               # Nhỏ hơn
            
            # 2. Hệ số theo CRF (Chất lượng video)
            crf = getattr(self, 'crfOutput', 28)
            if crf <= 18: crf_mult = 1.6     # Chất lượng cao -> Nặng
            elif crf <= 23: crf_mult = 1.0   # Trung bình (Mốc chuẩn)
            else: crf_mult = 0.6             # Thấp -> Nhẹ

            # 3. Hệ số theo Video Codec
            codec = getattr(self, 'vcodecOutput', 'libx264')
            if codec == "libx265": codec_mult = 0.5      # H.265 nén cực tốt, dung lượng giảm một nửa
            elif codec == "libvpx-vp9": codec_mult = 0.6 # VP9 nén cũng rất tốt
            elif codec == "libvpx": codec_mult = 1.2     # VP8 cũ hơn, nặng hơn
            elif codec == "mpeg4": codec_mult = 1.5      # MPEG4 cũ, tối ưu kém
            else: codec_mult = 1.0                       # libx264 (Mốc chuẩn)

            # 4. Hệ số theo Định dạng (Xử lý riêng cho GIF)
            fmt = getattr(self, 'dot', '.mp4').lower()
            if fmt == ".gif":
                format_mult = 4.5  # GIF là chuỗi hình ảnh không nén chuẩn video, cực kỳ nặng!
            else:
                format_mult = 1.0  # Các đuôi video khác dung lượng phụ thuộc chính vào Codec

            # Mức chuẩn trung bình cho 1080p, CRF 23, H.264 là khoảng 0.3 MB/giây
            mb_per_second = 0.3 * scale_mult * crf_mult * codec_mult * format_mult
            
            # Khối lượng cuối cùng
            estimated_mb = target_time * mb_per_second
            self.labelEstimate.config(text=f"Dung lượng ước tính: ~ {round(estimated_mb, 2)} MB")
            
            
        except ValueError:
            pass # Bỏ qua lỗi nếu đang gõ dở chữ/ký tự đặc biệt
    
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
            
        # Vô hiệu hóa UI trong lúc render
        self.choiceFileButton['state'] = "disabled"
        self.saveFileButton['state'] = "disabled"
        self.textBoxOutName['state'] = "disabled"
        self.format_cb['state'] = "disabled"
        self.scale_cb['state'] = "disabled"
        self.crf_cb['state'] = "disabled"
        self.codec_cb['state'] = "disabled"
        self.speed_cb['state'] = "disabled"
        
        self.progressBar['value'] = 0
        self.labelTextinfomation2.config(text="⏳ Đang xử lý... Vui lòng đợi!")
        self.master.update() 
        
        def render_thread():
            try:
                clip = VideoFileClip(self.fileNameInput)
                clip = self.apply_resize(clip, self.scaleOutput)
                    
                if self.speedOutput != 1.0:
                    clip = clip.with_speed_scaled(self.speedOutput)
                
                output_path = f"{folder}/{self.fileNameOutput}{self.dot}"
                my_logger = MyTkLogger(self.progressBar, self.master)
                
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
                
                # Cập nhật thông tin file đầu ra
                out_info = f'✅ ĐÃ XUẤT THÀNH CÔNG: {self.fileNameOutput}{self.dot} | Time: {round(clip.duration, 2)}s | Size: {clip.size[0]}x{clip.size[1]}'
                self.master.after(0, lambda: self.labelTextinfomation2.config(text=out_info))
                clip.close()
                
                self.master.after(0, lambda: showinfo(title="Hoàn tất", message="Đã xuất video thành công!"))
                
            except Exception as e:
                self.master.after(0, lambda err=e: showinfo(title="Lỗi xử lý", message=f"Đã có lỗi:\n{err}"))
                self.master.after(0, lambda: self.labelTextinfomation2.config(text="❌ Xuất file thất bại!", fg="red"))
            finally:
                # Bật lại UI
                def reset_ui():
                    self.choiceFileButton['state'] = "normal"
                    self.saveFileButton['state'] = "normal"
                    self.textBoxOutName['state'] = "normal"
                    self.format_cb['state'] = "readonly"
                    self.scale_cb['state'] = "readonly"
                    self.crf_cb['state'] = "readonly"
                    self.codec_cb['state'] = "readonly"
                    self.speed_cb['state'] = "readonly"
                    self.progressBar['value'] = 0
                
                self.master.after(0, reset_ui)

        threading.Thread(target=render_thread, daemon=True).start()

if __name__ == "__main__":
    root = Tk()
    root.geometry('650x550') # Mở rộng size một chút cho thoáng
    root.title('ResizeVideo Pro (MoviePy)')
    root.resizable(False, False)
    root.configure(bg=BG_COLOR)
    myGUI = GUI(root)
    root.mainloop()