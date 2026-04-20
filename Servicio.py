import serial
import serial.tools.list_ports
import psutil
import platform
import subprocess
import time
import requests
import datetime

# --- CONFIGURACIÓN ---
URL_WEB = "https://sistem-diag-default-rtdb.firebaseio.com/monitoreo.json"

def obtener_salud_bateria():
    """Calcula la salud de la batería en Windows."""
    try:
        if platform.system() == "Windows":
            # Obtenemos capacidad de diseño y capacidad a carga completa
            cmd_cap = "wmic /namespace:\\\\root\\wmi path BatteryStaticData get DesignedCapacity"
            cmd_full = "wmic /namespace:\\\\root\\wmi path BatteryFullChargeCapacity get FullChargeCapacity"
            
            cap_diseno = int(subprocess.check_output(cmd_cap, shell=True).decode().split('\n')[1].strip())
            cap_actual = int(subprocess.check_output(cmd_full, shell=True).decode().split('\n')[1].strip())
            
            salud = (cap_actual / cap_diseno) * 100
            return round(min(salud, 100), 1)
    except:
        pass
    return "N/A"

def obtener_info_fija():
    sistema = platform.system()
    user = subprocess.check_output("whoami", shell=True).decode().strip().split('\\')[-1]
    
    try:
        if sistema == "Windows":
            cmd = "wmic cpu get name"
            raw = subprocess.check_output(cmd, shell=True).decode().strip().split('\n')
            cpu = raw[1].strip() if len(raw) > 1 else platform.processor()
        else:
            cpu = platform.processor()
    except: cpu = "Generic CPU"

    ram_t = f"{round(psutil.virtual_memory().total / (1024**3))}GB"
    return cpu[:18], ram_t, user

def enviar_datos():
    cpu_mod, ram_t, usuario = obtener_info_fija()
    esp = None
    start_time = psutil.boot_time()

    while True:
        # Métricas principales
        cpu_p = int(psutil.cpu_percent())
        ram_p = int(psutil.virtual_memory().percent)
        
        # Batería: Nivel, Carga y Salud
        bateria = psutil.sensors_battery()
        bat_p = bateria.percent if bateria else 0
        cargando = bateria.power_plugged if bateria else False
        salud_bat = obtener_salud_bateria()
        
        # Tiempo de actividad (Uptime)
        uptime = str(datetime.timedelta(seconds=int(time.time() - start_time)))

        payload = {
            "info": {
                "cpu_mod": cpu_mod, 
                "ram_t": ram_t, 
                "user": usuario,
                "uptime": uptime
            },
            "stats": {
                "cpu": cpu_p, 
                "ram": ram_p, 
                "bat": bat_p,
                "bat_health": salud_bat,
                "charging": cargando
            },
            "time": time.strftime("%H:%M:%S")
        }

        try:
            requests.put(URL_WEB, json=payload, timeout=1.5)
        except: pass

        # Comunicación Serial (ESP8266)
        if esp:
            try:
                esp.write(bytes(f"MON:{cpu_p},{ram_p},{bat_p}\n", 'utf-8'))
            except: esp = None
        else:
            # Intento de reconexión simplificado
            for p in serial.tools.list_ports.comports():
                if "USB" in p.description.upper() or "CH340" in p.description.upper():
                    try:
                        esp = serial.Serial(port=p.device, baudrate=115200, timeout=1)
                    except: pass

        time.sleep(1)

if __name__ == "__main__":
    enviar_datos()
