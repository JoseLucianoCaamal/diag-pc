import psutil
import platform
import time
import requests
import datetime
import socket
import os
import shutil
import winreg  # Alternativa nativa a WMIC para Windows

URL_WEB = "https://sistem-diag-default-rtdb.firebaseio.com/monitoreo.json"

def obtener_datos_windows():
    """Extrae info sin usar WMIC, directo del registro de Windows."""
    datos = {"ram_brand": "Genérica", "disk_serial": "SATA_DATA_01", "bios": "2023", "age": "N/A"}
    try:
        if platform.system() == "Windows":
            # Extraer fecha de BIOS desde el Registro
            path = r"HARDWARE\DESCRIPTION\System\BIOS"
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path) as key:
                bios_date = winreg.QueryValueEx(key, "BIOSReleaseDate")[0]
                year = bios_date.split('/')[-1] if '/' in bios_date else bios_date[-4:]
                datos["bios"] = year
                edad = datetime.datetime.now().year - int(year)
                datos["age"] = f"{edad} años" if edad >= 0 else "Nuevo"
    except: pass
    return datos

def enviar_datos():
    equipo = platform.node()
    start_time = psutil.boot_time()
    info_fija = obtener_datos_windows()
    
    # PLUS: Monitoreo de USBs conectados
    usb_inicial = len(psutil.disk_partitions())

    while True:
        try:
            # Métricas dinámicas seguras
            cpu_p = int(psutil.cpu_percent())
            ram = psutil.virtual_memory()
            disco = psutil.disk_usage("C:\\" if platform.system() == "Windows" else "/")
            bat = psutil.sensors_battery()
            
            # Detección de intrusos (USB nuevo)
            usb_actual = len(psutil.disk_partitions())
            alerta_usb = "Seguro" if usb_actual <= usb_inicial else "USB DETECTADO"

            # Proceso pesado sin errores
            try:
                proc_top = sorted(psutil.process_iter(['name', 'cpu_percent']), key=lambda p: p.info['cpu_percent'], reverse=True)[0].info['name']
            except: proc_top = "Sistema"

            payload = {
                "info": {
                    "user": equipo,
                    "uptime": str(datetime.timedelta(seconds=int(time.time() - start_time))),
                    "disk_total": f"{round(disco.total/(1024**3))}GB",
                    "disk_free": f"{round(disco.free/(1024**3))}GB",
                    "top_proc": proc_top,
                    "ram_brand": info_fija["ram_brand"],
                    "disk_serial": info_fija["disk_serial"],
                    "age": info_fija["age"],
                    "bios": info_fija["bios"],
                    "usb_status": alerta_usb
                },
                "stats": {
                    "cpu": cpu_p, "ram": int(ram.percent), "disk": disco.percent,
                    "bat": bat.percent if bat else 100, "charging": bat.power_plugged if bat else True
                }
            }
            requests.put(URL_WEB, json=payload, timeout=1.5)
        except: pass
        time.sleep(1)

if __name__ == "__main__":
    enviar_datos()
