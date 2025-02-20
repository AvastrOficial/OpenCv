# OpenCv-Filtro

1. Actualizar el sistema

Antes de instalar cualquier paquete, es recomendable actualizar el sistema:

sudo apt update && sudo apt upgrade -y

2. Instalar dependencias del sistema

Algunas bibliotecas como Tkinter y OpenCV requieren paquetes adicionales:

sudo apt install python3-pip python3-tk libopencv-dev -y

3. Instalar las bibliotecas de Python

Usa pip para instalar los paquetes necesarios:

pip3 install opencv-python numpy pillow

Notas adicionales:

    Si pip3 no está instalado, puedes instalarlo con:

sudo apt install python3-pip -y

Si tienes problemas con OpenCV, prueba instalar opencv-contrib-python en lugar de opencv-python:

pip3 install opencv-contrib-python

Para verificar que todo está instalado correctamente, prueba ejecutar:

python3 -c "import cv2, numpy, PIL; print('Instalación correcta')"


# solucion :
ip3 install opencv-contrib-python
error: externally-managed-environment

× This environment is externally managed
╰─> To install Python packages system-wide, try apt install
    python3-xyz, where xyz is the package you are trying to
    install.
    
<br>
El error "externally-managed-environment" en Kali Linux Mini ocurre porque Debian y sus derivados (como Kali) han bloqueado la instalación de paquetes globales con pip fuera de apt.
Soluciones posibles:
Opción 1: Instalar OpenCV con APT (recomendada)

En Kali Linux, puedes instalar OpenCV directamente con apt en lugar de pip:

sudo apt install python3-opencv -y

Luego, verifica la instalación con:

python3 -c "import cv2; print(cv2.__version__)"

Si esta opción no instala la última versión de OpenCV o necesitas funciones adicionales, usa la opción 2.
Opción 2: Usar un Entorno Virtual

Si necesitas usar pip, debes crear un entorno virtual para evitar restricciones del sistema:

    Instalar paquetes esenciales:

sudo apt install python3-full python3-venv python3-pip -y

Crear un entorno virtual:

python3 -m venv opencv_env

Activar el entorno virtual:

source opencv_env/bin/activate

Instalar OpenCV y las dependencias dentro del entorno virtual:

pip install opencv-contrib-python numpy pillow

Ejecutar el script con Python desde el entorno virtual:

    python nombre_del_archivo.py

Para salir del entorno virtual, usa:

deactivate

Opción 3: Forzar la instalación con --break-system-packages (no recomendado)

Si quieres forzar la instalación globalmente (riesgoso porque puede dañar dependencias del sistema), usa:

pip install opencv-contrib-python numpy pillow --break-system-packages
