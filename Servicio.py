import psutil
import platform
import time
import requests
import datetime

URL_WEB = "https://sistem-diag-default-rtdb.firebaseio.com/monitoreo.json"

def enviar_datos():
    # Información fija sin usar consola
    cpu_mod = platform.processor() or "Procesador Central"
    ram_t = f"{round(psutil.virtual_memory().total / (1024**3))}GB"
    equipo = platform.node()
    start_time = psutil.boot_time()

    while True:
        try:
            # Métricas básicas
            cpu_p = int(psutil.cpu_percent())
            ram_p = int(psutil.virtual_memory().percent)
            
            # Batería
            bat = psutil.sensors_battery()
            bat_p = bat.percent if bat else 100
            cargando = bat.power_plugged if bat else True
            
            # Disco (Ruta universal)
            ruta = "C:\\" if platform.system() == "Windows" else "/"
            disk_p = int(psutil.disk_usage(ruta).percent)

            uptime = str(datetime.timedelta(seconds=int(time.time() - start_time)))

            payload = {
                "info": {
                    "cpu_mod": cpu_mod[:25], 
                    "ram_t": ram_t, 
                    "user": equipo,
                    "uptime": uptime
                },
                "stats": {
                    "cpu": cpu_p, "ram": ram_p, "disk": disk_p,
                    "bat": bat_p, "charging": cargando
                },
                "time": time.strftime("%H:%M:%S")
            }
            requests.put(URL_WEB, json=payload, timeout=1.5)
        except:
            pass
        time.sleep(1)

if __name__ == "__main__":
    enviar_datos()
