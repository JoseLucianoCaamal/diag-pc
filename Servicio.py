import psutil
import platform
import time
import requests
import datetime
import socket
import os
import shutil

URL_WEB = "https://sistem-diag-default-rtdb.firebaseio.com/monitoreo.json"

def limpiar_temporales():
    """Limpia la carpeta de archivos temporales de Windows."""
    temp_dir = os.environ.get('TEMP')
    if temp_dir and os.path.exists(temp_dir):
        for filename in os.listdir(temp_dir):
            file_path = os.path.join(temp_dir, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception:
                continue # Salta archivos en uso

def obtener_proceso_pesado():
    """Identifica el programa que más CPU consume."""
    try:
        procesos = [(p.info['name'], p.info['cpu_percent']) for p in psutil.process_iter(['name', 'cpu_percent'])]
        procesos.sort(key=lambda x: x[1], reverse=True)
        return procesos[0][0] if procesos else "Ninguno"
    except:
        return "N/A"

def enviar_datos():
    equipo = platform.node()
    start_time = psutil.boot_time()

    while True:
        try:
            # --- PLUS: ESCUCHAR COMANDO DE LIMPIEZA ---
            # Leemos la DB para ver si el usuario presionó el botón en la web
            res = requests.get(URL_WEB)
            if res.status_code == 200:
                cloud_data = res.json()
                if cloud_data.get("comando") == "limpiar":
                    limpiar_temporales()
                    # Resetear el comando tras limpiar
                    requests.patch(URL_WEB, json={"comando": "listo"})

            # Métricas estándar
            cpu_p = int(psutil.cpu_percent())
            ram = psutil.virtual_memory()
            disco = psutil.disk_usage("C:\\" if platform.system() == "Windows" else "/")
            bat = psutil.sensors_battery()
            
            # --- NUEVOS DATOS ---
            proceso_top = obtener_proceso_pesado()
            ping = "Error"
            try:
                socket.create_connection(("8.8.8.8", 53), timeout=1)
                ping = f"{int((time.time() - time.time()) * 1000)} ms" # Simplificado
            except: pass

            payload = {
                "info": {
                    "user": equipo,
                    "uptime": str(datetime.timedelta(seconds=int(time.time() - start_time))),
                    "disk_total": f"{round(disco.total / (1024**3), 1)} GB",
                    "disk_free": f"{round(disco.free / (1024**3), 1)} GB",
                    "ping": ping,
                    "top_process": proceso_top # <--- PLUS
                },
                "stats": {
                    "cpu": cpu_p, "ram": int(ram.percent), "disk": disco.percent,
                    "bat": bat.percent if bat else 100, "charging": bat.power_plugged if bat else True
                },
                "time": time.strftime("%H:%M:%S")
            }
            requests.put(URL_WEB, json=payload, timeout=1.5)
        except: pass
        time.sleep(1)

if __name__ == "__main__":
    enviar_datos()
