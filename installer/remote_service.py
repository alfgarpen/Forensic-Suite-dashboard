import os
import sys
import pwd
from pathlib import Path

# Add backend to path
BASE_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = BASE_DIR / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from forensic_suite.core.remote_watcher import start_watcher

if __name__ == "__main__":
    # Resolve the home directory of the user who owns the installation (to avoid /root/ when running as service)
    try:
        owner_uid = os.stat(BASE_DIR).st_uid
        USER_HOME = Path(pwd.getpwuid(owner_uid).pw_dir)
    except Exception:
        USER_HOME = Path.home()

    # Ensure the reports directory exists
    reports_path = USER_HOME / "Documentos" / "Reportes"
    reports_path.mkdir(parents=True, exist_ok=True)
    
    # Start the watchdog observer
    print(f"Forensic Suite: Remote Transfer Service starting for path: {reports_path}...")
    start_watcher(str(reports_path))
