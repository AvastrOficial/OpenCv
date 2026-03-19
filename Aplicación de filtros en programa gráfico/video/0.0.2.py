import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk
import time
import os
from datetime import datetime

class FiltrosVideoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Filtros en Tiempo Real - Proyecto Integrador")
        self.root.geometry("1400x800")
        self.root.configure(bg='#0a0a0a')
        
        # Bindear tecla ESC para cerrar
        self.root.bind('<Escape>', self.cerrar_app)
        
        # Variables
        self.video_capture = None
        self.video_active = False
        self.recording = False
        self.current_filter = tk.StringVar(value="Selecciona un filtro")
        self.out_video = None
        self.recording_start_time = None
        self.filtered_frame = None
        
        # Filtros seleccionados
        self.filters = [
            "Suavizado Gaussiano",
            "Filtro de Promedio",
            "Filtro de Mediana",
            "Detección de Bordes Canny",
            "Laplaciano",
            "Sobel X",
            "Sobel Y",
            "Umbralización Simple",
            "Umbralización Adaptativa",
            "Binarización Otsu",
            "Convolución 2D",
            "Filtro Bilateral"
        ]
        
        # Configurar estilos modernos
        self.setup_styles()
        
        # Crear interfaz
        self.create_widgets()
        
        # Centrar ventana
        self.center_window()
        
        # Directorio para guardar videos
        self.video_dir = "videos_grabados"
        if not os.path.exists(self.video_dir):
            os.makedirs(self.video_dir)
        
        # Mensaje de ayuda
        self.info_label.config(text="Presiona ESC para cerrar la aplicación")
        
    def cerrar_app(self, event=None):
        """Cierra la aplicación correctamente"""
        self.stop_video()
        self.root.quit()
        self.root.destroy()
        
    def setup_styles(self):
        self.colors = {
            'bg': '#0a0a0a',
            'card': '#1e1e1e',
            'text': '#ffffff',
            'text_secondary': '#b0b0b0',
            'accent': '#4a9eff',
            'accent_hover': '#7ab8ff',
            'success': '#00c853',
            'warning': '#ff6d00',
            'error': '#ff3d00',
            'gray': '#2c2c2c',
            'border': '#333333'
        }
        
        self.fonts = {
            'title': ('Segoe UI', 28, 'bold'),
            'subtitle': ('Segoe UI', 18),
            'body': ('Segoe UI', 12),
            'small': ('Segoe UI', 10),
            'button': ('Segoe UI', 11, 'bold')
        }
        
        # Configurar estilo para ttk widgets
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configurar Combobox
        style.configure(
            'Custom.TCombobox',
            fieldbackground=self.colors['card'],
            background=self.colors['card'],
            foreground=self.colors['text'],
            arrowcolor=self.colors['accent'],
            bordercolor=self.colors['border'],
            lightcolor=self.colors['border'],
            darkcolor=self.colors['border'],
            borderwidth=1,
            relief="flat",
            padding=8
        )
        
        style.map(
            'Custom.TCombobox',
            fieldbackground=[('readonly', self.colors['card'])],
            foreground=[('readonly', self.colors['text'])]
        )
        
    def create_widgets(self):
        # Main container
        main_frame = tk.Frame(self.root, bg=self.colors['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        # Header
        header_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        header_frame.pack(fill=tk.X, pady=(0, 25))
        
        # Título
        title_label = tk.Label(
            header_frame,
            text="Filtros en Tiempo Real", 
            font=self.fonts['title'],
            bg=self.colors['bg'],
            fg=self.colors['text']
        )
        title_label.pack()
        
        # Subtítulo
        subtitle_label = tk.Label(
            header_frame,
            text="Procesamiento de video con OpenCV",
            font=self.fonts['body'],
            bg=self.colors['bg'],
            fg=self.colors['text_secondary']
        )
        subtitle_label.pack(pady=(5, 0))
        
        # Frame para controles principales
        controls_card = tk.Frame(main_frame, bg=self.colors['card'], relief=tk.FLAT, bd=1)
        controls_card.pack(fill=tk.X, pady=(0, 25), ipadx=15, ipady=15)
        
        # Botones de fuente de video
        buttons_frame = tk.Frame(controls_card, bg=self.colors['card'])
        buttons_frame.pack(pady=10)
        
        self.create_styled_button(
            buttons_frame, 
            "Cámara en Vivo", 
            self.start_webcam, 
            'accent',
            width=15
        ).pack(side=tk.LEFT, padx=8)
        
        self.create_styled_button(
            buttons_frame, 
            "Cargar Video", 
            self.load_video, 
            'success',
            width=15
        ).pack(side=tk.LEFT, padx=8)
        
        self.create_styled_button(
            buttons_frame, 
            "Detener", 
            self.stop_video, 
            'error',
            width=15
        ).pack(side=tk.LEFT, padx=8)
        
        # Separador visual
        separator = tk.Frame(controls_card, height=1, bg=self.colors['border'])
        separator.pack(fill=tk.X, padx=20, pady=15)
        
        # Frame para selector de filtros y grabación
        control_frame = tk.Frame(controls_card, bg=self.colors['card'])
        control_frame.pack(fill=tk.X, padx=20, pady=(0, 15))
        
        # Label de filtro
        filter_label = tk.Label(
            control_frame,
            text="FILTRO",
            font=self.fonts['small'],
            bg=self.colors['card'],
            fg=self.colors['text_secondary']
        )
        filter_label.pack(anchor='w', pady=(0, 5))
        
        # Frame para el dropdown
        filter_select_frame = tk.Frame(control_frame, bg=self.colors['card'])
        filter_select_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Combobox
        filter_dropdown = ttk.Combobox(
            filter_select_frame,
            textvariable=self.current_filter,
            values=self.filters,
            state="readonly",
            font=self.fonts['body'],
            style='Custom.TCombobox',
            height=10
        )
        filter_dropdown.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5)
        filter_dropdown.set(self.filters[0])
        
        # Botones de grabación
        recording_frame = tk.Frame(control_frame, bg=self.colors['card'])
        recording_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.record_button = self.create_styled_button(
            recording_frame, 
            "Iniciar Grabación", 
            self.toggle_recording, 
            'warning',
            height=1,
            width=18
        )
        self.record_button.pack(side=tk.LEFT, padx=(0, 15))
        
        # Estado de grabación
        self.recording_indicator = tk.Label(
            recording_frame,
            text="○",
            font=self.fonts['title'],
            bg=self.colors['card'],
            fg=self.colors['text_secondary']
        )
        self.recording_indicator.pack(side=tk.LEFT)
        
        self.recording_label = tk.Label(
            recording_frame,
            text="No grabando",
            font=self.fonts['body'],
            bg=self.colors['card'],
            fg=self.colors['text_secondary']
        )
        self.recording_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # Frame para las dos ventanas de video
        videos_container = tk.Frame(main_frame, bg=self.colors['bg'])
        videos_container.pack(fill=tk.BOTH, expand=True)
        
        # Video original
        original_container = tk.Frame(videos_container, bg=self.colors['card'])
        original_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        original_header = tk.Frame(original_container, bg=self.colors['card'], height=40)
        original_header.pack(fill=tk.X, padx=15, pady=(10, 0))
        
        original_title = tk.Label(
            original_header,
            text="VIDEO ORIGINAL",
            font=self.fonts['small'],
            bg=self.colors['card'],
            fg=self.colors['text_secondary']
        )
        original_title.pack(side=tk.LEFT)
        
        self.label_original = tk.Label(
            original_container,
            bg=self.colors['gray'],
            relief=tk.FLAT
        )
        self.label_original.pack(expand=True, padx=15, pady=(5, 15))
        
        # Video filtrado
        filtered_container = tk.Frame(videos_container, bg=self.colors['card'])
        filtered_container.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        filtered_header = tk.Frame(filtered_container, bg=self.colors['card'], height=40)
        filtered_header.pack(fill=tk.X, padx=15, pady=(10, 0))
        
        filtered_title = tk.Label(
            filtered_header,
            text="VIDEO CON FILTRO",
            font=self.fonts['small'],
            bg=self.colors['card'],
            fg=self.colors['text_secondary']
        )
        filtered_title.pack(side=tk.LEFT)
        
        # Etiqueta del filtro aplicado
        self.filter_indicator = tk.Label(
            filtered_header,
            text="",
            font=self.fonts['small'],
            bg=self.colors['card'],
            fg=self.colors['accent']
        )
        self.filter_indicator.pack(side=tk.RIGHT)
        
        self.label_filtered = tk.Label(
            filtered_container,
            bg=self.colors['gray'],
            relief=tk.FLAT
        )
        self.label_filtered.pack(expand=True, padx=15, pady=(5, 15))
        
        # Barra de información inferior
        info_bar = tk.Frame(main_frame, bg=self.colors['card'], height=40)
        info_bar.pack(fill=tk.X, pady=(15, 0))
        
        self.info_label = tk.Label(
            info_bar,
            text="Listo para procesar video",
            font=self.fonts['body'],
            bg=self.colors['card'],
            fg=self.colors['text_secondary']
        )
        self.info_label.pack(side=tk.LEFT, padx=15, pady=10)
        
        # Mensaje de ayuda
        help_label = tk.Label(
            info_bar,
            text="ESC para cerrar",
            font=self.fonts['small'],
            bg=self.colors['card'],
            fg=self.colors['accent']
        )
        help_label.pack(side=tk.RIGHT, padx=15, pady=10)
        
        # Mensaje inicial
        self.show_placeholder()
        
        # Vincular cambio de filtro
        self.current_filter.trace('w', self.on_filter_change)
        
    def create_styled_button(self, parent, text, command, color_key, width=None, height=None):
        """Crea botones con estilo moderno"""
        button = tk.Button(
            parent,
            text=text,
            command=command,
            font=self.fonts['button'],
            bg=self.colors[color_key],
            fg='white',
            relief=tk.FLAT,
            padx=25,
            pady=12 if height is None else height * 6,
            cursor='hand2',
            borderwidth=0,
            activebackground=self.lighten_color(self.colors[color_key]),
            activeforeground='white'
        )
        
        if width:
            button.config(width=width)
        
        # Efecto hover
        button.bind("<Enter>", lambda e, b=button, c=color_key: self.on_button_enter(b, c))
        button.bind("<Leave>", lambda e, b=button, c=color_key: self.on_button_leave(b, c))
        
        return button
        
    def on_button_enter(self, button, color_key):
        button.config(bg=self.lighten_color(self.colors[color_key]))
        
    def on_button_leave(self, button, color_key):
        button.config(bg=self.colors[color_key])
        
    def lighten_color(self, color):
        """Aclara un color para efectos hover"""
        if color == '#4a9eff':
            return '#7ab8ff'
        elif color == '#00c853':
            return '#2ed573'
        elif color == '#ff6d00':
            return '#ff9500'
        elif color == '#ff3d00':
            return '#ff6b5f'
        return color
        
    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def on_filter_change(self, *args):
        """Actualiza el indicador cuando cambia el filtro"""
        filter_name = self.current_filter.get()
        if filter_name and filter_name != "Selecciona un filtro":
            self.filter_indicator.config(text=f"Filtro: {filter_name}")
    
    def show_placeholder(self):
        placeholder = np.ones((400, 600, 3), dtype=np.uint8) * 30
        placeholder = cv2.putText(placeholder, "No hay video cargado", (150, 180), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 1, (100, 100, 100), 2)
        placeholder = cv2.putText(placeholder, "Selecciona una fuente de video", (120, 240), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.8, (80, 80, 80), 2)
        self.show_image(placeholder, self.label_original)
        self.show_image(placeholder, self.label_filtered)
    
    def start_webcam(self):
        self.stop_video()
        self.video_capture = cv2.VideoCapture(0)
        if self.video_capture.isOpened():
            self.video_active = True
            self.info_label.config(text="Cámara en vivo - Aplicando filtros en tiempo real")
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
                self.info_label.config(text=f"Reproduciendo: {os.path.basename(file_path)}")
                self.update_video()
            else:
                self.show_error("No se pudo cargar el video")
    
    def stop_video(self):
        self.video_active = False
        if self.recording:
            self.toggle_recording()
        if self.video_capture:
            self.video_capture.release()
            self.video_capture = None
        self.show_placeholder()
        self.info_label.config(text="Video detenido")
        self.filter_indicator.config(text="")
    
    def toggle_recording(self):
        if not self.video_active:
            self.show_error("No hay video activo para grabar")
            return
            
        if not self.recording:
            # Iniciar grabación
            filter_name = self.current_filter.get().replace(" ", "_")
            filename = f"filtro_{filter_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.avi"
            filepath = os.path.join(self.video_dir, filename)
            
            # Obtener dimensiones del frame
            if self.video_capture and self.video_capture.isOpened():
                ret, frame = self.video_capture.read()
                if ret:
                    h, w = frame.shape[:2]
                    # Resetear posición
                    if hasattr(self.video_capture, 'set'):
                        self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
                else:
                    h, w = 480, 640
            else:
                h, w = 480, 640
            
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            self.out_video = cv2.VideoWriter(filepath, fourcc, 20.0, (w*2, h))
            self.recording = True
            self.recording_start_time = time.time()
            
            # Actualizar UI
            self.record_button.config(text="Detener Grabación", bg=self.colors['error'])
            self.recording_indicator.config(text="●", fg=self.colors['error'])
            self.recording_label.config(text="Grabando...")
            self.info_label.config(text=f"Grabando: {os.path.basename(filepath)}")
        else:
            # Detener grabación
            self.recording = False
            if self.out_video:
                self.out_video.release()
                self.out_video = None
            
            # Actualizar UI
            self.record_button.config(text="Iniciar Grabación", bg=self.colors['warning'])
            self.recording_indicator.config(text="○", fg=self.colors['text_secondary'])
            self.recording_label.config(text="No grabando")
            
            recording_time = time.time() - self.recording_start_time
            self.info_label.config(text=f"Video guardado - Duración: {recording_time:.1f} segundos")
    
    def update_video(self):
        if self.video_active and self.video_capture:
            ret, frame = self.video_capture.read()
            if ret:
                self.process_and_display(frame)
                self.root.after(30, self.update_video)
            else:
                # Reiniciar video si llegó al final
                if isinstance(self.video_capture, cv2.VideoCapture):
                    self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    self.root.after(30, self.update_video)
    
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
            if filter_name == "Suavizado Gaussiano":
                return cv2.GaussianBlur(frame, (5, 5), 0)
                
            elif filter_name == "Filtro de Promedio":
                return cv2.blur(frame, (5, 5))
                
            elif filter_name == "Filtro de Mediana":
                return cv2.medianBlur(frame, 5)
                
            elif filter_name == "Detección de Bordes Canny":
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                canny = cv2.Canny(gray, 100, 200)
                return cv2.cvtColor(canny, cv2.COLOR_GRAY2BGR)
                
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
                
            elif filter_name == "Binarización Otsu":
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                _, thresh = cv2.threshold(
                    gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
                )
                return cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)
                
            elif filter_name == "Convolución 2D":
                kernel = np.ones((5, 5), np.float32) / 25
                return cv2.filter2D(frame, -1, kernel)
                
            elif filter_name == "Filtro Bilateral":
                return cv2.bilateralFilter(frame, 9, 75, 75)
                
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
        error_window.geometry("350x150")
        
        error_window.update_idletasks()
        x = (error_window.winfo_screenwidth() // 2) - (350 // 2)
        y = (error_window.winfo_screenheight() // 2) - (150 // 2)
        error_window.geometry(f'350x150+{x}+{y}')
        
        error_label = tk.Label(
            error_window,
            text=message,
            font=self.fonts['body'],
            bg=self.colors['card'],
            fg=self.colors['error'],
            wraplength=250
        )
        error_label.pack(expand=True, padx=20, pady=20)
        
        close_button = tk.Button(
            error_window,
            text="OK",
            command=error_window.destroy,
            font=self.fonts['button'],
            bg=self.colors['accent'],
            fg='white',
            relief=tk.FLAT,
            padx=40,
            pady=8,
            cursor='hand2',
            activebackground=self.colors['accent_hover'],
            activeforeground='white'
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
