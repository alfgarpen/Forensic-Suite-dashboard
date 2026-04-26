import platform
import datetime
from forensic_suite.plugins.base_plugin import BasePlugin

class WindowsInfoPlugin(BasePlugin):
    @property
    def name(self) -> str:
        return "windows.info"
        
    def run(self, dump_path: str) -> dict:
        try:
            os_name = platform.system()
            release = platform.release()
            machine = platform.machine()
            if os_name == "Windows" and int(platform.version().split('.')[2]) >= 22000:
                release = "11"
            os_detected = f"{os_name} {release}"
        except Exception:
            os_detected = "Unknown"
            machine = "Unknown"

        return {
            "status": "success",
            "os_version": os_detected,
            "architecture": machine,
            "system_time": datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        }
