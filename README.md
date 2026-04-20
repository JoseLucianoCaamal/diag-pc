# 🚀 CloudLink Hardware: Mobile PC Diagnostic Suite

### *Hardware Monitoring & Real-Time Analytics Platform*

**SistemDiag** es una solución híbrida de monitoreo de hardware diseñada para técnicos y entusiastas del mantenimiento de computadoras. El sistema extrae métricas críticas de rendimiento (CPU, RAM, Disco) en cualquier sistema operativo y las transmite simultáneamente a un hardware físico (ESP8266) y a un dashboard web en la nube en tiempo real.

---

## 🛠️ Arquitectura del Sistema

El proyecto se divide en cuatro capas de ingeniería integradas:

1.  **Core (Python Service):** Un script multiplataforma que utiliza la librería `psutil` para la recolección de métricas. Es capaz de identificar el modelo de CPU y el inventario de hardware de forma dinámica.
2.  **Edge Hardware (ESP8266 + OLED):** Un microcontrolador que recibe los datos por protocolo Serial (115200 baudios) y los visualiza en una pantalla física, ideal para diagnósticos donde no se puede ocupar la pantalla principal.
3.  **Cloud Backend (Firebase):** Una base de datos NoSQL en tiempo real (Realtime Database) que actúa como puente entre la laptop en reparación y el mundo exterior.
4.  **Frontend (GitHub Pages):** Un dashboard web con estética *Dark Tech* construido con HTML5, CSS3 y **Chart.js**, que permite el monitoreo remoto desde cualquier smartphone o tablet.

---

## ✨ Características Principales

* **⚡ Despliegue de Un Solo Clic:** Scripts de automatización (`.bat` y `.sh`) que configuran el entorno, instalan Python si es necesario y abren el dashboard automáticamente.
* **🌐 Monitoreo Remoto:** Visualización de gráficas de historial en tiempo real mediante Web Sockets y APIs REST.
* **🐧 Universal:** Compatible con **Windows (10/11), macOS y distribuciones de Linux**.
* **🏗️ Diseño Portable:** Arquitectura preparada para ejecutarse desde medios extraíbles sin dejar residuos en el sistema operativo del cliente.

---

## 🚀 Guía de Inicio Rápido

### En Windows:
1. Conecta tu dispositivo ESP8266 al puerto USB.
2. Ejecuta el archivo `iniciar_diagnostico.bat`.
3. El sistema configurará las dependencias y abrirá el navegador con el Dashboard.

### En Linux / macOS:
1. Abre una terminal en la carpeta del proyecto.
2. Otorga permisos de ejecución: `chmod +x iniciar_diagnostico.sh`.
3. Ejecuta: `./iniciar_diagnostico.sh`.
4. En su caso Propiedades del archivo.sh, habilitar la opcion de ejecutar como programa.

---

## 📊 Tecnologías Utilizadas

| Componente | Tecnología |
| :--- | :--- |
| **Lenguaje** | Python 3.x |
| **Dashboard** | HTML5 / JavaScript (ES6+) |
| **Gráficas** | Chart.js |
| **Base de Datos** | Firebase Realtime DB |
| **Hardware** | ESP8266 (NodeMCU/Wemos) |
| **Cloud Hosting** | GitHub Pages |

---

## 📋 Reporte de Flujo de Datos

El sistema sigue un flujo asíncrono para garantizar que el diagnóstico no afecte el rendimiento del equipo:
1. **Captura:** Lectura de sensores mediante `psutil` cada 1000ms.
2. **Serial Link:** Transmisión de trama `MON:cpu,ram,disk` vía UART.
3. **Cloud Push:** Sincronización mediante el método `PUT` hacia Firebase.
4. **Web Sync:** El Dashboard web realiza un refresco constante para actualizar los medidores y el gráfico de líneas.

---

**Desarrollado por:** [Jose Luciano Caamal](https://github.com/JoseLucianoCaamal)  
*Ingeniería en Computacion.*
