import os
import zipfile
import shutil

# Ruta del archivo original
file_path = 'C:\\mv\\VMware-Workstation-Full-17.5.2-23775571.x86_64.bundle'

# Ruta del archivo comprimido temporal
compressed_file_path = 'C:\\mv\\\VMware-Workstation-Full-17.5.2-23775571.zip'

# Ruta destino donde mover el archivo comprimido
destination_path = 'C:\\movimiento\\VMware-Workstation-Full-17.5.2-23775571.zip'

# Función para comprimir el archivo
def compress_file():
    with zipfile.ZipFile(compressed_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(file_path, os.path.basename(file_path))
        print(f"Archivo comprimido en {compressed_file_path}")

# Función para mover el archivo comprimido
def move_compressed_file():
    if os.path.exists(compressed_file_path):
        shutil.move(compressed_file_path, destination_path)
        print(f"Archivo comprimido movido a {destination_path}")

# Realizar las acciones
compress_file()
move_compressed_file()

while True:
    print(1)
