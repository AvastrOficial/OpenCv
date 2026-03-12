import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk

def apply_filter():
    global img, img_tk
    if img is None:
        return
    
    filter_name = filter_var.get()
    filtered_img = img.copy()
    
    if filter_name == "Suavizado":
        filtered_img = cv2.GaussianBlur(img, (5, 5), 0)
    elif filter_name == "Convolución 2D":
        kernel = np.ones((5, 5), np.float32) / 25
        filtered_img = cv2.filter2D(img, -1, kernel)
    elif filter_name == "Promedio":
        filtered_img = cv2.blur(img, (5, 5))
    elif filter_name == "Gaussiano":
        filtered_img = cv2.GaussianBlur(img, (5, 5), 0)
    elif filter_name == "Mediana":
        filtered_img = cv2.medianBlur(img, 5)
    elif filter_name == "Umbralización Simple":
        _, filtered_img = cv2.threshold(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), 127, 255, cv2.THRESH_BINARY)
    elif filter_name == "Umbralización Adaptativa":
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        filtered_img = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    elif filter_name == "Binarización de Otsu":
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, filtered_img = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    elif filter_name == "Laplaciano":
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        filtered_img = cv2.Laplacian(gray, cv2.CV_64F)
        filtered_img = np.uint8(np.absolute(filtered_img))
    elif filter_name == "Sobel X":
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        filtered_img = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=5)
        filtered_img = np.uint8(np.absolute(filtered_img))
    elif filter_name == "Sobel Y":
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        filtered_img = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=5)
        filtered_img = np.uint8(np.absolute(filtered_img))
    elif filter_name == "Canny":
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        filtered_img = cv2.Canny(gray, 100, 200)
    
    show_image(filtered_img, label_filtered)

def load_image():
    global img
    file_path = filedialog.askopenfilename()
    if not file_path:
        return
    img = cv2.imread(file_path)
    show_image(img, label_original)

def show_image(image, label):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB) if len(image.shape) == 3 else image
    image = Image.fromarray(image)
    image.thumbnail((300, 300))
    imgtk = ImageTk.PhotoImage(image=image)
    label.imgtk = imgtk
    label.configure(image=imgtk)

# Configuración de la ventana
top = tk.Tk()
top.title("Filtro de Imágenes con OpenCV")
top.geometry("700x500")

tk.Button(top, text="Cargar Imagen", command=load_image).pack()

filter_var = tk.StringVar()
filters = ["Suavizado", "Convolución 2D", "Promedio", "Gaussiano", "Mediana", "Umbralización Simple", "Umbralización Adaptativa", "Binarización de Otsu", "Laplaciano", "Sobel X", "Sobel Y", "Canny"]
filter_dropdown = ttk.Combobox(top, textvariable=filter_var, values=filters, state="readonly")
filter_dropdown.pack()
filter_dropdown.set(filters[0])

tk.Button(top, text="Aplicar Filtro", command=apply_filter).pack()

label_original = tk.Label(top)
label_original.pack()
label_filtered = tk.Label(top)
label_filtered.pack()

img = None
top.mainloop()
