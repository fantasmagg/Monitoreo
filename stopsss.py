import time

import psutil
import os

# Leer el PID del archivo
with open("process.pid", "r") as f:
    pid = int(f.read().strip())

# Terminar el proceso
try:
    p = psutil.Process(pid)
    p.terminate()  # o p.kill() para forzar la terminación
    p.wait(timeout=5)
    print(f"Process {pid} terminated successfully")
except psutil.NoSuchProcess:
    print(f"No such process: {pid}")
except psutil.AccessDenied:
    print(f"Access denied to terminate process: {pid}")
except psutil.TimeoutExpired:
    print(f"Timeout expired trying to terminate process: {pid}")

while True:
    print(1)
    time.sleep(1)