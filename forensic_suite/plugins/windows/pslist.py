import psutil
from forensic_suite.plugins.base_plugin import BasePlugin

class WindowsPsListPlugin(BasePlugin):
    @property
    def name(self) -> str:
        return "windows.pslist"
        
    def run(self, dump_path: str) -> dict:
        ps_list = []
        count = 0
        for proc in psutil.process_iter(['pid', 'name', 'ppid']):
            try:
                ps_list.append({
                    "pid": proc.info['pid'],
                    "name": proc.info['name'],
                    "ppid": proc.info['ppid']
                })
                count += 1
                if count >= 50: break # Limit output like before
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
                
        return {
            "status": "success",
            "processes": ps_list
        }
