import click
import os
import json
import time

from forensic_suite.core.acquisition import Acquisition
from forensic_suite.core.analysis_engine import AnalysisEngine
from forensic_suite.core.reporting import Reporting
from forensic_suite.services.volatility_service import VolatilityService
from forensic_suite.utils.file_utils import FileUtils

@click.group()
def cli():
    """Forensic Suites - Modular CLI"""
    pass

@cli.command()
@click.option('--output', '-o', default='data/memory.raw', help='Path to output the memory dump.')
@click.option('--algo', '-a', default='md5', help='Hashing algorithm (md5, sha1, sha256).')
def acquire(output, algo):
    """Acquire system RAM and generate cryptographic hash."""
    if not FileUtils.is_valid_extension(output):
        click.echo("[-] Error: Invalid file extension. Only .raw and .mem are allowed.")
        return

    click.echo("[*] Starting memory acquisition...")
    acq = Acquisition()
    out = acq.acquire_memory(output)
    if out:
        # Calculate hashes for the state
        md5 = acq.verify_dump(out, 'md5')
        sha1 = acq.verify_dump(out, 'sha1')
        sha256 = acq.verify_dump(out, 'sha256')
        
        from datetime import datetime
        dump_info = {
            "path": out,
            "uploaded_at": datetime.now().isoformat(),
            "hashes": {
                "md5": md5['hash'] if md5 else "",
                "sha1": sha1['hash'] if sha1 else "",
                "sha256": sha256['hash'] if sha256 else ""
            },
            "type": os.path.splitext(out)[1][1:].lower()
        }
        FileUtils.set_active_dump('data', dump_info)
        
        click.echo(f"[+] Acquisition complete. Output saved to {out}")
        click.echo(f"[+] Registered as active dump.")
        click.echo(f"[+] {algo.upper()}: {md5['hash'] if algo == 'md5' else (sha1['hash'] if algo == 'sha1' else sha256['hash'])}")
    else:
        click.echo("[-] Acquisition failed.")

@cli.command()
@click.option('--dump', '-d', help='Path to the raw memory dump.')
@click.option('--plugins', '-p', multiple=True, help='Plugins to run. E.g., windows.pslist')
@click.option('--output', '-o', default='data/results.json', help='Path to save JSON results.')
@click.option('--list-plugins', is_flag=True, help='List available plugins.')
def analyze(dump, plugins, output, list_plugins):
    """Analyze a memory dump using plugins and threat detection."""
    vol_service = VolatilityService()
    
    if list_plugins:
        click.echo("[*] Available plugins:")
        for p in vol_service.get_available_plugins():
            click.echo(f"  - {p}")
        return

    plugin_list = list(plugins) if plugins else None
    
    if not dump:
        active = FileUtils.get_active_dump('data')
        dump = active.get('path')
        if not dump:
             click.echo("[-] Error: No dump provided and no active dump found. Run 'acquire' or provide --dump.")
             return

    click.echo(f"[*] Analyzing dump {dump}")
    if not os.path.exists(dump):
        click.echo(f"[-] Error: Dump file {dump} not found.")
        return

    engine = AnalysisEngine(dump)
    
    # Simple progress mock
    click.echo("[*] Running Analysis Engine... ", nl=False)
    for _ in range(3):
        time.sleep(0.5)
        click.echo(".", nl=False)
    click.echo(" Done!")

    res = engine.run_analysis(plugin_list)
    
    if FileUtils.write_json(output, res):
        click.echo(f"[+] Analysis complete. Results saved to {output}")
        
        # Link results to active dump in state
        active = FileUtils.get_active_dump('data')
        if active.get('path') == dump:
            active['last_results'] = output
            FileUtils.set_active_dump('data', active)
            
        threats = res.get('threats', {})
        if threats.get('alerts'):
             click.secho(f"[!] Warning: Found {len(threats['alerts'])} alerts (Severity: {threats['severity']})", fg="red" if threats['severity'] == "high" else "yellow")
    else:
        click.echo(f"[-] Error saving results to {output}")

@cli.command()
@click.option('--results', '-r', help='Path to analysis results JSON.')
@click.option('--output', '-o', default='data/report.html', help='Path to output HTML report.')
def report(results, output):
    """Generate an HTML report."""
    if not results:
        active = FileUtils.get_active_dump('data')
        results = active.get('last_results', 'data/results.json')

    click.echo(f"[*] Generating report from {results}...")
    res_data = FileUtils.read_json(results)
    if not res_data:
        click.echo(f"[-] Error: Results file {results} not found.")
        return
        
    reporter = Reporting()
    if reporter.generate_html_report(res_data, output):
        click.echo(f"[+] Report generated successfully: {output}")
    else:
        click.echo("[-] Failed to generate report.")

@cli.command()
@click.option('--output-dir', '-d', default='data', help='Directory to store pipeline artifacts.')
@click.option('--profile', type=click.Choice(['quick', 'deep']), default='quick', help='Analysis profile')
def pipeline(output_dir, profile):
    """Run the complete pipeline: Acquire -> Analyze -> Report."""
    click.echo(f"=== Starting Full Forensic Pipeline [{profile.upper()}] ===")
    os.makedirs(output_dir, exist_ok=True)
    
    dump_path = os.path.join(output_dir, 'memory.raw')
    results_path = os.path.join(output_dir, 'results.json')
    report_path = os.path.join(output_dir, 'report.html')
    
    # 1. Acquire
    click.echo("\n--- Phase 1: Acquisition ---")
    acq = Acquisition()
    out = acq.acquire_memory(dump_path)
    if not out:
         return
    
    # 2. Analyze
    click.echo("\n--- Phase 2: Analysis Engine ---")
    engine = AnalysisEngine(dump_path)
    # Different profiles
    plugins = ['windows.info'] if profile == 'quick' else None # Deep implies all plugins
    
    # Progress bar mock
    with click.progressbar(length=100, label='Analyzing') as bar:
        for _ in range(10):
            time.sleep(0.1)
            bar.update(10)
            
    res = engine.run_analysis(plugins)
    FileUtils.write_json(results_path, res)
    click.echo(f"[+] Analysis saved to {results_path}")
    
    # 3. Report
    click.echo("\n--- Phase 3: Reporting ---")
    reporter = Reporting()
    if reporter.generate_html_report(res, report_path):
        click.echo(f"[+] Full pipeline complete. Final report is at: {report_path}")
