import psutil
import platform
import time
import requests
import datetime
import socket
import os
import shutil
import winreg

URL_WEB = "https://sistem-diag-default-rtdb.firebaseio.com/monitoreo.json"

def obtener_datos_registro():
    """Extrae info de BIOS y Hardware sin usar comandos externos (Evita el error wmic)."""
    datos = {"bios": "N/D", "age": "N/A", "ram_brand": "Genérica"}
    try:
        if platform.system() == "Windows":
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
    info_pro = obtener_datos_registro()

    while True:
        try:
            # 1. Escuchar comandos (Limpieza)
            res = requests.get(URL_WEB)
            if res.status_code == 200 and res.json().get("comando") == "limpiar":
                temp = os.environ.get('TEMP')
                for f in os.listdir(temp):
                    try: shutil.rmtree(os.path.join(temp, f))
                    except: continue
                requests.patch(URL_WEB, json={"comando": "listo"})

            # 2. Métricas de Red y Disco
            net_1 = psutil.net_io_counters()
            time.sleep(0.5)
            net_2 = psutil.net_io_counters()
            dl = round(((net_2.bytes_recv - net_1.bytes_recv) * 8) / (1024 * 1024), 2)
            
            disk = psutil.disk_usage("C:\\" if platform.system() == "Windows" else "/")
            disk_io = psutil.disk_io_counters()

            # 3. Proceso más pesado
            try:
                top_p = sorted(psutil.process_iter(['name', 'cpu_percent']), key=lambda p: p.info['cpu_percent'], reverse=True)[0].info['name']
            except: top_p = "Sistema"

            payload = {
                "info": {
                    "user": equipo,
                    "uptime": str(datetime.timedelta(seconds=int(time.time() - start_time))),
                    "disk_total": f"{round(disk.total/(1024**3))}GB",
                    "disk_free": f"{round(disk.free/(1024**3))}GB",
                    "net_speed": f"{dl} Mbps",
                    "top_proc": top_p,
                    "bios": info_pro["bios"],
                    "age": info_pro["age"],
                    "disk_errors": disk_io.read_err_count + disk_io.write_err_count
                },
                "stats": {
                    "cpu": int(psutil.cpu_percent()),
                    "ram": int(psutil.virtual_memory().percent),
                    "disk": int(disk.percent),
                    "bat": psutil.sensors_battery().percent if psutil.sensors_battery() else 100,
                    "charging": psutil.sensors_battery().power_plugged if psutil.sensors_battery() else True
                }
            }
            requests.put(URL_WEB, json=payload, timeout=1.5)
        except: pass
