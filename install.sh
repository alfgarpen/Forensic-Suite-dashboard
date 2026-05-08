#!/bin/bash
echo "========================================================"
echo "  Instalador de Forensic Suite Dashboard (Linux/MacOS)"
echo "========================================================"
echo ""

# Verificar si Python o Python3 está instalado
if ! command -v python3 &> /dev/null
then
    echo "[!] Python3 no está instalado o no está en el PATH."
    echo "Por favor, instala la versión más reciente (ej. sudo apt install python3) y vuelve a probar."
    exit 1
fi

# Verificar si python3-venv está instalado (necesario en Ubuntu/Debian)
if ! python3 -m venv --help &> /dev/null
then
    echo "[!] python3-venv no está instalado."
    echo "[*] Intentando instalar python3-venv..."
    sudo apt update && sudo apt install -y python3-venv
    
    if [ $? -ne 0 ]; then
        echo "[!] Falló la instalación automática de python3-venv."
        echo "Por favor, ejecute: sudo apt install python3-venv"
        exit 1
    fi
fi

# Crear entorno virtual si no existe
if [ ! -d ".venv" ]; then
    echo "[*] Creando entorno virtual (.venv)..."
    python3 -m venv .venv
    
    if [ $? -ne 0 ]; then
        echo "[!] Hubo un error creando el entorno virtual."
        exit 1
    fi
else
    echo "[*] El entorno virtual ya existe."
fi

# Activar el entorno e instalar las dependencias
echo "[*] Instalando dependencias desde requirements.txt..."
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "========================================================"
echo "  ¡Instalación completada correctamente!"
echo "========================================================"
echo "Puedes ejecutar el dashboard usando: ./run.sh"
echo "O bien, puedes ejecutar la CLI manualmente usando:"
echo "  source .venv/bin/activate"
echo "  python3 cli.py --help"
echo ""
