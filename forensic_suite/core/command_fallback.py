# command_fallback.py

import subprocess
import os
import sys
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class CommandFallback:
    @staticmethod
    def run_fallback(category: str) -> dict:
        """
        Executes native system commands based on the requested category.
        """
        is_windows = sys.platform == "win32"
        
        commands = {
            "processes": ["tasklist"] if is_windows else ["ps", "aux"],
            "network": ["netstat", "-ano"] if is_windows else ["netstat", "-tulpn"],
            "system": ["systeminfo"] if is_windows else ["uname", "-a"],
            "services": ["sc", "query"] if is_windows else ["systemctl", "list-units", "--type=service"],
            "users": ["net", "user"] if is_windows else ["who"]
        }
        
        cmd = commands.get(category.lower())
        if not cmd:
            return {"status": "error", "error": f"No fallback command for category: {category}"}
            
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                return {
                    "status": "success",
                    "source": "native_command",
                    "command": " ".join(cmd),
                    "output": result.stdout
                }
            else:
                return {"status": "error", "error": result.stderr}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    @staticmethod
    def map_plugin_to_category(plugin_name: str) -> Optional[str]:
        """Maps a Volatility plugin name to a fallback category."""
        if "pslist" in plugin_name or "pstree" in plugin_name:
            return "processes"
        elif "netscan" in plugin_name or "netstat" in plugin_name:
            return "network"
        elif "info" in plugin_name:
            return "system"
        elif "services" in plugin_name:
            return "services"
        return None
