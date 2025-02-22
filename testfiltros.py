import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog
from tkinter import colorchooser
from PIL import Image, ImageTk

# Función para abrir el archivo de imagen
def cargar_imagen():
    archivo = filedialog.askopenfilename(filetypes=[("Imagenes", "*.jpg;*.png;*.jpeg")])
    if archivo:
        # Cargar la imagen
        imagen = cv2.imread(archivo)
        imagen_rgb = cv2.cvtColor(imagen, cv2.COLOR_BGR2RGB)
        
        # Mostrar la imagen original en la interfaz
        imagen_pil = Image.fromarray(imagen_rgb)
        imagen_tk = ImageTk.PhotoImage(imagen_pil)
        label_imagen_original.config(image=imagen_tk)
        label_imagen_original.image = imagen_tk
        
        # Guardar la imagen para usarla en otras funciones
        global img_original
        img_original = imagen

# Función para seleccionar el color
def seleccionar_color():
    color = colorchooser.askcolor()[0]
    if color:
        # Convertir color seleccionado a HSV
        global color_hsv
        color_hsv = np.array([[[color[0], color[1], color[2]]]], dtype=np.uint8)
        color_hsv = cv2.cvtColor(color_hsv, cv2.COLOR_RGB2HSV)[0][0]
        label_color_seleccionado.config(bg=colorchooser.askcolor()[1])
        
# Función para aplicar la segmentación por color
def segmentar_color():
    if 'img_original' not in globals():
        return
    
    # Convertir la imagen a HSV
    imagen_hsv = cv2.cvtColor(img_original, cv2.COLOR_BGR2HSV)
    
    # Definir los rangos de color
    lower_bound = np.array([color_hsv[0] - 10, 50, 50])
    upper_bound = np.array([color_hsv[0] + 10, 255, 255])
    
    # Crear la máscara
    mascara = cv2.inRange(imagen_hsv, lower_bound, upper_bound)
    
    # Aplicar la máscara a la imagen original
    resultado = cv2.bitwise_and(img_original, img_original, mask=mascara)
    
    # Mostrar los resultados
    mascara_rgb = cv2.cvtColor(mascara, cv2.COLOR_GRAY2RGB)
    
    # Mostrar imágenes en Tkinter
    mostrar_imagen(imagen_rgb, label_imagen_original)  # Imagen original
    mostrar_imagen(mascara_rgb, label_imagen_mascara)  # Máscara
    mostrar_imagen(resultado, label_imagen_resultado)  # Imagen resultante

# Función para mostrar una imagen en un label de Tkinter
def mostrar_imagen(imagen, label):
    imagen_pil = Image.fromarray(imagen)
    imagen_tk = ImageTk.PhotoImage(imagen_pil)
    label.config(image=imagen_tk)
    label.image = imagen_tk

# Crear la interfaz gráfica con Tkinter
ventana = tk.Tk()
ventana.title("Segmentación por Colores")

# Botón para cargar la imagen
boton_cargar_imagen = tk.Button(ventana, text="Cargar Imagen", command=cargar_imagen)
boton_cargar_imagen.pack()

# Botón para seleccionar el color
boton_seleccionar_color = tk.Button(ventana, text="Seleccionar Color", command=seleccionar_color)
boton_seleccionar_color.pack()

# Botón para segmentar la imagen
boton_segmentar = tk.Button(ventana, text="Segmentar", command=segmentar_color)
boton_segmentar.pack()

# Etiqueta para mostrar la imagen original
label_imagen_original = tk.Label(ventana)
label_imagen_original.pack()

# Etiqueta para mostrar la máscara
label_imagen_mascara = tk.Label(ventana)
label_imagen_mascara.pack()

# Etiqueta para mostrar la imagen resultante
label_imagen_resultado = tk.Label(ventana)
label_imagen_resultado.pack()

# Etiqueta para mostrar el color seleccionado
label_color_seleccionado = tk.Label(ventana, text="Color Seleccionado", width=20, height=2)
label_color_seleccionado.pack()

# Iniciar la ventana de Tkinter
ventana.mainloop()
