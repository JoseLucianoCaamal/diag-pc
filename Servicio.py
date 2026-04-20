import psutil
import platform
import time
import requests
import datetime
import os
import shutil
import winreg

# --- CONFIGURACIÓN ---
URL_WEB = "https://sistem-diag-default-rtdb.firebaseio.com/monitoreo.json"

def obtener_info_bios():
    """Extrae el año de la BIOS de forma nativa para evitar cierres."""
    try:
        if platform.system() == "Windows":
            path = r"HARDWARE\DESCRIPTION\System\BIOS"
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path) as key:
                bios_date = winreg.QueryValueEx(key, "BIOSReleaseDate")[0]
                return bios_date.split('/')[-1] if '/' in bios_date else bios_date[-4:]
    except: return "N/D"

def enviar_datos():
    equipo = platform.node()
    cpu_mod = platform.processor()[:25]
    start_time = psutil.boot_time()
    bios_year = obtener_info_bios()

    print(f">>> SISTEMDIAG ACTIVO EN: {equipo}")
    print(">>> Presiona Ctrl+C para detener.")

    while True:
        try:
            # 1. Escuchar comando de limpieza (con manejo de error de red)
            try:
                res = requests.get(URL_WEB, timeout=2)
                if res.status_code == 200 and res.json().get("comando") == "limpiar":
                    temp = os.environ.get('TEMP')
                    for f in os.listdir(temp):
                        try: shutil.rmtree(os.path.join(temp, f))
                        except: continue
                    requests.patch(URL_WEB, json={"comando": "listo"})
            except: pass

            # 2. Métricas básicas seguras
            cpu_p = int(psutil.cpu_percent())
            ram_p = int(psutil.virtual_memory().percent)
            bat = psutil.sensors_battery()
            
            # Disco (Evita errores si la unidad no responde)
            try:
                disk = psutil.disk_usage("C:\\")
                disk_p, disk_f, disk_t = int(disk.percent), f"{round(disk.free/1024**3)}GB", f"{round(disk.total/1024**3)}GB"
            except:
                disk_p, disk_f, disk_t = 0, "N/D", "N/D"

            # 3. Envío de datos
            payload = {
                "info": {
                    "user": equipo, "cpu_mod": cpu_mod, "bios": bios_year,
                    "disk_free": disk_f, "disk_total": disk_t,
                    "uptime": str(datetime.timedelta(seconds=int(time.time() - start_time)))
                },
                "stats": {
                    "cpu": cpu_p, "ram": ram_p, "disk": disk_p,
                    "bat": bat.percent if bat else 100, "charging": bat.power_plugged if bat else True
                }
            }
            requests.put(URL_WEB, json=payload, timeout=2)

        except Exception as e:
            # ESTA ES LA CLAVE: Si algo falla, el script sigue vivo
            print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Reintentando conexión...")
        
        time.sleep(1)

if __name__ == "__main__":
    enviar_datos()
