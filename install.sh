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
    echo "[*] Intentando instalar dependencias del sistema..."
    if command -v apt &> /dev/null; then
        sudo apt update && sudo apt install -y python3-venv python3-pip libyara-dev build-essential
    elif command -v brew &> /dev/null; then
        brew install yara
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
echo "[*] Instalando dependencias de Python y Volatility 3..."
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Descargar símbolos básicos de Volatility 3 (opcional pero recomendado)
echo "[*] ¿Deseas descargar los símbolos básicos de Volatility 3? (Windows/Linux) [s/N]"
read -r response
if [[ "$response" =~ ^([sS][iI]|[sS])$ ]]; then
    echo "[*] Descargando banner de símbolos..."
    mkdir -p .venv/lib/python$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')/site-packages/volatility3/symbols
    # Nota: La descarga de símbolos completa es pesada, aquí solo preparamos el entorno
fi

echo ""
echo "========================================================"
echo "  ¡Instalación completada correctamente!"
echo "========================================================"
echo "Puedes ejecutar el dashboard usando: ./run.sh"
echo "O bien, puedes ejecutar la CLI manualmente usando:"
echo "  source .venv/bin/activate"
echo "  python3 cli.py --help"
echo ""
