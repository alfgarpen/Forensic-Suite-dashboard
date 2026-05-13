import os
from forensic_suite.plugins.base_plugin import BasePlugin

class LinuxPsListPlugin(BasePlugin):
    @property
    def name(self) -> str:
        return "linux.pslist"
        
    def run(self, dump_path: str) -> dict:
        # Static mock forensic data for Linux
        # In a real scenario, this would call 'vol.py -f dump_path linux.pslist'
        ps_list = [
            {"pid": 1, "name": "systemd", "ppid": 0, "user": "root", "status": "sleeping"},
            {"pid": 2, "name": "kthreadd", "ppid": 0, "user": "root", "status": "sleeping"},
            {"pid": 12, "name": "ksoftirqd/0", "ppid": 2, "user": "root", "status": "sleeping"},
            {"pid": 450, "name": "systemd-journal", "ppid": 1, "user": "root", "status": "running"},
            {"pid": 600, "name": "sshd", "ppid": 1, "user": "root", "status": "listening"},
            {"pid": 1200, "name": "bash", "ppid": 600, "user": "analyst", "status": "running"},
            {"pid": 1250, "name": "python3", "ppid": 1200, "user": "analyst", "status": "running"},
            {"pid": 1337, "name": "nc", "ppid": 1, "user": "www-data", "status": "running"}, # Forensic indicator
        ]
        
        return {
            "status": "success",
            "message": f"Simulated analysis of {os.path.basename(dump_path)}",
            "processes": ps_list
        }
