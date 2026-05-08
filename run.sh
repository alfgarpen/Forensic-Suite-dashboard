#!/bin/bash
echo "[*] Iniciando Forensic Suite Dashboard..."
echo ""

if [ ! -f ".venv/bin/activate" ]; then
    echo "[!] El entorno virtual no existe."
    echo "Por favor, ejecuta bash install.sh primero."
    exit 1
fi

source .venv/bin/activate
python3 app.py
