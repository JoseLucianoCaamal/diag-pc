import serial
import serial.tools.list_ports
import psutil
import platform
import subprocess
import time
import requests # Recuerda agregar esto a tu .bat (pip install requests)

# --- CONFIGURACIÓN ---
# Reemplaza con tu URL de Firebase (la que termina en .json)
URL_WEB = "https://sistem-diag-default-rtdb.firebaseio.com/monitoreo.json"

def obtener_info_fija():
    """Detecta el modelo de CPU y tamaños totales según el SO."""
    sistema = platform.system()
    try:
        if sistema == "Windows":
            cmd = "wmic cpu get name"
            raw = subprocess.check_output(cmd, shell=True).decode().strip().split('\n')
            cpu = raw[1].strip() if len(raw) > 1 else platform.processor()
        elif sistema == "Darwin": # Mac
            cmd = "sysctl -n machdep.cpu.brand_string"
            cpu = subprocess.check_output(cmd, shell=True).decode().strip()
        else: # Linux
            cmd = "grep 'model name' /proc/cpuinfo | head -n 1"
            cpu = subprocess.check_output(cmd, shell=True).decode().split(":")[1].strip()
    except:
        cpu = "CPU Desconocida"

    ram_t = f"{round(psutil.virtual_memory().total / (1024**3))}GB"
    ruta = "C:" if sistema == "Windows" else "/"
    disk_t = f"{round(psutil.disk_usage(ruta).total / (1024**3))}GB"
    
    return cpu[:18].strip(), ram_t, disk_t

def enviar_datos():
    cpu_mod, ram_t, disk_t = obtener_info_fija()
    esp = None
    ruta_disco = "C:" if platform.system() == "Windows" else "/"

    print(f"Iniciando en {platform.system()}...")

    while True:
        # 1. Obtener porcentajes en tiempo real
        cpu_p = int(psutil.cpu_percent())
        ram_p = int(psutil.virtual_memory().percent)
        disk_p = int(psutil.disk_usage(ruta_disco).percent)

        # 2. ENVIAR A LA WEB (Firebase)
        payload = {
            "info": {"cpu_mod": cpu_mod, "ram_t": ram_t, "disk_t": disk_t},
            "stats": {"cpu": cpu_p, "ram": ram_p, "disk": disk_p},
            "status": "Online",
            "time": time.strftime("%H:%M:%S")
        }
        try:
            requests.put(URL_WEB, json=payload, timeout=1.5)
        except:
            pass

        # 3. ENVIAR AL ESP8266 (Serial)
        if esp is None:
            puertos = serial.tools.list_ports.comports()
            for p in puertos:
                if any(x in p.description.upper() for x in ["CH340", "CP210", "USB"]):
                    try:
                        esp = serial.Serial(port=p.device, baudrate=115200, timeout=1)
                        time.sleep(2)
                        # Enviar inventario inicial al ESP
                        esp.write(bytes(f"INV:{cpu_mod},{ram_t},{disk_t}\n", 'utf-8'))
                    except: esp = None

        if esp:
            try:
                esp.write(bytes(f"MON:{cpu_p},{ram_p},{disk_p}\n", 'utf-8'))
            except: esp = None

        time.sleep(1)

if __name__ == "__main__":
    enviar_datos()
