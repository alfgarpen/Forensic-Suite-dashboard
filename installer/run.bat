@echo off
title Forensic Suite Dashboard
setlocal enabledelayedexpansion

echo ========================================================
echo   INICIANDO FORENSIC SUITE DASHBOARD
echo ========================================================
echo.

:: Verificar si existe el entorno
if not exist ".venv\Scripts\activate.bat" (
    echo [!] ERROR: No se encuentra el entorno virtual.
    echo Por favor, ejecuta 'install.bat' primero.
    pause
    exit /b 1
)

:: Activar y ejecutar
echo [*] Activando entorno virtual...
call .venv\Scripts\activate.bat

echo [*] Lanzando servidor Flask...
echo [!] El dashboard estara disponible en: http://127.0.0.1:5000
echo.

:: Ejecutar Flask
python app.py

if %ERRORLEVEL% neq 0 (
    echo.
    echo [!] El servidor se ha detenido de forma inesperada (Codigo: %ERRORLEVEL%).
    pause
)
