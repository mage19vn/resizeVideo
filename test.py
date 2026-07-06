from tkinter import *
from tkinter import filedialog
from tkinter.messagebox import showinfo
from tkinter import ttk
import threading
from proglog import ProgressBarLogger
import random

# Import MoviePy (thay thế hoàn toàn ffmpeg-python)
from moviepy import VideoFileClip

class MyTkLogger(ProgressBarLogger):
    def __init__(self, progress_bar, root):
        super().__init__()
        self.progress_bar = progress_bar
        self.root = root

    def bars_callback(self, bar, attr, value, old_value=None):
        # Lấy tổng số (frame/thời gian) và tiến độ hiện tại
        total = self.bars[bar]['total']
        if total > 0:
            percent = (value / total) * 100
            self.progress_bar['value'] = percent
            # Bắt buộc giao diện vẽ lại ngay lập tức
            self.root.update_idletasks()

class GUI:
    def __init__(self, master):
        self.master = master
        
        # Khởi tạo các biến mặc định
        self.fileNameInput = ''
        self.fileNameOutput = 'United'
        self.scaleOutput = 0.5  # Mặc định scale giảm 50%
        self.crfOutput = 28
        self.speedOutput = 1.0  # Tốc độ mặc định là 1 (bình thường)
        self.vcodecOutput = "libx264"
        self.dot = '.mp4'

        labelText = Label(self.master, text="ResizeVideo", font=('Terminal', 20), bg="#2fd09b")
        labelText.pack()
        labelTextOut = Label(self.master, text="Name output", font=('Terminal', 12), bg="#2fd09b")
        labelTextOut.place(x=300, y=200)
        self.textBoxOutName = Entry(self.master, bg="#cccccc", relief=GROOVE, width=30)
        self.textBoxOutName.place(x=300, y=230)
        
        self.choiceFileButton = Button(self.master, text='Chon file', font=('Terminal', 12), 
                                  fg="#353535", bg="#b1b1b1", activebackground="#b1b1b1", relief=SOLID, command=self.choiceFILE)
        self.choiceFileButton.place(x=30, y=220)
        self.saveFileButton = Button(self.master, text='SAVE', font=('Terminal', 12), 
                                  fg="#353535", bg="#b1b1b1", activebackground="#b1b1b1", relief=SOLID, command=self.saveFILE)
        self.saveFileButton.place(x=300, y=420)
        
        self.labelTextinfomation = Label(self.master, bg='#ffffff',  font=('Terminal', 12), height=8, width=20, justify='left', wraplength=300)
        self.labelTextinfomation2 = Label(self.master, bg='#ffffff',  font=('Terminal', 12), height=8, width=20, justify='left', wraplength=300)
        
        self.labelTextinfomation3 = Label(self.master, bg="#a1a1a1",  font=('Terminal', 12), height=1, width=10, justify='left')
        self.labelTextinfomation3.place(x=300, y=50)
        self.TextTYPE = Label(self.master, text="Type", font=('Terminal', 12), bg="#2fd09b")
        self.TextTYPE.place(x=80, y=50)
        
        self.labelTextinfomation4 = Label(self.master, bg="#a1a1a1",  font=('Terminal', 12), height=1, width=10, justify='left')
        self.labelTextinfomation4.place(x=300, y=80)
        self.TextTYPE2 = Label(self.master, text="Scale", font=('Terminal', 12), bg="#2fd09b")
        self.TextTYPE2.place(x=70, y=80)
        
        self.labelTextinfomation5 = Label(self.master, bg="#a1a1a1",  font=('Terminal', 12), height=1, width=10, justify='left')
        self.labelTextinfomation5.place(x=300, y=110)
        self.TextTYPE3 = Label(self.master, text="CRF", font=('Terminal', 12), bg="#2fd09b")
        self.TextTYPE3.place(x=80, y=110)
        
        self.labelTextinfomation6 = Label(self.master, bg="#a1a1a1",  font=('Terminal', 12), height=1, width=10, justify='left')
        self.labelTextinfomation6.place(x=300, y=140)
        self.TextTYPE4 = Label(self.master, text="VCODEC", font=('Terminal', 12), bg="#2fd09b")
        self.TextTYPE4.place(x=65, y=140)
        
        self.labelTextinfomation7 = Label(self.master, bg="#a1a1a1",  font=('Terminal', 12), height=1, width=10, justify='left')
        self.labelTextinfomation7.place(x=300, y=170)
        self.TextTYPE5 = Label(self.master, text="SPEED", font=('Terminal', 12), bg="#2fd09b")
        self.TextTYPE5.place(x=65, y=170)
        
        self.menuN = Menu(self.master, bg='#ffffff', tearoff=0)
        
        self.listBox = Menu(self.master, bg="#ffffff", tearoff=0)
        self.LISTCANSAVE = [".mp4", ".avi", ".mov", ".mkv", ".gif"]
        for i in range(len(self.LISTCANSAVE)):
            self.listBox.add_command(label=self.LISTCANSAVE[i].upper()[1:], command=lambda idx=i: self.getDotfromMENU(idx))
        
        self.listBox2 = Menu(self.master, bg="#ffffff", tearoff=0)
        # Sử dụng Tuple (Width, Height) để tương thích với Moviepy
        self.LISTSCALE = [(3840, 2160), (2560, 1440), (1920, 1080), (1280, 720), (854, 480), (640, 360), (426, 240)]
        self.LISTSCALENAME = ["2160p (4K)", "1440p (2K)", "1080p (FHD)", "720p (HD)", "480p (SD)", "360p", "240p"]
        for i in range(len(self.LISTSCALENAME)):
            self.listBox2.add_command(label=self.LISTSCALENAME[i], command=lambda idx=i: self.getScalefromMENU(idx))
        
        self.listBox3 = Menu(self.master, bg="#ffffff", tearoff=0)
        self.LISTCRF = [18, 23, 28]
        self.listBox3.add_command(label="CRF 18 (Chất lượng cao)", command=lambda: self.getCrffromMENU(0))
        self.listBox3.add_command(label="CRF 23 (Chất lượng TB)", command=lambda: self.getCrffromMENU(1))
        self.listBox3.add_command(label="CRF 28 (Chất lượng thấp)", command=lambda: self.getCrffromMENU(2))
        
        self.listBox4 = Menu(self.master, bg="#ffffff", tearoff=0)
        self.LISTVCODEC = ["libx264", "libx265", "libvpx", "libvpx-vp9", "mpeg4"]
        for i in range(len(self.LISTVCODEC)):
            self.listBox4.add_command(label=self.LISTVCODEC[i].upper(), command=lambda idx=i: self.getVCODECfromMENU(idx))
        
        self.listBox5 = Menu(self.master, bg="#ffffff", tearoff=0)
        self.LISTSPEED = [0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0]
        for i in range(len(self.LISTSPEED)):
            self.listBox5.add_command(label=str(self.LISTSPEED[i]), command=lambda idx=i: self.getSpeedfromMENU(idx))
        
        self.menuN.add_cascade(label="Type", menu=self.listBox)
        self.menuN.add_cascade(label="Scale Video", menu=self.listBox2)
        self.menuN.add_cascade(label="Constant Rate Factor", menu=self.listBox3)
        self.menuN.add_cascade(label="VCODEC", menu=self.listBox4)
        self.menuN.add_cascade(label="Speed", menu=self.listBox5)
        self.master.bind("<Button-3>", self.showPU)
        
        # --- THÊM THANH TIẾN TRÌNH VÀO GIAO DIỆN ---
        self.progressBar = ttk.Progressbar(self.master, orient=HORIZONTAL, length=480, mode='determinate')
        self.progressBar.place(x=35, y=390)
        
    def showPU(self, even):
        self.menuN.post(even.x_root, even.y_root)
    
    def choiceFILE(self):
        self.fileNameInput = filedialog.askopenfilename(filetypes=[
                                                            ("Video Files", "*.mp4;*.avi;*.mov;*.mkv;*.gif")
                                                        ])
        if not self.fileNameInput:
            showinfo(title="Cảnh báo", message="Chưa chọn file")
        else:
            filename = self.fileNameInput.split("/")[-1]
            try:
                clip = VideoFileClip(self.fileNameInput)
                self.labelTextinfomation['text'] = f'File: {filename}\n\nTime: {round(clip.duration, 2)} s\n\nSize: {clip.size[0]} x {clip.size[1]}\n\nFPS: {round(clip.fps, 2)}'
                self.labelTextinfomation.place(x=30, y=270)
                clip.close() 
            except Exception as e:
                showinfo(title="Lỗi", message=f"Không thể đọc file: {e}")
    
    def randomS(self):
        r = ''
        for i in range(10):
            r += random.choice('qwertyuiopasdfghjklzxcvbnm1234567890')
        return r   
    
    def getSpeedfromMENU(self, val):
        self.speedOutput = self.LISTSPEED[val]
        self.labelTextinfomation7['text'] = str(self.speedOutput)
    
    def getDotfromMENU(self, val):
        self.dot = self.LISTCANSAVE[val]
        self.labelTextinfomation3["text"] = self.dot
        
    def getScalefromMENU(self, val):
        self.scaleOutput = self.LISTSCALE[val]
        self.labelTextinfomation4["text"] = f"{self.scaleOutput[0]}:{self.scaleOutput[1]}"
        
    def getCrffromMENU(self, val):
        self.crfOutput = self.LISTCRF[val]
        self.labelTextinfomation5["text"] = str(self.crfOutput)
        
    def getVCODECfromMENU(self, val):
        self.vcodecOutput = self.LISTVCODEC[val]
        self.labelTextinfomation6["text"] = self.vcodecOutput
    
    # Hàm hỗ trợ an toàn cho Resize (Tương thích tốt v2.2.1)
    def apply_resize(self, clip, scale_val):
        if isinstance(scale_val, tuple):
            return clip.resized(width=scale_val[0], height=scale_val[1])
        return clip.resized(scale_val) # Dùng cho trường hợp mặc định giảm 50% (float)
        
    def saveFILE(self):
        if not self.fileNameInput:
            showinfo(title="Cảnh báo", message="Vui lòng chọn file video trước!")
            return

        readentry = self.textBoxOutName.get()
        self.fileNameOutput = readentry if (len(readentry) > 0) else f'United_{self.randomS()}'
        
        folder = filedialog.askdirectory()
        if not folder:
            showinfo(title="Cảnh báo", message="Chưa chọn thư mục lưu")
            return
            
        # Vô hiệu hóa nút trong lúc render
        self.choiceFileButton['state'] = "disabled"
        self.saveFileButton['state'] = "disabled"
        self.textBoxOutName['state'] = "disabled"
        self.progressBar['value'] = 0  # Reset thanh tiến trình về 0
        self.master.update() 
        
        # Đưa chức năng render vào hàm chạy nền (Thread) để không làm đơ giao diện
        def render_thread():
            try:
                clip = VideoFileClip(self.fileNameInput)
                clip = self.apply_resize(clip, self.scaleOutput)
                    
                if self.speedOutput != 1.0:
                    clip = clip.with_speed_multiplied(self.speedOutput)
                
                output_path = f"{folder}/{self.fileNameOutput}{self.dot}"
                
                # Khởi tạo Logger kết nối với thanh Progress Bar của chúng ta
                my_logger = MyTkLogger(self.progressBar, self.master)
                
                # Thêm biến logger=my_logger vào để nó báo tiến độ
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
                
                self.labelTextinfomation2['text'] = f'File: {self.fileNameOutput+self.dot}\n\nTime: {round(clip.duration, 2)} s\n\nSize: {clip.size[0]} x {clip.size[1]}\n\nFPS: {round(clip.fps, 2)}'
                self.labelTextinfomation2.place(x=300, y=270)
                clip.close()
                
                # Việc hiển thị popup nên được đẩy về luồng chính của giao diện
                self.master.after(0, lambda: showinfo(title="Thông báo", message="Đã xuất file thành công!"))
                
            except Exception as e:
                self.master.after(0, lambda err=e: showinfo(title="Lỗi xử lý", message=f"Đã có lỗi:\n{err}"))
            finally:
                # Bật lại các nút bằng hàm của giao diện chính
                def reset_ui():
                    self.choiceFileButton['state'] = "normal"
                    self.saveFileButton['state'] = "normal"
                    self.textBoxOutName['state'] = "normal"
                    self.progressBar['value'] = 0
                
                self.master.after(0, reset_ui)

        # Kích hoạt tiến trình chạy ngầm
        threading.Thread(target=render_thread, daemon=True).start()

if __name__ == "__main__":
    root = Tk()
    root.geometry('550x450')
    root.title('ResizeVideo (MoviePy 2.2.1)')
    root.resizable(0,0)
    root.configure(bg="#2FD09B")
    myGUI = GUI(root)
    root.mainloop()