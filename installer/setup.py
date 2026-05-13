import os
import sys
import subprocess
import platform
import json
import shutil
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = BASE_DIR / "backend"
RUNTIME_DIR = BASE_DIR / "runtime"
CONFIG_DIR = BASE_DIR / "config"
LOGS_DIR = BASE_DIR / "logs"
UPLOADS_DIR = BASE_DIR / "uploads"
ARTIFACTS_DIR = BASE_DIR / "artifacts"
REPORTS_DIR = BASE_DIR / "reports"
VOLATILITY_DIR = BASE_DIR / "volatility3"

def create_dirs():
    print("[*] Creating directory structure...")
    dirs = [CONFIG_DIR, LOGS_DIR, UPLOADS_DIR, ARTIFACTS_DIR, REPORTS_DIR, VOLATILITY_DIR]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
        print(f"    - Created: {d.relative_to(BASE_DIR)}")

def setup_venv():
    print("[*] Setting up virtual environment in 'runtime'...")
    if platform.system() == "Windows":
        python_venv = RUNTIME_DIR / "Scripts" / "python.exe"
    else:
        python_venv = RUNTIME_DIR / "bin" / "python"

    if not RUNTIME_DIR.exists() or not python_venv.exists():
        if RUNTIME_DIR.exists():
            print("[!] venv directory exists but python not found. Cleaning up...")
            shutil.rmtree(RUNTIME_DIR)
        subprocess.check_call([sys.executable, "-m", "venv", str(RUNTIME_DIR)])
    
    print("[*] Installing dependencies from backend/requirements.txt...")
    req_path = BACKEND_DIR / "requirements.txt"
    if req_path.exists():
        # Use python -m pip as it's more reliable
        subprocess.check_call([str(python_venv), "-m", "pip", "install", "--upgrade", "pip"])
        subprocess.check_call([str(python_venv), "-m", "pip", "install", "-r", str(req_path)])
    else:
        print("[!] requirements.txt not found in backend directory.")

def configure_app():
    print("[*] Configuring application settings...")
    settings = {
        "base_dir": str(BASE_DIR),
        "backend_dir": str(BACKEND_DIR),
        "uploads_dir": str(UPLOADS_DIR),
        "artifacts_dir": str(ARTIFACTS_DIR),
        "reports_dir": str(REPORTS_DIR),
        "logs_dir": str(LOGS_DIR),
        "volatility_path": str(VOLATILITY_DIR),
        "port": 5001,
        "debug": False
    }
    
    config_file = CONFIG_DIR / "settings.json"
    with open(config_file, "w") as f:
        json.dump(settings, f, indent=4)
    print(f"    - Configured: {config_file.relative_to(BASE_DIR)}")

def setup_volatility():
    print("[*] Checking Volatility 3 setup...")
    vol_main = VOLATILITY_DIR / "vol.py"
    if not vol_main.exists():
        print("[!] Volatility 3 not found. Attempting to download...")
        try:
            subprocess.check_call(["git", "clone", "https://github.com/volatilityfoundation/volatility3.git", str(VOLATILITY_DIR)])
            print("[*] Volatility 3 downloaded successfully.")
        except Exception as e:
            print(f"[!] Failed to download Volatility 3: {e}")
            print("[!] Please ensure 'git' is installed or manually place Volatility 3 in the 'volatility3' folder.")
    else:
        print("[*] Volatility 3 found.")

    # Setup symbol tables (optional but recommended)
    # We could download standard symbol tables here if needed.

def main():
    print("=== Forensic Suite Installer ===")
    create_dirs()
    setup_venv()
    configure_app()
    setup_volatility()
    print("=== Setup Complete ===")

if __name__ == "__main__":
    main()
