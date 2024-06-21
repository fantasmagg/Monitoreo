import os
import shutil
import getpass

# Obtener el nombre de usuario actual del sistema
username = getpass.getuser()

# Configuraciones para la ruta local
directory_path = f"C:/Users/{username}/AppData/Roaming/Mozilla/Firefox/Profiles/"  # Directorio del cual enviar todos los archivos y carpetas
destination_path = f"C:/movimiento/"  # Ruta local donde se guardarán los archivos comprimidos

# Función para obtener el tamaño total de los archivos en un directorio
def get_dir_size(start_path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if os.path.exists(fp):
                total_size += os.path.getsize(fp)
    return total_size

# Función para comprimir y copiar directorios ordenados por tamaño
def compress_and_copy_directories(directory_path, destination_path):
    # Crear una lista de directorios junto con su tamaño total
    directories = [(d, get_dir_size(os.path.join(directory_path, d))) for d in os.listdir(directory_path) if os.path.isdir(os.path.join(directory_path, d))]
    # Ordenar los directorios por tamaño, del más pequeño al más grande
    directories.sort(key=lambda x: x[1])

    # Comprimir y copiar cada directorio
    for dir_name, _ in directories:
        zip_path = os.path.join(destination_path, f"{dir_name}.zip")
        shutil.make_archive(os.path.join(destination_path, dir_name), 'zip', directory_path, dir_name)
        print(f"Directorio {dir_name} comprimido y copiado a {zip_path}")

# Asegurarse de que la ruta de destino exista
os.makedirs(destination_path, exist_ok=True)

# Ejecutar la función para comprimir y copiar los directorios
compress_and_copy_directories(directory_path, destination_path)
print("Todos los archivos han sido comprimidos y copiados a la ruta local.")
