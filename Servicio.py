import serial
import serial.tools.list_ports
import psutil
import platform
import subprocess
import time

# --- FUNCIONES DE DETECCIÓN DE HARDWARE ---

def obtener_nombre_cpu():
    sistema = platform.system()
    try:
        if sistema == "Windows":
            # Comando directo de Windows para el nombre real
            cmd = "wmic cpu get name"
            raw = subprocess.check_output(cmd, shell=True).decode('utf-8')
            name = raw.split('\n')[1].strip()
        elif sistema == "Darwin": # macOS
            cmd = "sysctl -n machdep.cpu.brand_string"
            name = subprocess.check_output(cmd, shell=True).decode('utf-8').strip()
        else: # Linux
            cmd = "grep 'model name' /proc/cpuinfo | head -n 1"
            name = subprocess.check_output(cmd, shell=True).decode('utf-8').split(":")[1].strip()
        
        # Limpieza para que quepa en el OLED (max 18 carac)
        clean_name = name.replace("Intel(R) Core(TM) ", "").replace("CPU ", "").split("@")[0]
        return clean_name.strip()[:18]
    except:
        return platform.processor()[:18]

def obtener_datos_sistema():
    sistema = platform.system()
    ruta_disco = "C:" if sistema == "Windows" else "/"
    
    # 1. RAM Total
    ram_t = f"{round(psutil.virtual_memory().total / (1024**3))}GB"
    
    # 2. Disco Total
    try:
        disk_t = f"{round(psutil.disk_usage(ruta_disco).total / (1024**3))}GB"
    except:
        disk_t = "Error"
        
    # 3. Porcentajes de monitoreo
    cpu_p = int(psutil.cpu_percent())
    ram_p = int(psutil.virtual_memory().percent)
    disk_p = int(psutil.disk_usage(ruta_disco).percent)
    
    return cpu_p, ram_p, disk_p, ram_t, disk_t

# --- LÓGICA DE CONEXIÓN Y ENVÍO ---

def buscar_esp8266():
    """Busca el puerto serial del ESP8266 dinámicamente."""
    puertos = serial.tools.list_ports.comports()
    for p in puertos:
        desc = p.description.upper()
        # Buscamos palabras clave de los drivers del ESP
        if any(x in desc for x in ["CH340", "CP210", "USB-SERIAL", "USB SERIAL"]):
            return p.device
    return None

def ejecutar_diagnostico():
    esp = None
    cpu_modelo = obtener_nombre_cpu()
    print(f"Sistema detectado: {platform.system()}")
    print(f"Procesador: {cpu_modelo}")

    while True:
        if esp is None:
            puerto = buscar_esp8266()
            if puerto:
                try:
                    esp = serial.Serial(port=puerto, baudrate=115200, timeout=1)
                    print(f"--> ESP8266 encontrado en {puerto}")
                    time.sleep(2) # Pausa para que el ESP despierte
                    
                    # Enviar Inventario una vez al conectar
                    _, _, _, ram_t, disk_t = obtener_datos_sistema()
                    paquete_inv = f"INV:{cpu_modelo},{ram_t},{disk_t}\n"
                    esp.write(bytes(paquete_inv, 'utf-8'))
                except:
                    esp = None
            else:
                print("Buscando ESP8266... conecta el dispositivo.")
                time.sleep(3)
                continue

        try:
            # Obtener y enviar monitoreo
            c, r, d, _, _ = obtener_datos_sistema()
            paquete_mon = f"MON:{c},{r},{d}\n"
            esp.write(bytes(paquete_mon, 'utf-8'))
            time.sleep(1)
        except:
            print("(!) Conexión perdida con el dispositivo.")
            esp = None

if __name__ == "__main__":
    ejecutar_diagnostico()
