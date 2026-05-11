# volatility_manager.py

import subprocess
import json
import logging
import os
import sys
import threading
from typing import Callable, Optional, List

logger = logging.getLogger(__name__)

class VolatilityManager:
    def __init__(self, vol_path: Optional[str] = None):
        self.vol_path = vol_path or self._detect_volatility()
        self.is_installed = self.vol_path is not None
        if self.is_installed:
            logger.info(f"Volatility 3 detected at: {self.vol_path}")
        else:
            logger.warning("Volatility 3 NOT detected. Falling back to native commands.")

    def _detect_volatility(self) -> Optional[str]:
        """Attempts to find the Volatility 3 executable or module."""
        # 1. Check if 'vol.py' exists in current or parent dirs
        for path in [".", "..", "Volatility3", "../Volatility3"]:
            vol_py = os.path.join(path, "vol.py")
            if os.path.exists(vol_py):
                return f"{sys.executable} {vol_py}"

        # 2. Check if it's installed as a module
        try:
            import volatility3
            return f"{sys.executable} -m volatility3.cli"
        except ImportError:
            pass

        # 3. Check if 'vol' or 'volatility' is in PATH
        for cmd in ["vol", "volatility", "volatility3"]:
            try:
                subprocess.run([cmd, "--version"], capture_output=True, check=True)
                return cmd
            except (subprocess.CalledProcessError, FileNotFoundError):
                continue

        return None

    def execute_plugin(self, 
                       dump_path: str, 
                       plugin_name: str, 
                       args: List[str] = None, 
                       log_callback: Optional[Callable[[str], None]] = None) -> dict:
        """
        Executes a Volatility 3 plugin and returns the JSON result.
        Captures logs in real-time via log_callback.
        """
        if not self.is_installed:
            return {"status": "error", "error": "Volatility 3 not installed."}

        if args is None:
            args = []

        # Build command: vol -f dump -r json plugin_name
        base_cmd = self.vol_path.split()
        full_cmd = base_cmd + ["-f", dump_path, "-r", "json", plugin_name] + args

        if log_callback:
            log_callback(f"[+] Starting execution: {' '.join(full_cmd)}")

        try:
            process = subprocess.Popen(
                full_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )

            stdout_data = []
            stderr_data = []

            # We need to handle output carefully because Volatility might output non-JSON logs to stdout/stderr
            def read_stream(stream, container, is_error=False):
                for line in stream:
                    line = line.strip()
                    if line:
                        container.append(line)
                        if log_callback:
                            prefix = "[-] " if is_error else "[*] "
                            log_callback(f"{prefix}{line}")

            stdout_thread = threading.Thread(target=read_stream, args=(process.stdout, stdout_data))
            stderr_thread = threading.Thread(target=read_stream, args=(process.stderr, stderr_data, True))

            stdout_thread.start()
            stderr_thread.start()

            # Wait for completion with timeout
            process.wait(timeout=600) # 10 minutes timeout
            stdout_thread.join()
            stderr_thread.join()

            if process.returncode != 0:
                error_msg = "\n".join(stderr_data) or "Unknown Volatility error"
                return {"status": "error", "error": error_msg}

            # Parse JSON from stdout
            full_stdout = "".join(stdout_data)
            try:
                # Volatility 3 sometimes has logs BEFORE the JSON array
                start_idx = full_stdout.find('[')
                if start_idx != -1:
                    json_data = json.loads(full_stdout[start_idx:])
                    return {"status": "success", "data": json_data}
                else:
                    return {"status": "error", "error": "No JSON output found."}
            except json.JSONDecodeError as e:
                return {"status": "error", "error": f"JSON parse error: {str(e)}"}

        except subprocess.TimeoutExpired:
            process.kill()
            return {"status": "error", "error": "Analysis timed out (600s)."}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def get_version(self) -> str:
        if not self.is_installed:
            return "Not installed"
        try:
            cmd = self.vol_path.split() + ["--version"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.stdout.strip()
        except:
            return "Unknown version"
