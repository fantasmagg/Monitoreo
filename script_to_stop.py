import time
import os

# Guardar el PID en un archivo
pid = os.getpid()
with open("process.pid", "w") as f:
    f.write(str(pid))

try:
    while True:
        print("Running...")
        time.sleep(1)
except KeyboardInterrupt:
    print("Script stopped")
