@echo off
setlocal enabledelayedexpansion

:: Colores (aproximados en CMD)
set "HEADER_COLOR=0B"
set "NORMAL_COLOR=07"

color !HEADER_COLOR!
echo ========================================================
echo   FORENSIC SUITE DASHBOARD - INSTALADOR
echo ========================================================
echo.
color !NORMAL_COLOR!

:: 1. Verificar Python
echo [*] Verificando instalacion de Python...
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [!] ERROR: Python no esta instalado o no esta en el PATH.
    echo Por favor, instala Python 3.10 o superior: https://www.python.org/
    pause
    exit /b 1
)

:: 2. Crear directorios base
echo [*] Configurando estructura de directorios...
if not exist "data" mkdir data
if not exist "uploads" mkdir uploads
if not exist "data\artifacts" mkdir data\artifacts

:: 3. Entorno Virtual
if not exist ".venv" (
    echo [*] Creando entorno virtual (.venv)...
    python -m venv .venv
    if !ERRORLEVEL! neq 0 (
        echo [!] ERROR: No se pudo crear el entorno virtual.
        pause
        exit /b 1
    )
) else (
    echo [OK] Entorno virtual ya existe.
)

:: 4. Instalacion de dependencias
echo [*] Instalando dependencias (esto puede tardar unos minutos)...
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip >nul
pip install -r requirements.txt
if !ERRORLEVEL! neq 0 (
    echo [!] ERROR: La instalacion de dependencias fallo.
    pause
    exit /b 1
)

echo.
color 0A
echo ========================================================
echo   INSTALACION COMPLETADA EXITOSAMENTE
echo ========================================================
echo.
echo Para iniciar el dashboard: run.bat
echo Para reiniciar si hay problemas: restart.bat
echo.
color !NORMAL_COLOR!
pause
