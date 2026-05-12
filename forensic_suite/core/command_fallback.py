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
            "network": ["netstat", "-ano"] if is_windows else ["ss", "-atunp"],
            "system": ["systeminfo"] if is_windows else ["uname", "-a"],
            "services": ["sc", "query"] if is_windows else ["systemctl", "list-units", "--type=service"],
            "users": ["net", "user"] if is_windows else ["who"],
            "history": [] if is_windows else ["cat", os.path.expanduser("~/.bash_history")],
            "kernel": ["driverquery"] if is_windows else ["lsmod"]
        }
        
        # Special handling for Linux bash/zsh history to find more users
        if category.lower() == "history" and not is_windows:
            import glob
            history_files = []
            for pattern in ["/home/*/.bash_history", "/home/*/.zsh_history"]:
                history_files.extend(glob.glob(pattern))
            
            # Add root history
            for f in ["/root/.bash_history", "/root/.zsh_history"]:
                if os.path.exists(f):
                    history_files.append(f)
            
            # Add current user's history if not already there
            home = os.path.expanduser("~")
            for f in [os.path.join(home, ".bash_history"), os.path.join(home, ".zsh_history")]:
                if os.path.exists(f) and f not in history_files:
                    history_files.append(f)
            
            valid_files = [f for f in history_files if os.path.exists(f) and os.access(f, os.R_OK)]
            if valid_files:
                try:
                    history_data = []
                    for vf in valid_files:
                        with open(vf, 'r', errors='replace') as f:
                            for line in f:
                                line = line.strip()
                                if not line: continue
                                
                                cmd = line
                                ts = "N/A"
                                
                                # Handle Zsh history format: : 1234567890:0;command
                                if line.startswith(":"):
                                    try:
                                        parts = line.split(";", 1)
                                        if len(parts) > 1:
                                            meta = parts[0][1:].strip() # remove ":" and strip
                                            meta_parts = meta.split(":")
                                            if meta_parts:
                                                from datetime import datetime
                                                ts_unix = int(meta_parts[0])
                                                ts = datetime.fromtimestamp(ts_unix).strftime('%Y-%m-%d %H:%M:%S')
                                            cmd = parts[1]
                                    except:
                                        pass # Fallback to raw line
                                
                                history_data.append({
                                    "Source": os.path.basename(vf),
                                    "Timestamp": ts,
                                    "Command": cmd
                                })
                    
                    return {
                        "status": "success",
                        "source": "native_command",
                        "command": "cat " + " ".join(valid_files),
                        "data": history_data
                    }
                except Exception as e:
                    logger.warning(f"Failed to parse history files: {e}")

        cmd = commands.get(category.lower())
        if not cmd:
            return {"status": "error", "error": f"No fallback command for category: {category}"}
            
        try:
            # Special handling for empty commands (like history on Windows)
            if not cmd:
                return {"status": "error", "error": f"Category {category} not supported on this platform."}

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
        p = plugin_name.lower()
        if any(x in p for x in ["pslist", "pstree", "psaux"]):
            return "processes"
        elif any(x in p for x in ["netscan", "netstat", "sockstat"]):
            return "network"
        elif any(x in p for x in ["info", "banners"]):
            return "system"
        elif "services" in p:
            return "services"
        elif "bash" in p:
            return "history"
        elif "lsmod" in p or "check_modules" in p:
            return "kernel"
        elif any(x in p for x in ["users", "whoami"]):
            return "users"
        return None
