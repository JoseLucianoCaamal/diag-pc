import psutil
import platform
import time
import requests
import datetime
import socket

# --- CONFIGURACIÓN ---
URL_WEB = "https://sistem-diag-default-rtdb.firebaseio.com/monitoreo.json"

def obtener_latencia():
    """Mide la respuesta de la red en milisegundos."""
    try:
        inicio = time.time()
        socket.create_connection(("8.8.8.8", 53), timeout=2)
        return int((time.time() - inicio) * 1000)
    except:
        return "Error"

def enviar_datos():
    # Información estática
    cpu_mod = platform.processor() or "Procesador"
    equipo = platform.node()
    start_time = psutil.boot_time()

    print(f"SistemDiag Corriendo - Monitoreando: {equipo}")

    while True:
        try:
            # Métricas de CPU y RAM
            cpu_p = int(psutil.cpu_percent())
            ram = psutil.virtual_memory()
            
            # Cálculo de Disco (Corregido para evitar undefined)
            ruta = "C:\\" if platform.system() == "Windows" else "/"
            disco = psutil.disk_usage(ruta)
            disk_p = int(disco.percent)
            disk_free = round(disco.free / (1024**3), 1)
            disk_total = round(disco.total / (1024**3), 1)

            # Batería
            bat = psutil.sensors_battery()
            bat_p = bat.percent if bat else 100
            cargando = bat.power_plugged if bat else True

            # Tiempo y Red
            uptime = str(datetime.timedelta(seconds=int(time.time() - start_time)))
            ping = obtener_latencia()

            payload = {
                "info": {
                    "cpu_mod": cpu_mod[:25], 
                    "user": equipo,
                    "uptime": uptime,
                    "disk_total": f"{disk_total} GB",
                    "disk_free": f"{disk_free} GB",
                    "ping": f"{ping} ms"
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
            
        except Exception as e:
            print(f"Error de sincronización: {e}")
            
        time.sleep(1)

if __name__ == "__main__":
    enviar_datos()
