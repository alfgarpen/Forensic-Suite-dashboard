#!/bin/bash
echo "========================================================"
echo "  Reiniciando entorno de Forensic Suite Dashboard"
echo "========================================================"
echo ""

# 1. Detener procesos existentes (si los hay)
echo "[*] Buscando procesos activos de app.py..."
pids=$(pgrep -f "python3 app.py")
if [ -n "$pids" ]; then
    echo "[*] Deteniendo procesos: $pids"
    kill $pids
    sleep 2
fi

# 2. Eliminar el entorno virtual actual
if [ -d ".venv" ]; then
    echo "[*] Eliminando entorno virtual existente (.venv)..."
    rm -rf .venv
else
    echo "[*] No se encontró entorno virtual para eliminar."
fi

# 3. Ejecutar el instalador para recrear todo
if [ -f "install.sh" ]; then
    echo "[*] Ejecutando instalación limpia..."
    bash install.sh
else
    echo "[!] No se encontró install.sh. Intentando creación manual..."
    python3 -m venv .venv
    source .venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
fi

# 4. Iniciar la aplicación
if [ -f "run.sh" ]; then
    echo "[*] Iniciando la aplicación..."
    bash run.sh
else
    echo "[!] No se encontró run.sh. Iniciando manualmente..."
    source .venv/bin/activate
    python3 app.py
fi
