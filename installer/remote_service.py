import os
import sys
from pathlib import Path

# Add backend to path
BASE_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = BASE_DIR / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from forensic_suite.core.remote_watcher import start_watcher

if __name__ == "__main__":
    # Ensure the reports directory exists
    reports_path = Path.home() / "Documentos" / "Reportes"
    reports_path.mkdir(parents=True, exist_ok=True)
    
    # Start the watchdog observer
    print("Forensic Suite: Remote Transfer Service starting...")
    start_watcher(str(reports_path))
