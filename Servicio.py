import psutil
import platform
import time
import requests
import datetime

URL_WEB = "https://sistem-diag-default-rtdb.firebaseio.com/monitoreo.json"

def enviar_datos():
    # Información fija
    cpu_mod = platform.processor() or "Procesador"
    equipo = platform.node()
    start_time = psutil.boot_time()

    while True:
        try:
            cpu_p = int(psutil.cpu_percent())
            ram = psutil.virtual_memory()
            
            # Cálculo de Disco (Numeritos: Disponible y Total)
            ruta = "C:\\" if platform.system() == "Windows" else "/"
            disk = psutil.disk_usage(ruta)
            disk_p = int(disk.percent)
            disk_free = round(disk.free / (1024**3), 1)
            disk_total = round(disk.total / (1024**3), 1)

            # Batería
            bat = psutil.sensors_battery()
            bat_p = bat.percent if bat else 100
            cargando = bat.power_plugged if bat else True

            uptime = str(datetime.timedelta(seconds=int(time.time() - start_time)))

            payload = {
                "info": {
                    "cpu_mod": cpu_mod[:25], 
                    "user": equipo,
                    "uptime": uptime,
                    "disk_total": f"{disk_total} GB",
                    "disk_free": f"{disk_free} GB"
                },
                "stats": {
                    "cpu": cpu_p, 
                    "ram": int(ram.percent), 
                    "disk": disk_p,
                    "bat": bat_p, 
                    "charging": cargando
                },
                "time": time.strftime("%H:%M:%S")
            }
            requests.put(URL_WEB, json=payload, timeout=1.5)
        except:
            pass
        time.sleep(1)

if __name__ == "__main__":
    enviar_datos()
