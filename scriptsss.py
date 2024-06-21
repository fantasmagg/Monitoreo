import os

file_path = 'C:\\Users\\fanta\\Pictures\\Screenshots\\f\\archivo.txt'
renamed_file_path = 'C:\\Users\\fanta\\Pictures\\Screenshots\\f\\archivo_renombrado.txt'

# Función para escribir en el archivo (Modificación)
def modify_file():
    with open(file_path, 'w') as file:
        for _ in range(100):
            file.write('a')


# Función para renombrar el archivo
def rename_file():
    if os.path.exists(file_path):
        os.rename(file_path, renamed_file_path)
        print(f"Archivo renombrado a {renamed_file_path}")

# Función para eliminar el archivo
def delete_file():
    if os.path.exists(renamed_file_path):
        os.remove(renamed_file_path)
        print(f"Archivo {renamed_file_path} eliminado")

# Realizar las acciones sin pausas
modify_file()
rename_file()
delete_file()
while True:
    print(1)
