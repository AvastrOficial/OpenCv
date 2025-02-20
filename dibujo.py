import cv2
import numpy as np

# Variables globales
drawing = False  # Verdadero si el mouse está presionado
mode = True  # Modo True para dibujo libre, False para líneas rectas
ix, iy = -1, -1  # Coordenadas iniciales
color = (0, 0, 255)  # Color inicial (rojo en formato BGR)
thickness = 2  # Grosor inicial

def draw(event, x, y, flags, param):
    global ix, iy, drawing, mode, color, thickness
    
    if event == cv2.EVENT_LBUTTONDOWN:  # Click izquierdo presionado
        drawing = True
        ix, iy = x, y
    
    elif event == cv2.EVENT_MOUSEMOVE:  # Movimiento del mouse
        if drawing:
            if mode:
                cv2.circle(img, (x, y), thickness, color, -1)
            else:
                cv2.line(img, (ix, iy), (x, y), color, thickness)
                ix, iy = x, y
    
    elif event == cv2.EVENT_LBUTTONUP:  # Soltar click izquierdo
        drawing = False
        if not mode:
            cv2.line(img, (ix, iy), (x, y), color, thickness)

# Crear una imagen en blanco
img = np.ones((512, 512, 3), np.uint8) * 255
cv2.namedWindow("Dibujo")
cv2.setMouseCallback("Dibujo", draw)

while True:
    cv2.imshow("Dibujo", img)
    key = cv2.waitKey(1) & 0xFF
    
    if key == ord('m'):  # Cambiar entre dibujo libre y líneas
        mode = not mode
    elif key == ord('r'):  # Cambiar a color rojo
        color = (0, 0, 255)
    elif key == ord('g'):  # Cambiar a color verde
        color = (0, 255, 0)
    elif key == ord('b'):  # Cambiar a color azul
        color = (255, 0, 0)
    elif key == ord('+'):  # Aumentar grosor
        thickness += 1
    elif key == ord('-'):  # Disminuir grosor
        thickness = max(1, thickness - 1)
    elif key == 27:  # Tecla ESC para salir
        break

cv2.destroyAllWindows()

