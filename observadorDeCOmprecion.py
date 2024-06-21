import psutil
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time

class CompressionEventHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        file_extension = os.path.splitext(event.src_path)[1]
        if file_extension in ['.zip', '.rar', '.tar', '.gz']:
            print(f"Detected compression activity: {event.src_path}")

def monitor_processes():
    compression_keywords = ['zip', 'rar', 'tar', 'gzip']
    while True:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                process_name = proc.info['name']
                process_cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                for keyword in compression_keywords:
                    if keyword in process_name.lower() or keyword in process_cmdline.lower():
                        print(f"Detected compression process: PID={proc.info['pid']}, Name={process_name}")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        time.sleep(1)

if __name__ == "__main__":
    path_to_monitor = "C:/movimiento"  # Cambia a la ruta del directorio que quieres monitorear
    event_handler = CompressionEventHandler()
    observer = Observer()
    observer.schedule(event_handler, path=path_to_monitor, recursive=True)
    observer.start()

    try:
        monitor_processes()
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
