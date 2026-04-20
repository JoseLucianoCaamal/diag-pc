import psutil
import platform
import time
import requests
import datetime
import subprocess

URL_WEB = "https://sistem-diag-default-rtdb.firebaseio.com/monitoreo.json"

def obtener_auditoria():
    """Extrae datos de hardware nivel experto."""
    datos = {
        "ram_brand": "Genérica",
        "disk_serial": "No detectado",
        "bios_date": "Desconocida",
        "edad_estimada": "N/A"
    }
    try:
        if platform.system() == "Windows":
            # Marca de RAM
            ram_cmd = subprocess.check_output("wmic memorychip get manufacturer", shell=True).decode().split('\n')
            datos["ram_brand"] = ram_cmd[1].strip() if len(ram_cmd) > 1 else "Genérica"
            
            # Serie del Disco
            disk_cmd = subprocess.check_output("wmic diskdrive get serialnumber", shell=True).decode().split('\n')
            datos["disk_serial"] = disk_cmd[1].strip() if len(disk_cmd) > 1 else "N/D"
            
            # Fecha BIOS y Edad
            bios_cmd = subprocess.check_output("wmic bios get releasedate", shell=True).decode().split('\n')
            if len(bios_cmd) > 1:
                raw_date = bios_cmd[1].strip()[:4] # Tomamos el año
                datos["bios_date"] = raw_date
                edad = datetime.datetime.now().year - int(raw_date)
                datos["edad_estimada"] = f"{edad} años" if edad >= 0 else "Nuevo"
    except:
        pass
    return datos

def enviar_datos():
    equipo = platform.node()
    cpu_mod = platform.processor()[:25]
    auditoria = obtener_auditoria() # Se ejecuta una vez al inicio

    while True:
        try:
            # Métricas dinámicas
            cpu_p = int(psutil.cpu_percent())
            ram_p = int(psutil.virtual_memory().percent)
            bat = psutil.sensors_battery()
            
            payload = {
                "info": {
                    "user": equipo,
                    "cpu_mod": cpu_mod,
                    "ram_brand": auditoria["ram_brand"],
                    "disk_serial": auditoria["disk_serial"],
                    "age": auditoria["edad_estimada"],
                    "bios": auditoria["bios_date"]
                },
                "stats": {
                    "cpu": cpu_p,
                    "ram": ram_p,
                    "bat": bat.percent if bat else 100,
                    "charging": bat.power_plugged if bat else True
                }
            }
            requests.put(URL_WEB, json=payload, timeout=1.5)
        except: pass
        time.sleep(1)

if __name__ == "__main__":
    enviar_datos()
