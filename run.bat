@echo off
echo [*] Iniciando Forensic Suite Dashboard...
echo.

IF NOT EXIST ".venv\Scripts\activate.bat" (
    echo [!] El entorno virtual no existe.
    echo Por favor, ejecuta install.bat primero.
    pause
    exit /b
)

call .venv\Scripts\activate.bat
python app.py

pause
