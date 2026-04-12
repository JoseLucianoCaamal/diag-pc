@echo off
setlocal
title Diagnostico Pro v3.0 - Hibrido Local/Web
color 0b

echo ==========================================
echo    HERRAMIENTA DE DIAGNOSTICO UNIVERSAL
echo ==========================================
echo.

:: 1. VERIFICAR PYTHON
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Python no detectado. Instalando motor de sistema...
    powershell -Command "Invoke-WebRequest -Uri https://www.python.org/ftp/python/3.11.4/python-3.11.4-amd64.exe -OutFile python_installer.exe"
    echo [!] Ejecutando instalador silencioso...
    start /wait python_installer.exe /quiet InstallAllUsers=1 PrependPath=1
    del python_installer.exe
    echo [OK] Python instalado. Por favor, cierra y abre este archivo de nuevo.
    pause
    exit
)

:: 2. PREPARAR LIBRERIAS
echo [STEP 1] Revisando dependencias (psutil, pyserial, requests)...
:: Agregamos 'requests' por si acaso no estaba
pip install psutil pyserial requests --quiet

:: 3. ABRIR DASHBOARD AUTOMATICAMENTE
echo [STEP 2] Abriendo Panel de Control en el navegador...
start https://joselucianocaamal.github.io/diag-pc/

:: 4. DESCARGAR Y EJECUTAR DESDE GITHUB
echo [STEP 3] Conectando con Servicio.py en la nube...
echo.
python -c "import urllib.request; exec(urllib.request.urlopen('https://raw.githubusercontent.com/JoseLucianoCaamal/diag-pc/refs/heads/main/Servicio.py').read().decode('utf-8'))"

:: 5. MANEJO DE ERRORES
if %errorlevel% neq 0 (
    color 0c
    echo.
    echo [ERROR] No se pudo ejecutar el diagnostico.
    echo Verifique:
    echo 1. Conexion a Internet (necesaria para bajar el script).
    echo 2. Que el ESP8266 este conectado correctamente.
    echo 3. Que el puerto COM no este usado por otro programa (como Arduino IDE).
    pause
)