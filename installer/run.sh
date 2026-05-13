#!/bin/bash
echo "[*] Iniciando Forensic Suite Dashboard..."
echo ""

if [ ! -f ".venv/bin/activate" ]; then
    echo "[!] El entorno virtual no existe."
    echo "Por favor, ejecuta bash install.sh primero."
    exit 1
fi

source .venv/bin/activate

# Verificar si Volatility 3 está disponible como módulo
if ! python3 -c "import volatility3" &> /dev/null; then
    echo "[!] Volatility 3 no está correctamente instalado en el entorno virtual."
    echo "[*] Reintentando instalación de dependencias..."
    pip install -r requirements.txt
fi

echo "[+] Entorno listo. Iniciando servidor Flask..."
echo "[+] URL: http://127.0.0.1:5001"
echo "--------------------------------------------------------"
python3 app.py
