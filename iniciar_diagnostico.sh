#!/bin/bash

echo "=========================================="
echo "   HERRAMIENTA DE DIAGNOSTICO UNIVERSAL   "
echo "=========================================="

# 1. Intentar abrir el Dashboard automáticamente
URL="https://joselucianocaamal.github.io/diag-pc/"
echo "Abriendo Panel de Control en el navegador..."

if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    xdg-open "$URL" > /dev/null 2>&1
elif [[ "$OSTYPE" == "darwin"* ]]; then
    open "$URL"
fi

# 2. Instalando dependencias
echo "Instalando dependencias (psutil, pyserial, requests)..."
pip3 install psutil pyserial requests --quiet

# 3. Llamando al servidor de diagnóstico desde tu GitHub
echo "Llamando al servidor de diagnostico..."
python3 -c "import urllib.request; exec(urllib.request.urlopen('https://raw.githubusercontent.com/JoseLucianoCaamal/diag-pc/refs/heads/main/Servicio.py').read().decode('utf-8'))"