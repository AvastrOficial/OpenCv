import cv2
import numpy as np
from tkinter import Tk, filedialog

def generar_robot_estilizado():
    # Oculta la ventana raíz de Tkinter
    Tk().withdraw()
    
    # Abre el cuadro de diálogo para seleccionar la imagen
    file_path = filedialog.askopenfilename(
        title="Selecciona la imagen del robot",
        filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.bmp")]
    )
    
    # Verificar si se seleccionó un archivo
    if not file_path:
        print("No se seleccionó ninguna imagen.")
        return
    
    # Cargar la imagen con OpenCV
    img = cv2.imread(file_path)
    if img is None:
        print("Error: No se pudo cargar la imagen. Verifica el formato y la ruta del archivo.")
        return
    
    # Opción 1: Estilización con cv2.stylization (requiere OpenCV >= 4.5.2)
    try:
        # Ajusta los valores sigma_s y sigma_r para obtener distintos estilos
        stylized_img = cv2.stylization(img, sigma_s=150, sigma_r=0.25)
        
        # Mostrar la imagen original y la estilizada
        cv2.imshow("Robot Original", img)
        cv2.imshow("Robot Estilizado", stylized_img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        
    except AttributeError:
        print("Tu versión de OpenCV no soporta la función 'stylization'. Usando efecto 'cartoon'...")
        
        # Opción 2: Efecto 'cartoon' manual (filtro bilateral + detección de bordes)
        
        # 1. Convertir a escala de grises
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 2. Reducir ruido con desenfoque mediano
        gray_blur = cv2.medianBlur(gray, 5)
        
        # 3. Detectar bordes con umbral adaptativo
        edges = cv2.adaptiveThreshold(
            gray_blur, 255,
            cv2.ADAPTIVE_THRESH_MEAN_C,
            cv2.THRESH_BINARY,
            blockSize=9,
            C=9
        )
        
        # 4. Reducir la cantidad de colores con un filtro bilateral (varias pasadas)
        color = cv2.bilateralFilter(img, 9, 250, 250)
        
        # 5. Combinar bordes y color
        cartoon = cv2.bitwise_and(color, color, mask=edges)
        
        # Mostrar la imagen original y la imagen con efecto "cartoon"
        cv2.imshow("Robot Original", img)
        cv2.imshow("Robot en estilo 'Cartoon'", cartoon)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

# Llamar a la función principal
if __name__ == "__main__":
    generar_robot_estilizado()
