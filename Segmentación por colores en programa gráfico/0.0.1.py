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
        self.selector_manual_activo = False
        self.punto_seleccionado = None
        self.ventana_selector = None  # Para controlar la ventana selector
        
        # Crear interfaz
        self.crear_interfaz()
        
        # Bind teclas
        self.root.bind('<Escape>', self.cerrar_ventana_grande)
        
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
        
        # Botón seleccionar color con selector
        ttk.Button(control_frame, text="Seleccionar Color (Selector)", 
                  command=self.seleccionar_color).pack(side=tk.LEFT, padx=5)
        
        # Botón seleccionar color de la imagen
        ttk.Button(control_frame, text="Seleccionar Color de Imagen", 
                  command=self.activar_selector_manual).pack(side=tk.LEFT, padx=5)
        
        # Label para mostrar color seleccionado
        self.color_label = tk.Label(control_frame, width=10, height=2, 
                                   bg='#00FF00')  # Verde por defecto
        self.color_label.pack(side=tk.LEFT, padx=5)
        
        # Valores RGB del color seleccionado
        self.rgb_label = ttk.Label(control_frame, text="RGB: (0,255,0)")
        self.rgb_label.pack(side=tk.LEFT, padx=5)
        
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
        espacio_combo.bind('<<ComboboxSelected>>', lambda e: self.aplicar_segmentacion())
        
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
        self.label_original.bind('<Button-1>', lambda e: self.mostrar_imagen_grande('original'))
        
        # Máscara
        mascara_frame = ttk.LabelFrame(imagenes_frame, text="Máscara", padding="5")
        mascara_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.label_mascara = ttk.Label(mascara_frame)
        self.label_mascara.pack()
        self.label_mascara.bind('<Button-1>', lambda e: self.mostrar_imagen_grande('mascara'))
        
        # Imagen segmentada
        segmentada_frame = ttk.LabelFrame(imagenes_frame, text="Imagen Segmentada", padding="5")
        segmentada_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.label_segmentada = ttk.Label(segmentada_frame)
        self.label_segmentada.pack()
        self.label_segmentada.bind('<Button-1>', lambda e: self.mostrar_imagen_grande('segmentada'))
        
    def mostrar_imagen_grande(self, tipo_imagen):
        """Muestra la imagen seleccionada en una ventana grande"""
        if self.img_original is None:
            return
            
        # Crear ventana
        self.ventana_grande = tk.Toplevel(self.root)
        self.ventana_grande.title(f"Imagen {tipo_imagen.capitalize()} - Presiona ESC o X para cerrar")
        self.ventana_grande.geometry("800x600")
        
        # Bind teclas
        self.ventana_grande.bind('<Escape>', self.cerrar_ventana_grande)
        
        # Frame para la imagen
        frame_imagen = ttk.Frame(self.ventana_grande)
        frame_imagen.pack(fill=tk.BOTH, expand=True)
        
        # Label para la imagen
        label_imagen_grande = ttk.Label(frame_imagen)
        label_imagen_grande.pack()
        
        # Botón cerrar
        boton_frame = ttk.Frame(self.ventana_grande)
        boton_frame.pack(pady=10)
        
        ttk.Button(boton_frame, text="Cerrar (X)", 
                  command=self.cerrar_ventana_grande).pack()
        
        # Obtener imagen según tipo
        if tipo_imagen == 'original':
            imagen = self.img_original.copy()
        elif tipo_imagen == 'mascara':
            # Aplicar segmentación para obtener máscara actual
            espacio = self.espacio_color.get()
            tolerancia = self.tolerancia_var.get()
            mascara = self.segmentar_por_color(self.img_original, 
                                              self.color_seleccionado, 
                                              tolerancia, 
                                              espacio)
            imagen = mascara
        else:  # segmentada
            espacio = self.espacio_color.get()
            tolerancia = self.tolerancia_var.get()
            mascara = self.segmentar_por_color(self.img_original, 
                                              self.color_seleccionado, 
                                              tolerancia, 
                                              espacio)
            imagen = cv2.bitwise_and(self.img_original, self.img_original, mask=mascara)
        
        # Mostrar imagen en la ventana grande
        self.mostrar_imagen_en_ventana(imagen, label_imagen_grande)
        
        # Guardar referencia
        self.label_imagen_grande = label_imagen_grande
        self.ventana_grande.protocol("WM_DELETE_WINDOW", self.cerrar_ventana_grande)
        
    def mostrar_imagen_en_ventana(self, imagen, label):
        """Muestra una imagen en un label, redimensionada para la ventana"""
        if len(imagen.shape) == 2:  # Escala de grises
            imagen_rgb = cv2.cvtColor(imagen, cv2.COLOR_GRAY2RGB)
        else:
            imagen_rgb = cv2.cvtColor(imagen, cv2.COLOR_BGR2RGB)
        
        # Redimensionar para la ventana
        alto, ancho = imagen_rgb.shape[:2]
        max_dim = 700
        
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
        label.image = imagen_tk
        
    def cerrar_ventana_grande(self, event=None):
        """Cierra la ventana de imagen grande"""
        if hasattr(self, 'ventana_grande') and self.ventana_grande:
            self.ventana_grande.destroy()
            self.ventana_grande = None
            
    def activar_selector_manual(self):
        """Activa el modo de selección manual de color desde la imagen"""
        if self.img_original is None:
            tk.messagebox.showwarning("Advertencia", "Primero carga una imagen")
            return
            
        # Si ya hay una ventana selector abierta, cerrarla primero
        if self.ventana_selector and self.ventana_selector.winfo_exists():
            self.ventana_selector.destroy()
            
        self.selector_manual_activo = True
        self.punto_seleccionado = None
        
        # Crear ventana para selección manual
        self.ventana_selector = tk.Toplevel(self.root)
        self.ventana_selector.title("Selecciona un color - Haz clic en la imagen")
        self.ventana_selector.geometry("800x600")
        
        # Frame para la imagen
        frame_imagen = ttk.Frame(self.ventana_selector)
        frame_imagen.pack(fill=tk.BOTH, expand=True)
        
        # Label para la imagen
        self.label_selector = ttk.Label(frame_imagen)
        self.label_selector.pack()
        self.label_selector.bind('<Button-1>', self.seleccionar_color_de_imagen)
        
        # Botón cancelar
        ttk.Button(self.ventana_selector, text="Cancelar", 
                  command=self.cancelar_selector).pack(pady=10)
        
        # Mostrar imagen
        self.mostrar_imagen_en_ventana(self.img_original, self.label_selector)
        
        # Instrucciones
        ttk.Label(self.ventana_selector, 
                 text="Haz clic en la imagen para seleccionar un color").pack()
        
        # Configurar cierre de ventana
        self.ventana_selector.protocol("WM_DELETE_WINDOW", self.cancelar_selector)
        
    def cancelar_selector(self):
        """Cancela la selección manual y cierra la ventana"""
        self.selector_manual_activo = False
        if self.ventana_selector:
            self.ventana_selector.destroy()
            self.ventana_selector = None
        
    def seleccionar_color_de_imagen(self, event):
        """Selecciona el color del punto donde se hizo clic"""
        try:
            # Obtener coordenadas relativas a la imagen
            x = event.x
            y = event.y
            
            # Obtener dimensiones de la imagen mostrada
            imagen_mostrada = self.label_selector.image
            if not imagen_mostrada:
                return
                
            # Calcular proporciones
            alto_original, ancho_original = self.img_original.shape[:2]
            alto_mostrado = imagen_mostrada.height()
            ancho_mostrado = imagen_mostrada.width()
            
            # Mapear coordenadas a la imagen original
            x_original = int(x * ancho_original / ancho_mostrado)
            y_original = int(y * alto_original / alto_mostrado)
            
            # Asegurar que está dentro de los límites
            x_original = min(max(x_original, 0), ancho_original - 1)
            y_original = min(max(y_original, 0), alto_original - 1)
            
            # Obtener color BGR
            self.color_seleccionado = tuple(map(int, self.img_original[y_original, x_original]))
            
            # Actualizar label de color
            color_rgb = (self.color_seleccionado[2],  # R
                        self.color_seleccionado[1],   # G
                        self.color_seleccionado[0])   # B
            
            color_hex = '#{:02x}{:02x}{:02x}'.format(color_rgb[0], color_rgb[1], color_rgb[2])
            self.color_label.config(bg=color_hex)
            
            # Actualizar label RGB
            self.rgb_label.config(text=f"RGB: {color_rgb}")
            
            print(f"Color seleccionado de imagen - BGR: {self.color_seleccionado}, RGB: {color_rgb}")
            
            # Cerrar ventana selector
            self.cancelar_selector()
            
            # Forzar actualización de la segmentación
            self.root.after(100, self.aplicar_segmentacion)
            
        except Exception as e:
            print(f"Error al seleccionar color: {e}")
            self.cancelar_selector()
        
    def cargar_imagen(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Imágenes", "*.jpg *.jpeg *.png *.bmp *.tiff")]
        )
        
        if file_path:
            self.img_original = cv2.imread(file_path)
            self.mostrar_imagen(self.img_original, self.label_original)
            # Aplicar segmentación inicial
            self.aplicar_segmentacion()
            
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
            
            # Actualizar label RGB
            self.rgb_label.config(text=f"RGB: ({int(color_rgb[0])}, {int(color_rgb[1])}, {int(color_rgb[2])})")
            
            print(f"Color seleccionado (BGR): {self.color_seleccionado}")
            
            # Actualizar la segmentación inmediatamente
            self.aplicar_segmentacion()
            
    def actualizar_tolerancia(self, value):
        tolerancia = int(float(value))
        self.tolerancia_var.set(tolerancia)
        self.tolerancia_label.config(text=str(tolerancia))
        # Actualizar la segmentación cuando cambia la tolerancia
        if self.img_original is not None:
            self.aplicar_segmentacion()
        
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
            return
            
        # Obtener espacio de color seleccionado
        espacio = self.espacio_color.get()
        tolerancia = self.tolerancia_var.get()
        
        print(f"Aplicando segmentación - Color: {self.color_seleccionado}, Tolerancia: {tolerancia}, Espacio: {espacio}")
        
        try:
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
            
        except Exception as e:
            print(f"Error en segmentación: {e}")
        
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
