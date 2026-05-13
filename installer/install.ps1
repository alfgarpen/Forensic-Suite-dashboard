# Forensic Suite Windows Installer
# Run as Administrator

$BASE_DIR = Resolve-Path "$PSScriptRoot\.."
$PYTHON_EXE = "python.exe"

Write-Host "=== Forensic Suite Windows Installation ===" -ForegroundColor Cyan

# 1. Check for Python
Write-Host "[*] Checking for Python installation..."
try {
    & $PYTHON_EXE --version
} catch {
    Write-Error "Python not found. Please install Python 3.8+ and add it to PATH."
    exit 1
}

# 2. Run core setup script
Write-Host "[*] Running core setup script..."
& $PYTHON_EXE "$PSScriptRoot\setup.py"

# 3. Windows Service Logic
# Note: Creating a Python service on Windows is cleaner with NSSM
Write-Host "[*] Windows Service setup..."
Write-Host "To run this as a persistent service, we recommend using NSSM (Non-Sucking Service Manager)."
Write-Host "Installation path: $BASE_DIR"

# Example of how to start it manually for now
Write-Host "[*] You can start the application manually using:"
Write-Host "$BASE_DIR\runtime\Scripts\python.exe $BASE_DIR\backend\app.py"

Write-Host "=== Installation Finished ===" -ForegroundColor Green
Write-Host "Dashboard available at http://localhost:5001"
