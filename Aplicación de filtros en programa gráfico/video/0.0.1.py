import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk
import threading
import time
import os
from datetime import datetime

class FiltrosVideoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Filtros en Tiempo Real - Proyecto Integrador")
        self.root.geometry("1400x800")
        self.root.configure(bg='#f5f5f7')
        
        # Variables
        self.img = None
        self.video_capture = None
        self.video_active = False
        self.recording = False
        self.current_filter = tk.StringVar(value="Suavizado")
        self.video_source = tk.StringVar(value="none")
        self.out_video = None
        self.recording_start_time = None
        self.filtered_frame = None
        
        # Filtros seleccionados (más de 5)
        self.filters = ["Suavizado", "Convolución 2D", "Promedio", "Gaussiano", "Mediana", 
                   "Umbralización Simple", "Umbralización Adaptativa", "Binarización de Otsu", 
                   "Laplaciano", "Sobel X", "Sobel Y", "Canny"]
        
        # Configurar estilos
        self.setup_styles()
        
        # Crear interfaz
        self.create_widgets()
        
        # Centrar ventana
        self.center_window()
        
        # Directorio para guardar videos
        self.video_dir = "videos_grabados"
        if not os.path.exists(self.video_dir):
            os.makedirs(self.video_dir)
        
    def setup_styles(self):
        self.colors = {
            'bg': '#f5f5f7',
            'card': '#ffffff',
            'text': '#1d1d1f',
            'accent': '#007aff',
            'success': '#34c759',
            'warning': '#ff9500',
            'error': '#ff3b30',
            'gray': '#8e8e93'
        }
        
        self.fonts = {
            'title': ('Helvetica', 24, 'bold'),
            'subtitle': ('Helvetica', 16),
            'body': ('Helvetica', 12),
            'small': ('Helvetica', 10)
        }
        
    def create_widgets(self):
        main_frame = tk.Frame(self.root, bg=self.colors['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        title_label = tk.Label(
            main_frame, 
            text="Filtros en Tiempo Real", 
            font=self.fonts['title'],
            bg=self.colors['bg'],
            fg=self.colors['text']
        )
        title_label.pack(pady=(0, 20))
        
        # Frame para botones superiores
        top_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        top_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Botones de fuente de video
        self.create_button(top_frame, "📷 Cámara en Vivo", self.start_webcam, 'accent').pack(side=tk.LEFT, padx=5)
        self.create_button(top_frame, "🎥 Cargar Video", self.load_video, 'success').pack(side=tk.LEFT, padx=5)
        self.create_button(top_frame, "🖼️ Cargar Imagen", self.load_image, 'warning').pack(side=tk.LEFT, padx=5)
        self.create_button(top_frame, "⏹️ Detener", self.stop_video, 'error').pack(side=tk.LEFT, padx=5)
        
        # Frame para selector de filtros y grabación
        control_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        control_frame.pack(fill=tk.X, pady=(0, 20))
        
        filter_label = tk.Label(
            control_frame,
            text="Filtro:",
            font=self.fonts['body'],
            bg=self.colors['bg'],
            fg=self.colors['text']
        )
        filter_label.pack(side=tk.LEFT, padx=(0, 10))
        
        filter_dropdown = ttk.Combobox(
            control_frame,
            textvariable=self.current_filter,
            values=self.filters,
            state="readonly",
            font=self.fonts['body'],
            width=25
        )
        filter_dropdown.pack(side=tk.LEFT, padx=5)
        filter_dropdown.set(self.filters[0])
        
        # Botones de grabación
        self.record_button = self.create_button(control_frame, "⏺️ Grabar Video", self.toggle_recording, 'warning')
        self.record_button.pack(side=tk.LEFT, padx=20)
        
        # Estado de grabación
        self.recording_label = tk.Label(
            control_frame,
            text="",
            font=self.fonts['body'],
            bg=self.colors['bg'],
            fg=self.colors['error']
        )
        self.recording_label.pack(side=tk.LEFT, padx=10)
        
        # Frame para las dos ventanas de video
        videos_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        videos_frame.pack(fill=tk.BOTH, expand=True)
        
        # Video original
        original_frame = self.create_video_frame(videos_frame, "Video Original")
        original_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        
        self.label_original = tk.Label(
            original_frame,
            bg=self.colors['card'],
            relief=tk.FLAT
        )
        self.label_original.pack(expand=True, padx=10, pady=10)
        
        # Video filtrado
        filtered_frame = self.create_video_frame(videos_frame, "Video con Filtro")
        filtered_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)
        
        self.label_filtered = tk.Label(
            filtered_frame,
            bg=self.colors['card'],
            relief=tk.FLAT
        )
        self.label_filtered.pack(expand=True, padx=10, pady=10)
        
        # Información adicional
        info_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        info_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.info_label = tk.Label(
            info_frame,
            text="Selecciona una fuente de video para comenzar",
            font=self.fonts['body'],
            bg=self.colors['bg'],
            fg=self.colors['gray']
        )
        self.info_label.pack()
        
        # Mensaje inicial
        self.show_placeholder()
        
    def create_video_frame(self, parent, title):
        frame = tk.Frame(parent, bg=self.colors['bg'])
        
        title_label = tk.Label(
            frame,
            text=title,
            font=self.fonts['subtitle'],
            bg=self.colors['bg'],
            fg=self.colors['text']
        )
        title_label.pack(pady=(0, 10))
        
        return frame
        
    def create_button(self, parent, text, command, color_key):
        button = tk.Button(
            parent,
            text=text,
            command=command,
            font=self.fonts['body'],
            bg=self.colors[color_key],
            fg='white',
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor='hand2',
            borderwidth=0
        )
        
        button.bind("<Enter>", lambda e: self.on_enter(e, button, color_key))
        button.bind("<Leave>", lambda e: self.on_leave(e, button, color_key))
        
        return button
        
    def on_enter(self, event, button, color_key):
        button.config(bg=self.lighten_color(self.colors[color_key]))
        
    def on_leave(self, event, button, color_key):
        button.config(bg=self.colors[color_key])
        
    def lighten_color(self, color):
        if color == '#007aff':
            return '#3395ff'
        elif color == '#34c759':
            return '#5fd97a'
        elif color == '#ff9500':
            return '#ffaa33'
        elif color == '#ff3b30':
            return '#ff6b5f'
        return color
        
    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def show_placeholder(self):
        placeholder = np.ones((400, 600, 3), dtype=np.uint8) * 240
        placeholder = cv2.putText(placeholder, "Esperando video...", (150, 200), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 1, (100, 100, 100), 2)
        self.show_image(placeholder, self.label_original)
        self.show_image(placeholder, self.label_filtered)
    
    def start_webcam(self):
        self.stop_video()
        self.video_capture = cv2.VideoCapture(0)
        if self.video_capture.isOpened():
            self.video_active = True
            self.info_label.config(text="📷 Cámara en vivo - Aplicando filtros en tiempo real")
            self.update_video()
        else:
            self.show_error("No se pudo abrir la cámara")
    
    def load_video(self):
        file_path = filedialog.askopenfilename(
            title="Seleccionar video",
            filetypes=[
                ("Videos", "*.mp4 *.avi *.mov *.mkv *.wmv"),
                ("Todos los archivos", "*.*")
            ]
        )
        if file_path:
            self.stop_video()
            self.video_capture = cv2.VideoCapture(file_path)
            if self.video_capture.isOpened():
                self.video_active = True
                self.info_label.config(text=f"🎥 Reproduciendo: {os.path.basename(file_path)}")
                self.update_video()
            else:
                self.show_error("No se pudo cargar el video")
    
    def load_image(self):
        file_path = filedialog.askopenfilename(
            title="Seleccionar imagen",
            filetypes=[
                ("Imágenes", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff"),
                ("Todos los archivos", "*.*")
            ]
        )
        if file_path:
            self.stop_video()
            self.img = cv2.imread(file_path)
            if self.img is not None:
                self.video_active = True
                self.info_label.config(text=f"🖼️ Imagen cargada: {os.path.basename(file_path)}")
                self.update_static_image()
            else:
                self.show_error("No se pudo cargar la imagen")
    
    def stop_video(self):
        self.video_active = False
        if self.recording:
            self.toggle_recording()
        if self.video_capture:
            self.video_capture.release()
            self.video_capture = None
        self.show_placeholder()
        self.info_label.config(text="Video detenido")
    
    def toggle_recording(self):
        if not self.video_active:
            self.show_error("No hay video activo para grabar")
            return
            
        if not self.recording:
            # Iniciar grabación
            filename = f"filtro_{self.current_filter.get()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.avi"
            filepath = os.path.join(self.video_dir, filename)
            
            # Obtener dimensiones del frame
            if self.img is not None:
                h, w = self.img.shape[:2]
            else:
                h, w = 480, 640
            
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            self.out_video = cv2.VideoWriter(filepath, fourcc, 20.0, (w*2, h))
            self.recording = True
            self.recording_start_time = time.time()
            self.record_button.config(text="⏹️ Detener Grabación", bg=self.colors['error'])
            self.recording_label.config(text="🔴 GRABANDO")
            self.info_label.config(text=f"Grabando: {filename}")
        else:
            # Detener grabación
            self.recording = False
            if self.out_video:
                self.out_video.release()
                self.out_video = None
            self.record_button.config(text="⏺️ Grabar Video", bg=self.colors['warning'])
            self.recording_label.config(text="")
            recording_time = time.time() - self.recording_start_time
            self.info_label.config(text=f"Video guardado - Duración: {recording_time:.1f} segundos")
    
    def update_video(self):
        if self.video_active and self.video_capture:
            ret, frame = self.video_capture.read()
            if ret:
                self.img = frame
                self.process_and_display(frame)
                self.root.after(30, self.update_video)
            else:
                # Reiniciar video si llegó al final
                if isinstance(self.video_capture, cv2.VideoCapture):
                    self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    self.root.after(30, self.update_video)
    
    def update_static_image(self):
        if self.video_active and self.img is not None:
            self.process_and_display(self.img)
            self.root.after(100, self.update_static_image)
    
    def process_and_display(self, frame):
        # Mostrar original
        self.show_image(frame, self.label_original)
        
        # Aplicar filtro
        filtered = self.apply_filter_to_frame(frame)
        self.filtered_frame = filtered
        self.show_image(filtered, self.label_filtered)
        
        # Grabar si está activo
        if self.recording and self.out_video:
            # Combinar original y filtrado para grabar
            h, w = frame.shape[:2]
            if len(filtered.shape) == 2:
                filtered = cv2.cvtColor(filtered, cv2.COLOR_GRAY2BGR)
            
            # Asegurar que ambas imágenes tengan el mismo tamaño
            if filtered.shape[:2] != (h, w):
                filtered = cv2.resize(filtered, (w, h))
            
            combined = np.hstack((frame, filtered))
            self.out_video.write(combined)
    
    def apply_filter_to_frame(self, frame):
        filter_name = self.current_filter.get()
        
        try:
            if filter_name == "Suavizado":
                return cv2.GaussianBlur(frame, (5, 5), 0)
                
            elif filter_name == "Convolución 2D":
                kernel = np.ones((5, 5), np.float32) / 25
                return cv2.filter2D(frame, -1, kernel)
                
            elif filter_name == "Promedio":
                return cv2.blur(frame, (5, 5))
                
            elif filter_name == "Gaussiano":
                return cv2.GaussianBlur(frame, (5, 5), 0)
                
            elif filter_name == "Mediana":
                return cv2.medianBlur(frame, 5)
                
            elif filter_name == "Umbralización Simple":
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
                return cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)
                
            elif filter_name == "Umbralización Adaptativa":
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                thresh = cv2.adaptiveThreshold(
                    gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                    cv2.THRESH_BINARY, 11, 2
                )
                return cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)
                
            elif filter_name == "Binarización de Otsu":
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                _, thresh = cv2.threshold(
                    gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
                )
                return cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)
                
            elif filter_name == "Laplaciano":
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                laplacian = cv2.Laplacian(gray, cv2.CV_64F)
                laplacian = np.uint8(np.absolute(laplacian))
                return cv2.cvtColor(laplacian, cv2.COLOR_GRAY2BGR)
                
            elif filter_name == "Sobel X":
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=5)
                sobelx = np.uint8(np.absolute(sobelx))
                return cv2.cvtColor(sobelx, cv2.COLOR_GRAY2BGR)
                
            elif filter_name == "Sobel Y":
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=5)
                sobely = np.uint8(np.absolute(sobely))
                return cv2.cvtColor(sobely, cv2.COLOR_GRAY2BGR)
                
            elif filter_name == "Canny":
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                canny = cv2.Canny(gray, 100, 200)
                return cv2.cvtColor(canny, cv2.COLOR_GRAY2BGR)
                
        except Exception as e:
            print(f"Error aplicando filtro: {e}")
            return frame
        
        return frame
    
    def show_image(self, image, label):
        if image is None:
            return
            
        if len(image.shape) == 3:
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        else:
            image_rgb = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
            
        height, width = image_rgb.shape[:2]
        max_size = 400
        
        if width > height:
            new_width = max_size
            new_height = int(height * (max_size / width))
        else:
            new_height = max_size
            new_width = int(width * (max_size / height))
            
        image_rgb = cv2.resize(image_rgb, (new_width, new_height))
        
        image_pil = Image.fromarray(image_rgb)
        imgtk = ImageTk.PhotoImage(image=image_pil)
        
        label.configure(image=imgtk, width=new_width, height=new_height)
        label.image = imgtk
            
    def show_error(self, message):
        error_window = tk.Toplevel(self.root)
        error_window.title("Error")
        error_window.configure(bg=self.colors['card'])
        error_window.geometry("300x150")
        
        error_window.update_idletasks()
        x = (error_window.winfo_screenwidth() // 2) - (300 // 2)
        y = (error_window.winfo_screenheight() // 2) - (150 // 2)
        error_window.geometry(f'300x150+{x}+{y}')
        
        error_label = tk.Label(
            error_window,
            text="⚠️ " + message,
            font=self.fonts['body'],
            bg=self.colors['card'],
            fg=self.colors['text'],
            wraplength=250
        )
        error_label.pack(expand=True, padx=20, pady=20)
        
        close_button = tk.Button(
            error_window,
            text="OK",
            command=error_window.destroy,
            font=self.fonts['body'],
            bg=self.colors['accent'],
            fg='white',
            relief=tk.FLAT,
            padx=30,
            pady=5,
            cursor='hand2'
        )
        close_button.pack(pady=(0, 20))
        
        error_window.after(3000, error_window.destroy)
    
    def __del__(self):
        if self.video_capture:
            self.video_capture.release()
        if self.out_video:
            self.out_video.release()

if __name__ == "__main__":
    root = tk.Tk()
    app = FiltrosVideoApp(root)
    root.mainloop()
