# OpenCv

Este repositorio contiene instrucciones y soluciones para la instalación y configuración de OpenCV en sistemas basados en Linux, con especial atención a Kali Linux y sus derivados.

![WhatsApp Image 2025-02-22 at 00 24 23_87ba4879](https://github.com/user-attachments/assets/bb105163-19d3-41af-9a6c-0dcf696125a4)

![WhatsApp Image 2025-02-22 at 23 48 21_ca72fbce](https://github.com/user-attachments/assets/01dec642-219e-455f-91b9-ea714b955aa7)

## OpenCv-Filtro

### 1. Actualizar el sistema

Antes de instalar cualquier paquete, es recomendable actualizar el sistema:

```bash
sudo apt update && sudo apt upgrade -y
```
2. Instalar dependencias del sistema
Algunas bibliotecas como Tkinter y OpenCV requieren paquetes adicionales. Instala estas dependencias:

```bash
sudo apt install python3-pip python3-tk libopencv-dev -y
```
3. Instalar las bibliotecas de Python
Usa pip para instalar los paquetes necesarios:

```bash
pip3 install opencv-python numpy pillow
```
Notas adicionales:
Si pip3 no está instalado, puedes instalarlo con:

```bash
sudo apt install python3-pip -y
```
Si tienes problemas con OpenCV, prueba instalar opencv-contrib-python en lugar de opencv-python:

```bash
pip3 install opencv-contrib-python
```
Para verificar que todo está instalado correctamente, ejecuta:

```bash
python3 -c "import cv2, numpy, PIL; print('Instalación correcta')"
```
Soluciones a problemas comunes
```bash
Problema: Error "externally-managed-environment"
Si encuentras el error:

vbnet
error: externally-managed-environment
× This environment is externally managed
╰─> To install Python packages system-wide, try apt install
    python3-xyz, where xyz is the package you are trying to install.
Este error ocurre en Kali Linux Mini porque Debian y sus derivados (como Kali) bloquean la instalación de paquetes globales con pip fuera de apt.
```
Soluciones posibles:
Opción 1: Instalar OpenCV con APT (recomendada)

Puedes instalar OpenCV directamente con apt en lugar de pip:

```bash
sudo apt install python3-opencv -y
```
Verifica la instalación con:

```bash
python3 -c "import cv2; print(cv2.__version__)"
```
Si esta opción no instala la última versión de OpenCV o necesitas funciones adicionales, utiliza la opción 2.

Opción 2: Usar un Entorno Virtual

Si necesitas usar pip, crea un entorno virtual para evitar restricciones del sistema:

Instala paquetes esenciales:

```bash
sudo apt install python3-full python3-venv python3-pip -y
```
Crea un entorno virtual:

```bash
python3 -m venv opencv_env
```
Activa el entorno virtual:
```bash
source opencv_env/bin/activate
```
Instala OpenCV y las dependencias dentro del entorno virtual:

```bash
pip install opencv-contrib-python numpy pillow
```
Ejecuta el script con Python desde el entorno virtual:

```bash
python nombre_del_archivo.py
```
Para salir del entorno virtual, usa:

```bash
deactivate
```
Opción 3: Forzar la instalación con 
```bash 
--break-system-packages 
```
(no recomendado)

Si quieres forzar la instalación globalmente (riesgoso porque puede dañar dependencias del sistema), usa:

```bash
pip install opencv-contrib-python numpy pillow --break-system-packages
```
Instalar Tkinter y Drag-and-Drop en Python
Si necesitas usar Tkinter con soporte de arrastrar y soltar, instala el paquete necesario:

```bash
pip install tkinterdnd2
```
