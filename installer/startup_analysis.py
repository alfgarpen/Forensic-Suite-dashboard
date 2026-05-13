import os
import subprocess
import sys
import datetime
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = BASE_DIR / "backend"
UPLOADS_DIR = BASE_DIR / "uploads"
SCRIPTS_DIR = BASE_DIR / "scripts"
RUNTIME_DIR = BASE_DIR / "runtime"

def run_startup_analysis():
    print("=== Forensic Suite: Automated Startup Pipeline ===")
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    python_exe = RUNTIME_DIR / "bin" / "python"
    if not python_exe.exists():
        python_exe = RUNTIME_DIR / "Scripts" / "python.exe"

    # 1. Perform Memory Acquisition
    print(f"[*] Phase 1: Acquiring fresh memory dump...")
    dump_filename = f"dump_{timestamp}.raw"
    dump_path = UPLOADS_DIR / dump_filename
    acq_script = SCRIPTS_DIR / "memory_acquisition.py"
    
    try:
        subprocess.check_call([
            str(python_exe), str(acq_script),
            "--output", str(dump_path)
        ])
        print(f"[*] Memory acquired successfully: {dump_filename}")
    except Exception as e:
        print(f"[!] Memory acquisition failed: {e}")
        return

    # 2. Run analysis using Volatility 3
    print(f"[*] Phase 2: Running Volatility 3 analysis...")
    analysis_script = SCRIPTS_DIR / "analyze_dump.py"
    results_path = BASE_DIR / "artifacts" / f"results_{timestamp}.json"
    
    try:
        subprocess.check_call([
            str(python_exe), str(analysis_script),
            "--input", str(dump_path),
            "--output", str(results_path)
        ])
        print("[*] Analysis complete.")
    except Exception as e:
        print(f"[!] Analysis failed: {e}")
        return

    # 3. Generate report
    print(f"[*] Phase 3: Generating timestamped HTML report...")
    report_script = SCRIPTS_DIR / "generate_report.py"
    report_name = f"reporte_{timestamp}.html"
    
    try:
        subprocess.check_call([
            str(python_exe), str(report_script),
            "--results", str(results_path),
            "--output", str(BASE_DIR / "reports" / report_name)
        ])
        print(f"[*] Startup pipeline finished. Report: {report_name}")
    except Exception as e:
        print(f"[!] Report generation failed: {e}")

if __name__ == "__main__":
    run_startup_analysis()

if __name__ == "__main__":
    run_startup_analysis()
