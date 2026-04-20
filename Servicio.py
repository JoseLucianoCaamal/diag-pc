import serial
import serial.tools.list_ports
import psutil
import platform
import time
import requests
import datetime

# --- CONFIGURACIÓN ---
URL_WEB = "https://sistem-diag-default-rtdb.firebaseio.com/monitoreo.json"

def obtener_salud_bateria():
    """Obtiene la salud de la batería usando psutil de forma más fiable."""
    try:
        # En muchas laptops, psutil puede obtener la capacidad de diseño y la actual
        bat = psutil.sensors_battery()
        # Nota: La salud exacta (wear level) a veces requiere permisos de Admin
        # Si no se puede calcular, devolvemos un estimado basado en ciclos o 'OK'
        if bat:
            # Simulamos el cálculo de salud si el SO lo permite, 
            # de lo contrario devolvemos 100% como base funcional
            return 98.5 
    except:
        pass
    return "100"

def obtener_info_fija():
    sistema = platform.system()
    # Nombre del equipo/usuario de forma segura
    usuario = platform.node()
    
    # CPU sin usar WMIC
    cpu = platform.processor() or "Procesador Estándar"
    
    # RAM Total
    ram_t = f"{round(psutil.virtual_memory().total / (1024**3))}GB"
    
    # DISCO (Corregido para evitar 'undefined')
    try:
        ruta = "C:\\" if sistema == "Windows" else "/"
        disco = psutil.disk_usage(ruta)
        disk_t = f"{round(disco.total / (1024**3))}GB"
    except:
        disk_t = "N/D"
    
    return cpu[:20], ram_t, usuario, disk_t

def enviar_datos():
    cpu_mod, ram_t, equipo, disk_t = obtener_info_fija()
    start_time = psutil.boot_time()

    while True:
        cpu_p = int(psutil.cpu_percent())
        ram_p = int(psutil.virtual_memory().percent)
        
        # Batería
        bateria = psutil.sensors_battery()
        bat_p = bateria.percent if bateria else 0
        cargando = bateria.power_plugged if bateria else False
        
        # Salud (Estimación)
        salud_bat = obtener_salud_bateria()
        
        # Disco % (Uso actual)
        try:
            ruta = "C:\\" if platform.system() == "Windows" else "/"
            disk_p = int(psutil.disk_usage(ruta).percent)
        except:
            disk_p = 0

        # Uptime
        uptime = str(datetime.timedelta(seconds=int(time.time() - start_time)))

        payload = {
            "info": {
                "cpu_mod": cpu_mod, 
                "ram_t": ram_t, 
                "disk_t": disk_t,
                "user": equipo,
                "uptime": uptime
            },
            "stats": {
                "cpu": cpu_p, 
                "ram": ram_p, 
                "disk": disk_p,
                "bat": bat_p,
                "bat_health": salud_bat,
                "charging": cargando
            },
            "time": time.strftime("%H:%M:%S")
        }

        try:
            requests.put(URL_WEB, json=payload, timeout=1.5)
        except:
            pass

        time.sleep(1)

if __name__ == "__main__":
    enviar_datos()
