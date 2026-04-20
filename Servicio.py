import serial
import serial.tools.list_ports
import psutil
import platform
import subprocess
import time
import requests

# --- CONFIGURACIÓN ---
URL_WEB = "https://sistem-diag-default-rtdb.firebaseio.com/monitoreo.json"

def obtener_info_fija():
    sistema = platform.system()
    try:
        if sistema == "Windows":
            cmd = "wmic cpu get name"
            raw = subprocess.check_output(cmd, shell=True).decode().strip().split('\n')
            cpu = raw[1].strip() if len(raw) > 1 else platform.processor()
        elif sistema == "Darwin":
            cmd = "sysctl -n machdep.cpu.brand_string"
            cpu = subprocess.check_output(cmd, shell=True).decode().strip()
        else:
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

    print(f"Iniciando Diagnóstico con Batería en {platform.system()}...")

    while True:
        # 1. Obtener métricas básicas
        cpu_p = int(psutil.cpu_percent())
        ram_p = int(psutil.virtual_memory().percent)
        disk_p = int(psutil.disk_usage(ruta_disco).percent)

        # 2. Obtener estado de batería
        bateria = psutil.sensors_battery()
        if bateria:
            bat_p = int(bateria.percent)
            cargando = bateria.power_plugged
        else:
            bat_p = 0
            cargando = False

        # 3. ENVIAR A FIREBASE
        payload = {
            "info": {"cpu_mod": cpu_mod, "ram_t": ram_t, "disk_t": disk_t},
            "stats": {
                "cpu": cpu_p, 
                "ram": ram_p, 
                "disk": disk_p,
                "bat": bat_p,
                "charging": cargando
            },
            "status": "Online",
            "time": time.strftime("%H:%M:%S")
        }
        try:
            requests.put(URL_WEB, json=payload, timeout=1.5)
        except:
            pass

        # 4. ENVIAR AL ESP8266 (Serial)
        if esp is None:
            puertos = serial.tools.list_ports.comports()
            for p in puertos:
                if any(x in p.description.upper() for x in ["CH340", "CP210", "USB"]):
                    try:
                        esp = serial.Serial(port=p.device, baudrate=115200, timeout=1)
                        time.sleep(2)
                        esp.write(bytes(f"INV:{cpu_mod},{ram_t},{disk_t}\n", 'utf-8'))
                    except: esp = None

        if esp:
            try:
                # Trama extendida: MON:cpu,ram,disk,bat
                esp.write(bytes(f"MON:{cpu_p},{ram_p},{disk_p},{bat_p}\n", 'utf-8'))
            except: esp = None

        time.sleep(1)

if __name__ == "__main__":
    enviar_datos()
