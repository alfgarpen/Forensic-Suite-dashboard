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
    python_bin = "python3" if platform.system() != "Windows" else "python"
    
    # Executable path inside venv
    if platform.system() == "Windows":
        python_venv = RUNTIME_DIR / "Scripts" / "python.exe"
    else:
        python_venv = RUNTIME_DIR / "bin" / "python"

    if not RUNTIME_DIR.exists():
        print(f"    - Creating venv using {python_bin}...")
        subprocess.check_call([python_bin, "-m", "venv", str(RUNTIME_DIR)])
    
    print("[*] Installing/Updating dependencies...")
    req_path = BACKEND_DIR / "requirements.txt"
    if req_path.exists():
        subprocess.check_call([str(python_venv), "-m", "pip", "install", "--upgrade", "pip"])
        subprocess.check_call([str(python_venv), "-m", "pip", "install", "-r", str(req_path)])
        print("    - All dependencies installed.")
    else:
        print(f"    [!] Error: {req_path} not found.")

def configure_app():
    print("[*] Initializing portable configuration...")
    settings_file = CONFIG_DIR / "settings.json"
    remote_config_file = CONFIG_DIR / "remote_config.json"
    
    # Default core settings
    if not settings_file.exists():
        settings = {
            "base_dir": str(BASE_DIR),
            "port": 5001,
            "debug": False
        }
        with open(settings_file, "w") as f:
            json.dump(settings, f, indent=4)
        print("    - Created settings.json")

    # Default remote config
    if not remote_config_file.exists():
        remote_config = {
            "remote_host": "127.0.0.1",
            "remote_user": "forensic",
            "remote_password": "YOUR_SSH_PASSWORD",
            "remote_port": 22,
            "remote_path": "/home/forensic/reports/",
            "enabled": false,
            "auto_rename": true,
            "verify_integrity": true
        }
        with open(remote_config_file, "w") as f:
            json.dump(remote_config, f, indent=4)
        print("    - Created remote_config.json (template)")

def setup_volatility():
    print("[*] Ensuring Volatility 3 is present...")
    if not (VOLATILITY_DIR / "vol.py").exists():
        print("    - Cloning Volatility 3 from GitHub...")
        try:
            subprocess.check_call(["git", "clone", "--depth", "1", "https://github.com/volatilityfoundation/volatility3.git", str(VOLATILITY_DIR)])
        except Exception as e:
            print(f"    [!] Error cloning Volatility: {e}")
    else:
        print("    - Volatility 3 already installed.")

def main():
    print("\n" + "="*40)
    print("      Forensic Suite - Setup Script")
    print("="*40 + "\n")
    
    create_dirs()
    setup_volatility()
    setup_venv()
    configure_app()
    
    print("\n" + "="*40)
    print("      Environment Setup Complete!")
    print("="*40)
    print("Next: Run 'sudo ./installer/install.sh' to finalize.\n")

if __name__ == "__main__":
    main()
