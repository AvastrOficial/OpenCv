import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, ttk, colorchooser
from PIL import Image, ImageTk

class SegmentacionColoresApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Segmentación por Colores - OpenCV")
        self.root.geometry("1200x600")
        
        # Variables
        self.img_original = None
        self.color_seleccionado = (0, 255, 0)  # Verde por defecto (BGR)
        self.tolerancia = 40  # Tolerancia para el rango de color
        
        # Crear interfaz
        self.crear_interfaz()
        
    def crear_interfaz(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Frame de controles
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=5)
        
        # Botón cargar imagen
        ttk.Button(control_frame, text="Cargar Imagen", 
                  command=self.cargar_imagen).pack(side=tk.LEFT, padx=5)
        
        # Botón seleccionar color
        ttk.Button(control_frame, text="Seleccionar Color", 
                  command=self.seleccionar_color).pack(side=tk.LEFT, padx=5)
        
        # Label para mostrar color seleccionado
        self.color_label = tk.Label(control_frame, width=10, height=2, 
                                   bg='#00FF00')  # Verde por defecto
        self.color_label.pack(side=tk.LEFT, padx=5)
        
        # Control de tolerancia
        ttk.Label(control_frame, text="Tolerancia:").pack(side=tk.LEFT, padx=5)
        self.tolerancia_var = tk.IntVar(value=40)
        self.tolerancia_slider = ttk.Scale(control_frame, from_=0, to=100, 
                                          orient=tk.HORIZONTAL, 
                                          variable=self.tolerancia_var,
                                          command=self.actualizar_tolerancia)
        self.tolerancia_slider.pack(side=tk.LEFT, padx=5)
        
        self.tolerancia_label = ttk.Label(control_frame, text="40")
        self.tolerancia_label.pack(side=tk.LEFT, padx=5)
        
        # Espacio de colores
        ttk.Label(control_frame, text="Espacio de Color:").pack(side=tk.LEFT, padx=5)
        self.espacio_color = tk.StringVar(value="RGB")
        espacio_combo = ttk.Combobox(control_frame, textvariable=self.espacio_color,
                                     values=["RGB", "HSV", "LAB"], state="readonly")
        espacio_combo.pack(side=tk.LEFT, padx=5)
        
        # Botón aplicar segmentación
        ttk.Button(control_frame, text="Aplicar Segmentación", 
                  command=self.aplicar_segmentacion).pack(side=tk.LEFT, padx=20)
        
        # Frame para imágenes
        imagenes_frame = ttk.Frame(main_frame)
        imagenes_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Imagen original
        original_frame = ttk.LabelFrame(imagenes_frame, text="Imagen Original", padding="5")
        original_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.label_original = ttk.Label(original_frame)
        self.label_original.pack()
        
        # Máscara
        mascara_frame = ttk.LabelFrame(imagenes_frame, text="Máscara", padding="5")
        mascara_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.label_mascara = ttk.Label(mascara_frame)
        self.label_mascara.pack()
        
        # Imagen segmentada
        segmentada_frame = ttk.LabelFrame(imagenes_frame, text="Imagen Segmentada", padding="5")
        segmentada_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.label_segmentada = ttk.Label(segmentada_frame)
        self.label_segmentada.pack()
        
    def cargar_imagen(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Imágenes", "*.jpg *.jpeg *.png *.bmp *.tiff")]
        )
        
        if file_path:
            self.img_original = cv2.imread(file_path)
            self.mostrar_imagen(self.img_original, self.label_original)
            
    def seleccionar_color(self):
        # Selector de color de tkinter (devuelve RGB)
        color_rgb = colorchooser.askcolor(title="Selecciona un color", 
                                         color='#00FF00')[0]
        
        if color_rgb:
            # Convertir de RGB a BGR (OpenCV usa BGR)
            self.color_seleccionado = (int(color_rgb[2]),  # B
                                      int(color_rgb[1]),  # G
                                      int(color_rgb[0]))  # R
            
            # Actualizar label de color
            color_hex = '#{:02x}{:02x}{:02x}'.format(int(color_rgb[0]), 
                                                     int(color_rgb[1]), 
                                                     int(color_rgb[2]))
            self.color_label.config(bg=color_hex)
            
            print(f"Color seleccionado (BGR): {self.color_seleccionado}")
            
    def actualizar_tolerancia(self, value):
        tolerancia = int(float(value))
        self.tolerancia_var.set(tolerancia)
        self.tolerancia_label.config(text=str(tolerancia))
        
    def segmentar_por_color(self, imagen, color_bgr, tolerancia, espacio):
        if espacio == "RGB":
            return self.segmentar_rgb(imagen, color_bgr, tolerancia)
        elif espacio == "HSV":
            return self.segmentar_hsv(imagen, color_bgr, tolerancia)
        elif espacio == "LAB":
            return self.segmentar_lab(imagen, color_bgr, tolerancia)
            
    def segmentar_rgb(self, imagen, color_bgr, tolerancia):
        # Crear rango de colores en BGR
        lower = np.array([max(0, color_bgr[0] - tolerancia),
                         max(0, color_bgr[1] - tolerancia),
                         max(0, color_bgr[2] - tolerancia)])
        upper = np.array([min(255, color_bgr[0] + tolerancia),
                         min(255, color_bgr[1] + tolerancia),
                         min(255, color_bgr[2] + tolerancia)])
        
        # Crear máscara
        mascara = cv2.inRange(imagen, lower, upper)
        return mascara
        
    def segmentar_hsv(self, imagen, color_bgr, tolerancia):
        # Convertir a HSV
        imagen_hsv = cv2.cvtColor(imagen, cv2.COLOR_BGR2HSV)
        color_hsv = cv2.cvtColor(np.uint8([[color_bgr]]), cv2.COLOR_BGR2HSV)[0][0]
        
        # En HSV, el matiz es circular (0-180)
        lower = np.array([max(0, color_hsv[0] - tolerancia//2),
                         max(0, color_hsv[1] - tolerancia),
                         max(0, color_hsv[2] - tolerancia)])
        upper = np.array([min(180, color_hsv[0] + tolerancia//2),
                         min(255, color_hsv[1] + tolerancia),
                         min(255, color_hsv[2] + tolerancia)])
        
        mascara = cv2.inRange(imagen_hsv, lower, upper)
        return mascara
        
    def segmentar_lab(self, imagen, color_bgr, tolerancia):
        # Convertir a LAB
        imagen_lab = cv2.cvtColor(imagen, cv2.COLOR_BGR2LAB)
        color_lab = cv2.cvtColor(np.uint8([[color_bgr]]), cv2.COLOR_BGR2LAB)[0][0]
        
        lower = np.array([max(0, color_lab[0] - tolerancia),
                         max(0, color_lab[1] - tolerancia),
                         max(0, color_lab[2] - tolerancia)])
        upper = np.array([min(255, color_lab[0] + tolerancia),
                         min(255, color_lab[1] + tolerancia),
                         min(255, color_lab[2] + tolerancia)])
        
        mascara = cv2.inRange(imagen_lab, lower, upper)
        return mascara
        
    def aplicar_segmentacion(self):
        if self.img_original is None:
            tk.messagebox.showwarning("Advertencia", "Primero carga una imagen")
            return
            
        # Obtener espacio de color seleccionado
        espacio = self.espacio_color.get()
        tolerancia = self.tolerancia_var.get()
        
        # Aplicar segmentación
        mascara = self.segmentar_por_color(self.img_original, 
                                          self.color_seleccionado, 
                                          tolerancia, 
                                          espacio)
        
        # Crear imagen segmentada (solo el color seleccionado)
        imagen_segmentada = cv2.bitwise_and(self.img_original, 
                                           self.img_original, 
                                           mask=mascara)
        
        # Mostrar resultados
        self.mostrar_imagen(self.img_original, self.label_original)
        self.mostrar_imagen(mascara, self.label_mascara, is_gray=True)
        self.mostrar_imagen(imagen_segmentada, self.label_segmentada)
        
    def mostrar_imagen(self, imagen, label, is_gray=False):
        if is_gray:
            # Para imágenes en escala de grises (máscara)
            imagen_rgb = cv2.cvtColor(imagen, cv2.COLOR_GRAY2RGB)
        else:
            # Convertir BGR a RGB para mostrar correctamente
            imagen_rgb = cv2.cvtColor(imagen, cv2.COLOR_BGR2RGB)
        
        # Redimensionar para mantener proporción
        alto, ancho = imagen_rgb.shape[:2]
        max_dim = 350
        
        if alto > max_dim or ancho > max_dim:
            escala = max_dim / max(alto, ancho)
            nuevo_alto = int(alto * escala)
            nuevo_ancho = int(ancho * escala)
            imagen_rgb = cv2.resize(imagen_rgb, (nuevo_ancho, nuevo_alto))
        
        # Convertir a PhotoImage
        imagen_pil = Image.fromarray(imagen_rgb)
        imagen_tk = ImageTk.PhotoImage(imagen_pil)
        
        # Actualizar label
        label.configure(image=imagen_tk)
        label.image = imagen_tk  # Mantener referencia

def main():
    root = tk.Tk()
    app = SegmentacionColoresApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
