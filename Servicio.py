import psutil
import platform
import time
import requests
import datetime
import socket
import os
import shutil
import subprocess

URL_WEB = "https://sistem-diag-default-rtdb.firebaseio.com/monitoreo.json"

def obtener_auditoria():
    datos = {"ram_brand": "Genérica", "disk_serial": "N/D", "bios": "N/D", "age": "N/A"}
    try:
        if platform.system() == "Windows":
            # RAM
            r = subprocess.check_output("wmic memorychip get manufacturer", shell=True).decode().split('\n')
            datos["ram_brand"] = r[1].strip() if len(r) > 1 else "Genérica"
            # Disco
            d = subprocess.check_output("wmic diskdrive get serialnumber", shell=True).decode().split('\n')
            datos["disk_serial"] = d[1].strip() if len(d) > 1 else "N/D"
            # BIOS/Edad
            b = subprocess.check_output("wmic bios get releasedate", shell=True).decode().split('\n')
            if len(b) > 1:
                year = b[1].strip()[:4]
                datos["bios"] = year
                datos["age"] = f"{datetime.datetime.now().year - int(year)} años"
    except: pass
    return datos

def limpiar_temporales():
    temp = os.environ.get('TEMP')
    if temp and os.path.exists(temp):
        for f in os.listdir(temp):
            path = os.path.join(temp, f)
            try:
                if os.path.isfile(path) or os.path.islink(path): os.unlink(path)
                elif os.path.isdir(path): shutil.rmtree(path)
            except: continue

def enviar_datos():
    equipo = platform.node()
    cpu_mod = platform.processor()[:25]
    start_time = psutil.boot_time()
    auditoria = obtener_auditoria()

    while True:
        try:
            # Escuchar comando de limpieza
            res = requests.get(URL_WEB)
            if res.status_code == 200 and res.json().get("comando") == "limpiar":
                limpiar_temporales()
                requests.patch(URL_WEB, json={"comando": "listo"})

            # Métricas dinámicas
            cpu_p = int(psutil.cpu_percent())
            ram = psutil.virtual_memory()
            disco = psutil.disk_usage("C:\\" if platform.system() == "Windows" else "/")
            bat = psutil.sensors_battery()
            
            # Proceso pesado y Ping
            proc_top = "N/A"
            try:
                proc_top = sorted([(p.info['name'], p.info['cpu_percent']) for p in psutil.process_iter(['name', 'cpu_percent'])], key=lambda x: x[1], reverse=True)[0][0]
                socket.create_connection(("8.8.8.8", 53), timeout=1)
                ping = "OK"
            except: ping = "Error"

            payload = {
                "info": {
                    "user": equipo, "cpu_mod": cpu_mod, "uptime": str(datetime.timedelta(seconds=int(time.time() - start_time))),
                    "disk_total": f"{round(disco.total/(1024**3))}GB", "disk_free": f"{round(disco.free/(1024**3))}GB",
                    "ping": ping, "top_proc": proc_top,
                    "ram_brand": auditoria["ram_brand"], "disk_serial": auditoria["disk_serial"], "age": auditoria["age"], "bios": auditoria["bios"]
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
