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


def generate_report_like_web(results_data: dict, output_path: Path) -> bool:
    """
    Generates the HTML report using the exact same Reporting class as the web dashboard.
    """
    from forensic_suite.core.reporting import Reporting
    
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

    # 2. Forensic Analysis Engine
    print("[*] Phase 2: Running Forensic Analysis Engine...")
    from forensic_suite.core.analysis_engine import AnalysisEngine
    results_path = ARTIFACTS_DIR / f"results_{timestamp}.json"

    try:
        engine = AnalysisEngine(str(dump_path))
        # Run standard plugins (None = default set)
        results_data = engine.run_analysis()
        
        with open(results_path, 'w', encoding='utf-8') as f:
            json.dump(results_data, f, indent=4)
            
        print("[*] Analysis complete.")
    except Exception as e:
        print(f"[!] Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return

    # 3. Generate report using the same engine as the web dashboard
    print("[*] Phase 3: Generating HTML report...")
    report_name = f"reporte_{timestamp}.html"
    report_output = REPORTS_DIR / report_name

    try:
        success = generate_report_like_web(results_data, report_output)
        if not success:
            print("[!] Report generation failed (template error).")
            return

        # 4. Update dashboard active state
        print("[*] Updating dashboard active state...")

        # Update current_dump.json metadata from engine results
        metadata = results_data.get("metadata", {})
        state = {
            "active_memory_dump": str(dump_path),
            "filename": dump_filename,
            "status": "analysis_completed",
            "last_results": str(DATA_DIR / "results.json"),
            "timestamp": timestamp,
            "size_bytes": metadata.get("dump_size_bytes", 0),
            "size_human": f"{metadata.get('dump_size_bytes', 0) // (1024 * 1024)} MB",
            "hash": metadata.get("hashes", {}).get("sha256", "N/A"),
            "detected_os": metadata.get("detected_os", "Unknown"),
            "source": "startup_automated"
        }
        with open(DATA_DIR / "current_dump.json", 'w') as f:
            json.dump(state, f, indent=4)

        # Copy to data/ so it's accessible as file:// and via /download/report
        shutil.copy2(results_path, DATA_DIR / "results.json")
        shutil.copy2(report_output, DATA_DIR / "report.html")

        # Fix ownership and permissions
        stat_info = os.stat(BASE_DIR)
        uid, gid = stat_info.st_uid, stat_info.st_gid

        for f in [dump_path, results_path, report_output,
                  DATA_DIR / "results.json", DATA_DIR / "report.html",
                  DATA_DIR / "current_dump.json"]:
            if os.path.exists(f):
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
