@echo off
setlocal

echo ========================================================
echo   REINICIANDO FORENSIC SUITE DASHBOARD
echo ========================================================
echo.

:: 1. Intentar cerrar procesos existentes por titulo de ventana
echo [*] Deteniendo instancias previas...
taskkill /FI "WINDOWTITLE eq Forensic Suite Dashboard*" /T /F >nul 2>&1

:: 2. Tambien intentar cerrar por el puerto si es posible (opcional)
:: netstat -ano | findstr :5000 -> taskkill /PID ...

echo [*] Esperando a que los procesos se liberen...
timeout /t 2 /nobreak >nul

:: 3. Iniciar una nueva instancia
echo [*] Iniciando nueva instancia...
start run.bat

echo.
echo [OK] El dashboard se esta reiniciando en una nueva ventana.
echo Puedes cerrar esta ventana.
timeout /t 3 >nul
exit
