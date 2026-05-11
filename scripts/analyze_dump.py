import click
import json
import os
import time
import platform
import psutil
from datetime import datetime

def get_available_plugins():
    return [
        {"id": "windows.info.Info", "name": "System Info", "description": "Shows OS & hardware details."},
        {"id": "windows.pslist.PsList", "name": "Process List", "description": "List running processes."},
        {"id": "windows.netscan.NetScan", "name": "Network Scan", "description": "List active network connections."},
        {"id": "windows.cmdline.CmdLine", "name": "Command Line", "description": "Show command line arguments for processes."},
        {"id": "windows.malfind.Malfind", "name": "Malfind", "description": "Find hidden and injected code."}
    ]

class DumpAnalyzer:
    def __init__(self, dump_path):
        self.dump_path = dump_path
        self.os_detected = "Unknown"

    def detect_os(self):
        time.sleep(0.5)
        # Fetch actual OS info
        try:
            os_name = platform.system()
            release = platform.release()
            machine = platform.machine()
            # Try to get Windows 11 specifically if applicable
            if os_name == "Windows" and int(platform.version().split('.')[2]) >= 22000:
                release = "11"
            self.os_detected = f"{os_name} {release} {machine}"
        except Exception:
            self.os_detected = "Windows 11 x64"
        click.echo(f"Detected OS Profile: {self.os_detected}")
        return self.os_detected

    def run_plugins(self, plugins):
        results = {
            "dump_file": os.path.basename(self.dump_path),
            "os_profile": self.os_detected,
            "plugins_run": plugins,
            "findings": {}
        }
        
        for plugin in plugins:
            click.echo(f"Running plugin: {plugin}...")
            time.sleep(0.5) # Simulate real analysis time
            
            if "info" in plugin:
                results["findings"][plugin] = {
                    "Kernel Base": "0xf807abcdef123456 (Simulado)",
                    "DTB": "0x1aa000 (Simulado)",
                    "SystemTime": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
                }
            elif "pslist" in plugin:
                ps_list = []
                count = 0
                for proc in psutil.process_iter(['pid', 'name', 'ppid']):
                    try:
                        ps_list.append({
                            "PID": proc.info['pid'],
                            "Name": proc.info['name'],
                            "Parent": proc.info['ppid']
                        })
                        count += 1
                        if count >= 30: break # Limit output length for the report
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                results["findings"][plugin] = ps_list
                
            elif "netscan" in plugin:
                net_list = []
                count = 0
                try:
                    for conn in psutil.net_connections(kind='inet'):
                        laddr = f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else ""
                        raddr = f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "0.0.0.0:0"
                        net_list.append({
                            "Proto": "TCP" if conn.type == 1 else "UDP",
                            "Local": laddr,
                            "Remote": raddr,
                            "State": conn.status,
                            "PID": conn.pid if conn.pid else "Unknown"
                        })
                        count += 1
                        if count >= 20: break
                except psutil.AccessDenied:
                    net_list.append({"Error": "Requiere permisos de administrador para leer conexiones de red activas completas."})
                
                results["findings"][plugin] = net_list
            else:
                results["findings"][plugin] = {"Message": "No specific data for this plugin yet."}
                
        return results

@click.command()
@click.option('--dump', '-d', help='Path to the raw memory dump (optional if active evidence exists).')
@click.option('--plugins', '-p', multiple=True, default=['windows.info.Info', 'windows.pslist.PsList'], help='Volatility plugins to run.')
@click.option('--output', '-o', default='data/results.json', help='Path to save results.')
def main(dump, plugins, output):
    """Analyzes a memory dump using Volatility plugins (mocked)."""
    click.echo(f"--- Digital Forensics: Dump Analysis ---")
    
    data_dir = 'data'
    state_file = os.path.join(data_dir, 'current_dump.json')
    
    if not dump:
        if os.path.exists(state_file):
            with open(state_file, 'r') as f:
                state = json.load(f)
                dump = state.get('active_memory_dump')
                click.echo(f"Using active evidence: {dump}")
        
    if not dump or not os.path.exists(dump):
        click.echo(f"Error: No memory dump specified and no active evidence found.")
        return
        
    analyzer = DumpAnalyzer(dump)
    analyzer.detect_os()
    res = analyzer.run_plugins(plugins)
    
    # Add source reference
    res["source_dump"] = dump
    
    os.makedirs(os.path.dirname(os.path.abspath(output)), exist_ok=True)
    with open(output, 'w') as f:
        json.dump(res, f, indent=4)
        
    # Update state if it exists
    if os.path.exists(state_file):
        with open(state_file, 'r') as f:
            state = json.load(f)
        state['last_results'] = output
        state['status'] = 'analysis_completed'
        with open(state_file, 'w') as f:
            json.dump(state, f, indent=4)
        
    click.echo(f"Analysis complete. Results saved to {output}")

if __name__ == '__main__':
    main()
