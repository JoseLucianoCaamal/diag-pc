import psutil
import platform
import time
import requests
import datetime
import socket
import os
import shutil

URL_WEB = "https://sistem-diag-default-rtdb.firebaseio.com/monitoreo.json"

def enviar_datos():
    # Usamos info nativa de Python para evitar errores de consola (wmic)
    equipo = platform.node()
    cpu_mod = platform.processor()[:25]
    start_time = psutil.boot_time()

    print(f"Iniciando servicio estable en: {equipo}")

    while True:
        try:
            # 1. Recolección de métricas con salvaguardas
            cpu_p = int(psutil.cpu_percent())
            ram_p = int(psutil.virtual_memory().percent)
            
            # Disco con manejo de error por si la ruta no existe
            try:
                ruta = "C:\\" if platform.system() == "Windows" else "/"
                disk_usage = psutil.disk_usage(ruta)
                disk_p = int(disk_usage.percent)
                disk_f = f"{round(disk_usage.free/(1024**3))}GB"
                disk_t = f"{round(disk_usage.total/(1024**3))}GB"
            except:
                disk_p, disk_f, disk_t = 0, "N/A", "N/A"

            # Batería (Verifica si existe el sensor)
            bat = psutil.sensors_battery()
            bat_p = bat.percent if bat else 100
            cargando = bat.power_plugged if bat else True

            # 2. Preparación del envío
            payload = {
                "info": {
                    "user": equipo,
                    "cpu_mod": cpu_mod,
                    "uptime": str(datetime.timedelta(seconds=int(time.time() - start_time))),
                    "disk_free": disk_f,
                    "disk_total": disk_t
                },
                "stats": {
                    "cpu": cpu_p, "ram": ram_p, "disk": disk_p,
                    "bat": bat_p, "charging": cargando
                }
            }

            # 3. Envío con Timeout para que no se congele el script
            requests.put(URL_WEB, json=payload, timeout=2)

        except Exception as e:
            # Si hay CUALQUIER error (internet, puerto, etc), lo imprime pero NO CIERRA el programa
            print(f"Sincronizando... (Error temporal: {e})")
        
        time.sleep(1) # Espera obligatoria para no saturar el CPU

if __name__ == "__main__":
    enviar_datos()
