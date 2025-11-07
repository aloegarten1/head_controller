import tkinter as tk
from tkinter import ttk
import cv2
from PIL import Image, ImageTk
import logging
import threading
import time
import queue
import random
import serial.tools.list_ports
from utils import head_device

class WebcamApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Real-time Webcam with Parallel Logic")
        self.root.geometry("1200x800")
        
        self.data_queue = queue.Queue()
        self.command_queue = queue.Queue()
        
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            raise ValueError("Unable to open webcam")
        
        width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        print(f"Width: {width}, Height: {height}")

        self.running = True
        self.parallel_logic_active = True
        self.curr_lapl = 0
        
        self.setup_gui()
        self.start_threads()
        self.update_gui()
        
    def setup_gui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        title_label = ttk.Label(main_frame, text="Webcam + Parallel Logic", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        video_frame = ttk.Frame(main_frame)
        video_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        video_frame.columnconfigure(0, weight=1)
        video_frame.columnconfigure(1, weight=1)
        
        ttk.Label(video_frame, text="Full Webcam", font=('Arial', 11, 'bold')).grid(row=0, column=0)
        self.video_label = ttk.Label(video_frame, background='black')
        self.video_label.grid(row=1, column=0, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        ttk.Label(video_frame, text="Center Bottom Square", font=('Arial', 11, 'bold')).grid(row=0, column=1)
        self.square_label = ttk.Label(video_frame, background='black')
        self.square_label.grid(row=1, column=1, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        logic_frame = ttk.LabelFrame(main_frame, text="Parallel Logic Output", padding="10")
        logic_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        logic_frame.columnconfigure(0, weight=1)
        logic_frame.rowconfigure(0, weight=1)
        
        self.log_text = tk.Text(logic_frame, height=12, width=30, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(logic_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        ttk.Button(control_frame, text="Capture Image", 
                  command=self.capture_image).grid(row=0, column=0, padx=5)
        ttk.Button(control_frame, text="Flip Horizontal", 
                  command=self.toggle_flip).grid(row=0, column=1, padx=5)
        ttk.Button(control_frame, text="Start Logic", 
                  command=self.start_logic).grid(row=0, column=2, padx=5)
        ttk.Button(control_frame, text="Stop Logic", 
                  command=self.stop_logic).grid(row=0, column=3, padx=5)
        ttk.Button(control_frame, text="Clear Log", 
                  command=self.clear_log).grid(row=0, column=4, padx=5)
        
        self.status_label = ttk.Label(main_frame, text="System: Starting...")
        self.status_label.grid(row=4, column=0, columnspan=2, pady=5)
        
        self.flip_horizontal = False
        self.frame_count = 0
        
    def start_threads(self):
        self.video_thread = threading.Thread(target=self.video_processing_loop, daemon=True)
        self.video_thread.start()
        
        self.logic_thread = threading.Thread(target=self.parallel_logic_loop, daemon=True)
        self.logic_thread.start()
        
    def video_processing_loop(self):
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                if self.flip_horizontal:
                    frame = cv2.flip(frame, 1)
                
                processed_frame = self.process_frame(frame)
                square_region = self.extract_center_bottom_square(frame)
                
                frame_rgb = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
                square_rgb = cv2.cvtColor(square_region, cv2.COLOR_BGR2RGB)
                
                pil_image = Image.fromarray(frame_rgb)
                pil_square = Image.fromarray(square_rgb)
                
                pil_image = self.resize_image(pil_image, 400, 400)
                pil_square = self.resize_image(pil_square, 400, 400)
                
                self.data_queue.put(('video', pil_image, pil_square))
            
            time.sleep(0.03)
    
    def extract_center_bottom_square(self, frame):
        height, width = frame.shape[:2]
        
        square_size = min(width, height // 2)
        
        x_center = width // 2
        y_bottom = height
        
        x_start = x_center - square_size // 2
        x_end = x_center + square_size // 2
        y_start = y_bottom - square_size
        y_end = y_bottom
        
        x_start = max(0, x_start)
        y_start = max(0, y_start)
        x_end = min(width, x_end)
        y_end = min(height, y_end)
        
        square_region = frame[y_start:y_end, x_start:x_end]
        
        square_with_border = square_region.copy()
        cv2.rectangle(square_with_border, (0, 0), 
                     (square_region.shape[1]-1, square_region.shape[0]-1), 
                     (0, 255, 0), 2)
        
        self.curr_lapl = self.calculate_laplacian_variance(square_region)
        cv2.putText(square_with_border, f"Laplacian: {self.curr_lapl:.1f}", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        print(f"Laplacian: {self.curr_lapl:.1f}")
        
        return square_with_border
    
    def calculate_laplacian_variance(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        return laplacian.var()
    
    def process_frame(self, frame):
        self.frame_count += 1
        cv2.putText(frame, f"Frame: {self.frame_count}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        height, width = frame.shape[:2]
        square_size = min(width, height // 2)
        x_center = width // 2
        y_bottom = height
        
        cv2.rectangle(frame, 
                     (x_center - square_size // 2, y_bottom - square_size),
                     (x_center + square_size // 2, y_bottom),
                     (0, 255, 0), 2)
        
        return frame
    
    def parallel_logic_loop(self):
        self.set_logger()
        logger = logging.getLogger()
        logger.log(logging.INFO, "Logger started.")

        devs = serial.tools.list_ports.comports()
        
        if (len(devs) == 0):
            logger.log(level=logging.INFO, msg="No serial device was found. Try to connect USB-device to you host.")
            return
        print("\nAvailable devices:")
        self.print_devices(devs)
        head = head_device.HeadDevice("COM4")
        
        head.mot1_go(300, 1000, 0)

        for i in range(700):
            head.mot1_go(700 + (i + 1) * 10, 1000, 0)
            
            if (self.curr_lapl > 200.0):
                print("AAAAAAAAAAA")
                break


        head.mot1_go(0, 1000, 0)
    
    def update_gui(self):
        try:
            while True:
                data = self.data_queue.get_nowait()
                
                if data[0] == 'video':
                    self.photo = ImageTk.PhotoImage(image=data[1])
                    self.video_label.configure(image=self.photo)
                    
                    self.square_photo = ImageTk.PhotoImage(image=data[2])
                    self.square_label.configure(image=self.square_photo)
                        
        except queue.Empty:
            pass
        
        status = f"Frames: {self.frame_count} | Logic: {'Active' if self.parallel_logic_active else 'Paused'}"
        self.status_label.configure(text=status)
        
        self.root.after(50, self.update_gui)
    
    def resize_image(self, image, max_width, max_height):
        width, height = image.size
        if width > max_width or height > max_height:
            ratio = min(max_width/width, max_height/height)
            new_width = int(width * ratio)
            new_height = int(height * ratio)
            return image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        return image
    
    def capture_image(self):
        ret, frame = self.cap.read()
        if ret:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"capture_{timestamp}.jpg"
            cv2.imwrite(filename, frame)
            self.add_to_log(f"Image saved: {filename}")
    
    def toggle_flip(self):
        self.flip_horizontal = not self.flip_horizontal
        self.add_to_log(f"Flip horizontal: {self.flip_horizontal}")
    
    def start_logic(self):
        self.parallel_logic_active = True
        self.add_to_log("Parallel logic STARTED")
    
    def stop_logic(self):
        self.parallel_logic_active = False
        self.add_to_log("Parallel logic STOPPED")
    
    def clear_log(self):
        self.log_text.delete(1.0, tk.END)
    
    def add_to_log(self, message):
        self.log_text.insert(tk.END, f"SYSTEM: {message}\n")
        self.log_text.see(tk.END)
     
    def shutdown(self):
        self.running = False
        if hasattr(self, 'cap'):
            self.cap.release()

    def set_logger(self):
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s [%(levelname)s] (%(filename)s:%(lineno)d): %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

    def print_devices(self, devs):
        for dev in devs:
            print(f"\t- [{dev.serial_number}] {dev.name} - {dev.description}")

def main():
    root = tk.Tk()
    app = WebcamApp(root)
    
    def on_closing():
        app.shutdown()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()