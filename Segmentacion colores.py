import os
import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, colorchooser
from tkinter.simpledialog import askstring  # Importar para solicitar entrada de texto
from PIL import Image, ImageTk
import requests
import io

# Ruta absoluta de la carpeta uploads (ya no la usamos para cargar imágenes)
uploads_path = '/home/runner/workspace/uploads'  # Asegúrate de que esta ruta es correcta

img_original = None
color_hsv = None

# Función para cargar imagen desde una URL
def cargar_imagen_url():
    global img_original

    # Pedir al usuario que ingrese la URL de la imagen
    url = askstring("Ingresar URL", "Ingresa la URL de la imagen:")

    if url:
        try:
            # Resolver la URL acortada si es necesario
            response = requests.get(url, allow_redirects=True)

            # Verificar que la respuesta sea exitosa
            if response.status_code == 200:
                # Obtener los bytes de la imagen
                imagen_bytes = response.content
                img_array = np.array(bytearray(imagen_bytes), dtype=np.uint8)
                img_original = cv2.imdecode(img_array, -1)

                if img_original is None:
                    print(f"No se pudo cargar la imagen desde la URL: {url}")
                    return

                # Redimensionar la imagen a 300x300
                img_original = cv2.resize(img_original, (300, 300))

                imagen_rgb = cv2.cvtColor(img_original, cv2.COLOR_BGR2RGB)

                # Mostrar la imagen en la interfaz
                mostrar_imagen(imagen_rgb, label_imagen_original)
            else:
                print(f"No se pudo obtener la imagen. Código de estado: {response.status_code}")
        except Exception as e:
            print(f"Ocurrió un error al intentar cargar la imagen desde la URL: {e}")

# Función para seleccionar el color
def seleccionar_color():
    global color_hsv

    color = colorchooser.askcolor()[0]  # Obtener color en RGB
    if color:
        color_hsv = np.array([[[color[0], color[1], color[2]]]], dtype=np.uint8)
        color_hsv = cv2.cvtColor(color_hsv, cv2.COLOR_RGB2HSV)[0][0]
        label_color_seleccionado.config(bg=colorchooser.askcolor()[1])

# Función para segmentar el color seleccionado
def segmentar_color():
    if img_original is None or color_hsv is None:
        return  # No hacer nada si no hay imagen o color seleccionado

    imagen_hsv = cv2.cvtColor(img_original, cv2.COLOR_BGR2HSV)
    lower_bound = np.array([color_hsv[0] - 10, 50, 50])
    upper_bound = np.array([color_hsv[0] + 10, 255, 255])
    mascara = cv2.inRange(imagen_hsv, lower_bound, upper_bound)
    resultado = cv2.bitwise_and(img_original, img_original, mask=mascara)

    # Convertir imágenes para mostrar
    mascara_rgb = cv2.cvtColor(mascara, cv2.COLOR_GRAY2RGB)
    imagen_rgb = cv2.cvtColor(img_original, cv2.COLOR_BGR2RGB)

    # Mostrar imágenes en la interfaz
    mostrar_imagen(imagen_rgb, label_imagen_original)  # Imagen original
    mostrar_imagen(mascara_rgb, label_imagen_mascara)  # Máscara
    mostrar_imagen(resultado, label_imagen_resultado)  # Imagen segmentada

# Función para mostrar una imagen en un label de Tkinter
def mostrar_imagen(imagen, label):
    imagen_pil = Image.fromarray(imagen)
    imagen_tk = ImageTk.PhotoImage(imagen_pil)
    label.config(image=imagen_tk)
    label.image = imagen_tk

# Crear la interfaz con soporte para Drag & Drop
ventana = tk.Tk()
ventana.title("Segmentación por Colores")

# Botones de la interfaz
boton_cargar_imagen_url = tk.Button(ventana, text="Cargar Imagen desde URL", command=cargar_imagen_url)
boton_cargar_imagen_url.pack()

boton_seleccionar_color = tk.Button(ventana, text="Seleccionar Color", command=seleccionar_color)
boton_seleccionar_color.pack()

boton_segmentar = tk.Button(ventana, text="Segmentar", command=segmentar_color)
boton_segmentar.pack()

# Etiquetas para mostrar imágenes
label_imagen_original = tk.Label(ventana)
label_imagen_original.pack()

label_imagen_mascara = tk.Label(ventana)
label_imagen_mascara.pack()

label_imagen_resultado = tk.Label(ventana)
label_imagen_resultado.pack()

label_color_seleccionado = tk.Label(ventana, text="Color Seleccionado", width=20, height=2)
label_color_seleccionado.pack()

# Iniciar la interfaz gráfica
ventana.mainloop()
