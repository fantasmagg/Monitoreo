import psutil
import win32file
import win32con
import os
import time
import subprocess
import threading
import signal

# Función para verificar si un archivo está comprimido
def is_compressed(file_path):
    try:
        output = subprocess.check_output(['compact', '/Q', file_path], shell=True, text=True)
        return "compressed" in output.lower()
    except subprocess.CalledProcessError:
        return False

# Función para obtener información sobre un proceso dado su PID
def get_process_info(pid):
    try:
        process = psutil.Process(pid)
        process_info = {
            "pid": pid,
            "name": process.name(),
            "exe": process.exe(),
            "cmdline": process.cmdline(),
            "username": process.username()
        }
        return process_info
    except psutil.NoSuchProcess:
        return None

monito = []
esMal = 0
action_count = {'Deleted': 0, 'Modified': 0, 'Renamed from': 0, 'Renamed to': 0}

# Función para verificar si se deben detener los procesos sospechosos
def check_stop_condition():
    print("Checking stop condition:", action_count)
    return (
        action_count['Deleted'] >= 1 and
        action_count['Modified'] >= 1 and
        action_count['Renamed from'] >= 1 and
        action_count['Renamed to'] >= 1
    )

# Función para detener un proceso dado su PID
def stop_suspicious_process(pid):
    try:
        process = psutil.Process(pid)
        process.terminate()  # Usar terminate() para solicitar al proceso que termine
        process.wait(timeout=5)  # Esperar hasta 5 segundos para que el proceso termine
        print(f"Proceso {pid} detenido por acciones sospechosas.")
        main()
    except psutil.NoSuchProcess:
        print(f"Proceso {pid} no encontrado.")
    except psutil.AccessDenied:
        print(f"Acceso denegado para detener el proceso {pid}.")
    except psutil.TimeoutExpired:
        print(f"Timeout expirado intentando detener el proceso {pid}.")
    except Exception as e:
        print(f"Error al detener el proceso {pid}: {e}")

# Función para monitorear directorios
def monitor_directory(path):
    global esMal
    FILE_LIST_DIRECTORY = 0x0001
    hDir = win32file.CreateFile(
        path,
        FILE_LIST_DIRECTORY,
        win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE | win32con.FILE_SHARE_DELETE,
        None,
        win32con.OPEN_EXISTING,
        win32con.FILE_FLAG_BACKUP_SEMANTICS,
        None
    )

    while True:
        try:
            results = win32file.ReadDirectoryChangesW(
                hDir,
                1024,
                True,  # Monitoreo recursivo de subdirectorios
                win32con.FILE_NOTIFY_CHANGE_FILE_NAME |
                win32con.FILE_NOTIFY_CHANGE_DIR_NAME |
                win32con.FILE_NOTIFY_CHANGE_ATTRIBUTES |
                win32con.FILE_NOTIFY_CHANGE_SIZE |
                win32con.FILE_NOTIFY_CHANGE_LAST_WRITE |
                win32con.FILE_NOTIFY_CHANGE_SECURITY,
                None,
                None
            )
            for action, file in results:
                full_filename = os.path.join(path, file)
                ass = ""
                if action == 1:  # Creación
                    ass = f"Created: {full_filename}"
                elif action == 2:  # Eliminación
                    ass = f"Deleted: {full_filename}"
                    if ass not in monito:
                        monito.append(ass)
                        action_count['Deleted'] += 1
                elif action == 3:  # Modificación
                    ass = f"Modified: {full_filename}"
                    if ass not in monito:
                        monito.append(ass)
                        action_count['Modified'] += 1
                elif action == 4:  # Renombrar desde
                    ass = f"Renamed from: {full_filename}"
                    if ass not in monito:
                        monito.append(ass)
                        action_count['Renamed from'] += 1
                elif action == 5:  # Renombrar a
                    ass = f"Renamed to: {full_filename}"
                    if ass not in monito:
                        monito.append(ass)
                        action_count['Renamed to'] += 1

                if ass:
                    print(ass)
                    if ass not in monito:
                        monito.append(ass)
                        if action in [2, 3, 4, 5]:
                            esMal += 1

                if check_stop_condition():
                    print("Se han detectado 3 o más acciones específicas. Deteniendo procesos sospechosos.")
                    suspicious_pids = [proc.info['pid'] for proc in psutil.process_iter(['pid', 'name', 'cmdline']) if 'python' in proc.info['name']]
                    for pid in suspicious_pids:
                        stop_suspicious_process(pid)
                    action_count['Deleted'] = 0
                    action_count['Modified'] = 0
                    action_count['Renamed from'] = 0
                    action_count['Renamed to'] = 0

            print(f"Hay algo sospechoso. Número de acciones realizadas: {esMal}")
            for ac in monito:
                print(ac)
            time.sleep(1)  # Añadir un pequeño delay para evitar sobrecargar el CPU
        except Exception as e:
            print(f"Error en monitor_directory: {e}")

# Función para monitorear un script de Python específico
def monitor_specific_python_script(script_name):
    while True:
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                if proc.info['name'] == 'python.exe' or proc.info['name'] == 'pythonw.exe':
                    if script_name in proc.info['cmdline']:
                        pid = proc.info['pid']
                        try:
                            process = psutil.Process(pid)
                            with process.oneshot():
                                open_files = process.open_files()
                                for file in open_files:
                                    print(f"Process {pid} is accessing {file.path}")
                                    process_info = get_process_info(pid)
                                    if process_info:
                                        print(f"Process {pid} information:")
                                        print(f"  Name: {process_info['name']}")
                                        print(f"  Executable: {process_info['exe']}")
                                        print(f"  Command Line: {' '.join(process_info['cmdline'])}")
                                        print(f"  User: {process_info['username']}")
                        except (psutil.AccessDenied, psutil.NoSuchProcess) as e:
                            print(f"Error accessing process {pid}: {e}")

            if check_stop_condition():
                print("Se han detectado 3 o más acciones específicas. Deteniendo procesos sospechosos.")
                suspicious_pids = [proc.info['pid'] for proc in psutil.process_iter(['pid', 'name', 'cmdline']) if 'python' in proc.info['name']]
                for pid in suspicious_pids:
                    stop_suspicious_process(pid)
                action_count['Deleted'] = 0
                action_count['Modified'] = 0
                action_count['Renamed from'] = 0
                action_count['Renamed to'] = 0
            time.sleep(1)
        except Exception as e:
            print(f"Error en monitor_specific_python_script: {e}")

# Monitorear directorios y procesos específicos
def main():
    paths_to_monitor = ["C:\\curos\\monitoreo\\monitoreoScrpt", "C:\\Users\\fanta\\Pictures\\Screenshots\\f"]

    # Monitorear los directorios en hilos separados
    threads = []
    for path in paths_to_monitor:
        thread = threading.Thread(target=monitor_directory, args=(path,))
        thread.daemon = True
        threads.append(thread)
        thread.start()

    # Nombre del script de Python a monitorear (puedes ponerlo en None para monitorear todos los scripts de Python)
    script_name = "scriptsss.py"

    # Monitorear el acceso a archivos por parte del script de Python específico de forma continua
    script_thread = threading.Thread(target=monitor_specific_python_script, args=(script_name,))
    script_thread.daemon = True
    script_thread.start()

    for thread in threads:
        thread.join()

if __name__ == "__main__":
    main()
