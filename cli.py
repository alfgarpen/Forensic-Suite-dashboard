import click
import os
import sys
import json

# Add current directory to path so we can import scripts
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scripts.memory_acquisition import MemoryAcquisition
from scripts.analyze_dump import DumpAnalyzer, get_available_plugins
from scripts.generate_report import ReportGenerator

@click.group()
def cli():
    """Forensic Scripts Suite - Command Line Interface"""
    pass

@cli.command()
@click.option('--output', '-o', default='data/memory.raw', help='Path to output the memory dump.')
@click.option('--algo', '-a', default='md5', help='Hashing algorithm (md5, sha1, sha256).')
def acquire(output, algo):
    """Acquire system RAM and generate cryptographic hash."""
    click.echo("[*] Starting memory acquisition...")
    acq = MemoryAcquisition()
    os.makedirs(os.path.dirname(os.path.abspath(output)), exist_ok=True)
    out = acq.acquire(output)
    if out:
        acq.verify_hash(out, algo)
        click.echo(f"[+] Acquisition complete. Output saved to {out}")

@cli.command()
@click.option('--dump', '-d', default='data/memory.raw', help='Path to the raw memory dump.')
@click.option('--plugins', '-p', multiple=True, help='Volatility plugins to run.')
@click.option('--output', '-o', default='data/results.json', help='Path to save JSON results.')
@click.option('--list-plugins', is_flag=True, help='List available plugins.')
def analyze(dump, plugins, output, list_plugins):
    """Analyze a memory dump using Volatility plugins."""
    if list_plugins:
        click.echo("[*] Available plugins:")
        for p in get_available_plugins():
            click.echo(f"  - {p['id']}: {p['description']}")
        return

    if not plugins:
        plugins = ['windows.info.Info', 'windows.pslist.PsList', 'windows.netscan.NetScan']

    click.echo(f"[*] Analyzing dump {dump} with plugins: {', '.join(plugins)}")
    if not os.path.exists(dump):
        click.echo(f"[-] Error: Dump file {dump} not found. Run 'acquire' first.")
        return

    analyzer = DumpAnalyzer(dump)
    analyzer.detect_os()
    res = analyzer.run_plugins(plugins)
    
    os.makedirs(os.path.dirname(os.path.abspath(output)), exist_ok=True)
    with open(output, 'w') as f:
        json.dump(res, f, indent=4)
        
    click.echo(f"[+] Analysis complete. Results saved to {output}")

@cli.command()
@click.option('--results', '-r', default='data/results.json', help='Path to analysis results JSON.')
@click.option('--output', '-o', default='data/report.html', help='Path to output HTML report.')
def report(results, output):
    """Generate an HTML report from analysis results."""
    click.echo(f"[*] Generating report from {results}...")
    templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    generator = ReportGenerator(templates_dir)
    
    os.makedirs(os.path.dirname(os.path.abspath(output)), exist_ok=True)
    if generator.generate(results, output):
        click.echo(f"[+] Report generated successfully: {output}")
    else:
        click.echo("[-] Failed to generate report.")

@cli.command()
@click.option('--output-dir', '-d', default='data', help='Directory to store pipeline artifacts.')
def pipeline(output_dir):
    """Run the full forensic pipeline automatically (Acquire -> Analyze -> Report)."""
    click.echo("=== Starting Full Forensic Pipeline ===")
    os.makedirs(output_dir, exist_ok=True)
    
    dump_path = os.path.join(output_dir, 'memory.raw')
    results_path = os.path.join(output_dir, 'results.json')
    report_path = os.path.join(output_dir, 'report.html')
    
    # Phase 1: Acquire
    click.echo("\n--- Phase 1: Acquisition ---")
    acq = MemoryAcquisition()
    out = acq.acquire(dump_path)
    if not out:
        click.echo("[-] Acquisition failed. Aborting pipeline.")
        return
    acq.verify_hash(out)
    
    # Phase 2: Analyze
    click.echo("\n--- Phase 2: Analysis ---")
    plugins = ['windows.info.Info', 'windows.pslist.PsList', 'windows.netscan.NetScan']
    analyzer = DumpAnalyzer(out)
    analyzer.detect_os()
    res = analyzer.run_plugins(plugins)
    
    with open(results_path, 'w') as f:
        json.dump(res, f, indent=4)
    click.echo(f"[+] Analysis results saved to {results_path}")
    
    # Phase 3: Report
    click.echo("\n--- Phase 3: Reporting ---")
    templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    generator = ReportGenerator(templates_dir)
    if generator.generate(results_path, report_path):
        click.echo(f"[+] Full pipeline complete. Final report is at: {report_path}")

if __name__ == '__main__':
    cli()
