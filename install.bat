@echo off
echo ========================================================
echo   Instalador de Forensic Suite Dashboard
echo ========================================================
echo.

:: Verificar si Python esta instalado
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [!] Python no esta instalado o no esta en el PATH.
    echo Por favor, instala Python 3 (preferiblemente 3.10+) y vuelve a probar.
    pause
    exit /b
)

:: Crear entorno virtual si no existe
IF NOT EXIST ".venv" (
    echo [*] Creando entorno virtual (.venv)...
    python -m venv .venv
    IF %ERRORLEVEL% NEQ 0 (
        echo [!] Hubo un error creando el entorno virtual.
        pause
        exit /b
    )
) ELSE (
    echo [*] El entorno virtual ya existe.
)

:: Activar el entorno e instalar las dependencias
echo [*] Instalando dependencias desde requirements.txt...
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt

echo.
echo ========================================================
echo   Instalacion completada correctamente!
echo ========================================================
echo Puedes ejecutar el dashboard usando: run.bat
echo O bien, puedes ejecutar la CLI manualmente usando: 
echo   call .venv\Scripts\activate.bat
echo   python cli.py --help
echo.
pause
