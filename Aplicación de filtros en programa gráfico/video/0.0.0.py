import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from PIL import Image, ImageTk
import threading
import time
import os
from datetime import datetime

class FiltrosVideoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("📹 Aplicación de Filtros para Video - Trabajo Integrador")
        self.root.geometry("1300x750")
        self.root.configure(bg='#f0f0f0')
        
        # Variables de control
        self.cap = None
        self.video_capture = None
        self.is_playing = False
        self.is_recording = False
        self.current_filter = tk.StringVar(value="Original")
        self.video_source = None
        self.out_video = None
        self.recording_filters = []
        self.current_recording_filter = None
        
        # Configurar interfaz
        self.setup_ui()
        
    def setup_ui(self):
        # Frame principal
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Panel de controles superior
        control_frame = tk.Frame(main_frame, bg='#ffffff', relief=tk.RAISED, bd=2)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(control_frame, text="🎥 CONTROL DE VIDEO", font=('Arial', 12, 'bold'),
                bg='#ffffff', fg='#333').pack(pady=5)
        
        # Botones de control
        button_frame = tk.Frame(control_frame, bg='#ffffff')
        button_frame.pack(pady=10)
        
        # Botón cámara en tiempo real
        self.btn_webcam = tk.Button(button_frame, text="📷 Cámara en Tiempo Real", 
                                    command=self.start_webcam,
                                    bg='#2196F3', fg='white', font=('Arial', 10, 'bold'),
                                    padx=15, pady=8, cursor='hand2')
        self.btn_webcam.pack(side=tk.LEFT, padx=5)
        
        # Botón cargar video guardado
        self.btn_load_video = tk.Button(button_frame, text="🎬 Cargar Video Guardado", 
                                        command=self.load_video,
                                        bg='#FF9800', fg='white', font=('Arial', 10, 'bold'),
                                        padx=15, pady=8, cursor='hand2')
        self.btn_load_video.pack(side=tk.LEFT, padx=5)
        
        # Botón detener
        self.btn_stop = tk.Button(button_frame, text="⏹️ Detener", command=self.stop_video,
                                  bg='#f44336', fg='white', font=('Arial', 10, 'bold'),
                                  padx=15, pady=8, cursor='hand2', state=tk.DISABLED)
        self.btn_stop.pack(side=tk.LEFT, padx=5)
        
        # Separador
        ttk.Separator(control_frame, orient='horizontal').pack(fill=tk.X, padx=10, pady=5)
        
        # Panel de filtros
        filter_frame = tk.Frame(control_frame, bg='#ffffff')
        filter_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(filter_frame, text="🎨 SELECCIÓN DE FILTROS", font=('Arial', 11, 'bold'),
                bg='#ffffff', fg='#333').pack(pady=5)
        
        # Radio buttons para filtros
        filters = [
            ("Original", "Sin filtro aplicado"),
            ("Suavizado", "Reduce ruido usando promedio"),
            ("Gaussiano", "Suavizado con kernel gaussiano"),
            ("Mediana", "Elimina ruido sal y pimienta"),
            ("Canny", "Detección de bordes"),
            ("Sobel X", "Detección de bordes horizontales")
        ]
        
        radio_frame = tk.Frame(filter_frame, bg='#ffffff')
        radio_frame.pack(pady=5)
        
        for i, (filter_name, desc) in enumerate(filters):
            rb = tk.Radiobutton(radio_frame, text=filter_name, variable=self.current_filter,
                               value=filter_name, bg='#ffffff', font=('Arial', 9),
                               command=self.update_filter_description)
            rb.grid(row=i//3, column=i%3, padx=10, pady=2, sticky='w')
        
        # Descripción del filtro
        self.filter_desc = tk.Label(filter_frame, text=filters[0][1], bg='#e0e0e0',
                                    font=('Arial', 9), fg='#666', padx=10, pady=5)
        self.filter_desc.pack(pady=5)
        
        # Panel de grabación
        record_frame = tk.Frame(control_frame, bg='#ffffff')
        record_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(record_frame, text="⏺️ GRABACIÓN DE VIDEOS (2 minutos cada uno)", 
                font=('Arial', 11, 'bold'), bg='#ffffff', fg='#333').pack(pady=5)
        
        record_button_frame = tk.Frame(record_frame, bg='#ffffff')
        record_button_frame.pack(pady=5)
        
        # Botones para grabar cada filtro
        record_filters = [
            ("Grabar Original", "Original"),
            ("Grabar Suavizado", "Suavizado"),
            ("Grabar Gaussiano", "Gaussiano"),
            ("Grabar Mediana", "Mediana"),
            ("Grabar Canny", "Canny"),
            ("Grabar Sobel X", "Sobel X")
        ]
        
        for i, (btn_text, filter_name) in enumerate(record_filters):
            btn = tk.Button(record_button_frame, text=btn_text,
                           command=lambda f=filter_name: self.start_recording(f),
                           bg='#4CAF50', fg='white', font=('Arial', 8, 'bold'),
                           padx=8, pady=4, cursor='hand2')
            btn.grid(row=i//3, column=i%3, padx=3, pady=2)
        
        # Panel de estado
        status_frame = tk.Frame(control_frame, bg='#ffffff')
        status_frame.pack(fill=tk.X, pady=5)
        
        self.status_label = tk.Label(status_frame, text="Estado: Esperando acción...",
                                     bg='#e0e0e0', font=('Arial', 9), padx=10, pady=5)
        self.status_label.pack(fill=tk.X, padx=10, pady=5)
        
        # Frame para videos
        video_frame = tk.Frame(main_frame, bg='#f0f0f0')
        video_frame.pack(fill=tk.BOTH, expand=True)
        
        # Video original
        original_frame = tk.Frame(video_frame, bg='#333', relief=tk.SUNKEN, bd=2)
        original_frame.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.BOTH, expand=True)
        
        tk.Label(original_frame, text="🎬 VIDEO ORIGINAL", bg='#333', fg='white',
                font=('Arial', 10, 'bold')).pack(pady=2)
        self.label_original = tk.Label(original_frame, bg='#000')
        self.label_original.pack(padx=5, pady=5, expand=True)
        
        # Video filtrado
        filtered_frame = tk.Frame(video_frame, bg='#333', relief=tk.SUNKEN, bd=2)
        filtered_frame.pack(side=tk.RIGHT, padx=5, pady=5, fill=tk.BOTH, expand=True)
        
        tk.Label(filtered_frame, text="🎨 VIDEO CON FILTRO", bg='#333', fg='white',
                font=('Arial', 10, 'bold')).pack(pady=2)
        self.label_filtered = tk.Label(filtered_frame, bg='#000')
        self.label_filtered.pack(padx=5, pady=5, expand=True)
        
    def update_filter_description(self):
        descripciones = {
            "Original": "Sin filtro aplicado - Video original",
            "Suavizado": "Filtro de suavizado: Reduce el ruido aplicando un promedio de píxeles vecinos",
            "Gaussiano": "Filtro Gaussiano: Suavizado ponderado basado en distribución gaussiana",
            "Mediana": "Filtro de Mediana: Excelente para eliminar ruido sal y pimienta",
            "Canny": "Detector de bordes Canny: Ideal para encontrar contornos en imágenes",
            "Sobel X": "Filtro Sobel en X: Detecta bordes horizontales en la imagen"
        }
        self.filter_desc.config(text=descripciones.get(self.current_filter.get(), ""))
    
    def apply_filter(self, frame):
        filter_name = self.current_filter.get()
        
        if filter_name == "Original":
            return frame
        elif filter_name == "Suavizado":
            return cv2.blur(frame, (5, 5))
        elif filter_name == "Gaussiano":
            return cv2.GaussianBlur(frame, (5, 5), 0)
        elif filter_name == "Mediana":
            return cv2.medianBlur(frame, 5)
        elif filter_name == "Canny":
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 100, 200)
            return cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        elif filter_name == "Sobel X":
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=5)
            sobelx = np.uint8(np.absolute(sobelx))
            return cv2.cvtColor(sobelx, cv2.COLOR_GRAY2BGR)
        
        return frame
    
    def start_webcam(self):
        self.stop_video()
        self.video_source = "webcam"
        self.cap = cv2.VideoCapture(0)
        
        if not self.cap.isOpened():
            messagebox.showerror("Error", "No se pudo abrir la cámara web")
            return
        
        self.is_playing = True
        self.btn_webcam.config(state=tk.DISABLED)
        self.btn_load_video.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)
        self.status_label.config(text="Estado: Cámara en tiempo real activa")
        
        self.play_video()
    
    def load_video(self):
        file_path = filedialog.askopenfilename(
            title="Seleccionar video",
            filetypes=[("Archivos de video", "*.mp4 *.avi *.mov *.mkv")]
        )
        
        if file_path:
            self.stop_video()
            self.video_source = file_path
            self.cap = cv2.VideoCapture(file_path)
            
            if not self.cap.isOpened():
                messagebox.showerror("Error", "No se pudo abrir el archivo de video")
                return
            
            self.is_playing = True
            self.btn_webcam.config(state=tk.DISABLED)
            self.btn_load_video.config(state=tk.DISABLED)
            self.btn_stop.config(state=tk.NORMAL)
            self.status_label.config(text=f"Estado: Reproduciendo {os.path.basename(file_path)}")
            
            self.play_video()
    
    def stop_video(self):
        self.is_playing = False
        if self.is_recording:
            self.stop_recording()
        
        if self.cap:
            self.cap.release()
            self.cap = None
        
        self.btn_webcam.config(state=tk.NORMAL)
        self.btn_load_video.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.DISABLED)
        self.status_label.config(text="Estado: Video detenido")
        
        # Limpiar displays
        self.label_original.config(image='')
        self.label_filtered.config(image='')
    
    def play_video(self):
        if not self.is_playing or self.cap is None:
            return
        
        ret, frame = self.cap.read()
        
        if ret:
            # Aplicar filtro
            filtered_frame = self.apply_filter(frame)
            
            # Si está grabando, guardar frame
            if self.is_recording and self.out_video:
                self.out_video.write(filtered_frame)
            
            # Convertir para mostrar
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            filtered_rgb = cv2.cvtColor(filtered_frame, cv2.COLOR_BGR2RGB)
            
            self.show_frame(frame_rgb, self.label_original)
            self.show_frame(filtered_rgb, self.label_filtered)
            
            # Programar siguiente frame
            self.root.after(30, self.play_video)
        else:
            if self.video_source != "webcam":
                self.stop_video()
                messagebox.showinfo("Fin del video", "El video ha terminado")
    
    def show_frame(self, frame, label):
        image = Image.fromarray(frame)
        image.thumbnail((500, 400))
        imgtk = ImageTk.PhotoImage(image=image)
        label.imgtk = imgtk
        label.configure(image=imgtk)
    
    def start_recording(self, filter_name):
        if not self.is_playing:
            messagebox.showwarning("Advertencia", "Debes iniciar un video primero")
            return
        
        if self.is_recording:
            messagebox.showwarning("Advertencia", "Ya hay una grabación en curso")
            return
        
        # Crear directorio para grabaciones si no existe
        if not os.path.exists("grabaciones"):
            os.makedirs("grabaciones")
        
        # Guardar filtro actual
        original_filter = self.current_filter.get()
        self.current_filter.set(filter_name)
        
        # Configurar grabación
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"grabaciones/video_{filter_name}_{timestamp}.avi"
        
        # Obtener dimensiones del video
        if self.cap:
            width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = int(self.cap.get(cv2.CAP_PROP_FPS))
            
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            self.out_video = cv2.VideoWriter(filename, fourcc, fps, (width, height))
            
            self.is_recording = True
            self.current_recording_filter = filter_name
            
            self.status_label.config(text=f"Estado: Grabando {filter_name} - 2 minutos...")
            
            # Programar parada después de 2 minutos
            self.root.after(120000, self.stop_recording)
    
    def stop_recording(self):
        if self.is_recording:
            self.is_recording = False
            if self.out_video:
                self.out_video.release()
                self.out_video = None
            
            self.status_label.config(text=f"Estado: Grabación de {self.current_recording_filter} completada")
            
            # Restaurar filtro original
            if hasattr(self, 'current_recording_filter'):
                self.current_filter.set("Original")
                self.current_recording_filter = None
            
            messagebox.showinfo("Grabación completada", 
                               f"Video con filtro {self.current_recording_filter} guardado en carpeta 'grabaciones'")
    
    def __del__(self):
        if self.cap:
            self.cap.release()
        if self.out_video:
            self.out_video.release()

if __name__ == "__main__":
    root = tk.Tk()
    app = FiltrosVideoApp(root)
    root.mainloop()
