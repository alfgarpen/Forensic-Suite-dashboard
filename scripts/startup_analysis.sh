#!/bin/bash
# startup_analysis.sh - Script para ejecutar el análisis forense al arrancar
# Generado por Antigravity

# Navegar al directorio del proyecto
cd /home/hackerguarro/Documentos/Forensic-Suite-dashboard

# Activar el entorno virtual
source .venv/bin/activate

# Ejecutar el pipeline completo
# --profile deep para un análisis completo (tarda más)
# --profile quick para un análisis rápido
python cli.py pipeline --profile deep

# Corregir propiedad de archivos generados para que el Dashboard pueda leerlos/escribirlos
chown -R hackerguarro:hackerguarro data/ uploads/

# Desactivar el entorno
deactivate
