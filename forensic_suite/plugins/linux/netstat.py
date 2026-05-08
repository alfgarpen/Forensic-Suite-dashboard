import psutil
from forensic_suite.plugins.base_plugin import BasePlugin

class LinuxNetStatPlugin(BasePlugin):
    @property
    def name(self) -> str:
        return "linux.netstat"
        
    def run(self, dump_path: str) -> dict:
        net_list = []
        count = 0
        try:
            for conn in psutil.net_connections(kind='inet'):
                laddr = f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else ""
                raddr = f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "0.0.0.0:0"
                net_list.append({
                    "protocol": "TCP" if conn.type == 1 else "UDP",
                    "local_addr": laddr,
                    "foreign_addr": raddr,
                    "state": conn.status,
                    "pid": conn.pid if conn.pid else 0
                })
                count += 1
                if count >= 20: break
        except psutil.AccessDenied:
            net_list.append({"Error": "Requires root permissions to read all connections."})
            
        return {
            "status": "success",
            "connections": net_list
        }
