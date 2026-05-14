import os
import subprocess
import sys
import json
import shutil
import datetime
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = BASE_DIR / "backend"
UPLOADS_DIR = BASE_DIR / "uploads"
SCRIPTS_DIR = BASE_DIR / "scripts"
RUNTIME_DIR = BASE_DIR / "runtime"
DATA_DIR = BASE_DIR / "data"
ARTIFACTS_DIR = BASE_DIR / "artifacts"
REPORTS_DIR = BASE_DIR / "reports"
TEMPLATES_DIR = BASE_DIR / "frontend" / "templates"

# Inject backend into path so we can import forensic_suite directly
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


def generate_report_like_web(results_path: Path, output_path: Path) -> bool:
    """
    Generates the HTML report using the exact same Reporting class as the web dashboard.
    This guarantees identical output (alerts, severity, findings normalization, etc.).
    """
    from forensic_suite.core.reporting import Reporting
    
    # Load results JSON
    with open(results_path, 'r', encoding='utf-8') as f:
        results_data = json.load(f)

    # Enrich metadata to match Reporting.generate_html_report expectations
    metadata = results_data.setdefault('metadata', {})
    
    state_file = DATA_DIR / "current_dump.json"
    if state_file.exists():
        with open(state_file, 'r') as f:
            active = json.load(f)
        
        # Match reporting.py expectations: metadata['hashes'], metadata['dump_size_bytes']
        metadata.update({
            "dump_path": active.get('active_memory_dump'),
            "hashes": {"md5": "N/A", "sha256": active.get('hash', 'N/A')},
            "dump_size_bytes": active.get('size_bytes', 0),
            "acquisition_source": active.get('source', 'startup_automated'),
            "acquisition_time": active.get('timestamp'),
        })

    reporter = Reporting(str(TEMPLATES_DIR))
    return reporter.generate_html_report(results_data, str(output_path))


def run_startup_analysis():
    print("=== Forensic Suite: Automated Startup Pipeline ===")

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    python_exe = RUNTIME_DIR / "bin" / "python"
    if not python_exe.exists():
        python_exe = RUNTIME_DIR / "Scripts" / "python.exe"

    # Ensure directories exist
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Memory Acquisition
    print("[*] Phase 1: Acquiring fresh memory dump...")
    dump_filename = f"dump_{timestamp}.raw"
    dump_path = UPLOADS_DIR / dump_filename
    acq_script = SCRIPTS_DIR / "memory_acquisition.py"

    try:
        subprocess.check_call([str(python_exe), str(acq_script), "--output", str(dump_path)])
        print(f"[*] Memory acquired: {dump_filename}")
    except Exception as e:
        print(f"[!] Memory acquisition failed: {e}")
        return

    # 2. Volatility 3 Analysis
    print("[*] Phase 2: Running Volatility 3 analysis...")
    analysis_script = SCRIPTS_DIR / "analyze_dump.py"
    results_path = ARTIFACTS_DIR / f"results_{timestamp}.json"

    try:
        subprocess.check_call([
            str(python_exe), str(analysis_script),
            "--dump", str(dump_path),
            "--output", str(results_path)
        ])
        print("[*] Analysis complete.")
    except Exception as e:
        print(f"[!] Analysis failed: {e}")
        return

    # 3. Generate report using the same engine as the web dashboard
    print("[*] Phase 3: Generating HTML report (web-identical engine)...")
    report_name = f"reporte_{timestamp}.html"
    report_output = REPORTS_DIR / report_name

    try:
        # Before generating report, we need a current_dump.json for metadata enrichment
        dump_size_bytes = os.path.getsize(dump_path)
        state = {
            "active_memory_dump": str(dump_path),
            "filename": dump_filename,
            "status": "analysis_completed",
            "last_results": str(DATA_DIR / "results.json"),
            "timestamp": timestamp,
            "size_bytes": dump_size_bytes,
            "size_human": f"{dump_size_bytes // (1024 * 1024)} MB",
            "hash": "N/A",
            "source": "startup_automated"
        }
        with open(DATA_DIR / "current_dump.json", 'w') as f:
            json.dump(state, f, indent=4)

        success = generate_report_like_web(results_path, report_output)
        if not success:
            print("[!] Report generation failed (template error).")
            return

        # 4. Update dashboard active state
        print("[*] Updating dashboard active state...")

        # Copy to data/ so it's accessible as file:// and via /download/report
        shutil.copy2(results_path, DATA_DIR / "results.json")
        shutil.copy2(report_output, DATA_DIR / "report.html")

        # Fix ownership and permissions
        # Get UID/GID from BASE_DIR to match the user's workspace
        stat_info = os.stat(BASE_DIR)
        uid, gid = stat_info.st_uid, stat_info.st_gid

        for f in [dump_path, results_path, report_output,
                  DATA_DIR / "results.json", DATA_DIR / "report.html",
                  DATA_DIR / "current_dump.json"]:
            os.chmod(f, 0o644)
            try:
                os.chown(f, uid, gid)
            except:
                pass

        print(f"[*] Startup pipeline finished. Report: {report_name}")
        print(f"[*] Also available at: {DATA_DIR / 'report.html'}")

    except Exception as e:
        print(f"[!] Report generation or state update failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_startup_analysis()
