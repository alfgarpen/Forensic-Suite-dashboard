# analysis_engine.py

import logging
import os
from datetime import datetime
from typing import List, Optional, Callable

from forensic_suite.core.volatility_manager import VolatilityManager
from forensic_suite.core.plugin_registry import get_plugins_for_os, is_plugin_compatible
from forensic_suite.core.artifact_parser import ArtifactParser
from forensic_suite.core.command_fallback import CommandFallback
from forensic_suite.utils.os_detector import detect_os_from_dump
from forensic_suite.services.hash_service import HashService

logger = logging.getLogger(__name__)

class AnalysisEngine:
    def __init__(self, dump_path: str, log_callback: Optional[Callable[[str], None]] = None):
        self.dump_path = dump_path
        self.vol_manager = VolatilityManager()
        self.log_callback = log_callback or (lambda x: logger.info(x))
        self.artifacts_dir = os.path.join(os.path.dirname(dump_path), "artifacts")
        os.makedirs(self.artifacts_dir, exist_ok=True)

    def run_analysis(self, plugins: List[str] = None) -> dict:
        """
        Main analysis loop. Performs OS detection, executes plugins, 
        normalizes results, and handles fallback.
        """
        self.log_callback(f"[!] Starting forensic analysis for: {os.path.basename(self.dump_path)}")
        
        # 0. Basic Validation
        if os.path.exists(self.dump_path):
            file_size = os.path.getsize(self.dump_path)
            if file_size < 1024 * 1024: # Less than 1MB
                self.log_callback(f"[!] WARNING: File size is very small ({file_size / 1024:.2f} KB). "
                                   "This is likely NOT a valid memory dump.")

        # 1. Basic Metadata
        detected_os = detect_os_from_dump(self.dump_path)
        self.log_callback(f"[+] Initial OS detection: {detected_os}")
        
        # Calculate hashes for the report
        self.log_callback("[*] Calculating file hashes (MD5, SHA256)...")
        md5_res = HashService.calculate_hash(self.dump_path, 'md5')
        sha256_res = HashService.calculate_hash(self.dump_path, 'sha256')
        
        # 2. Refine OS Detection if unknown using Volatility
        if detected_os == "unknown" and self.vol_manager.is_installed:
            self.log_callback("[*] Attempting advanced OS detection via Volatility banners...")
            # Try windows.info or banners.Banners
            for probe in ["windows.info", "banners.Banners"]:
                res = self.vol_manager.execute_plugin(self.dump_path, probe)
                if res["status"] == "success" and res.get("data"):
                    detected_os = "windows" if "windows" in probe else "linux"
                    self.log_callback(f"[+] Advanced detection confirmed: {detected_os}")
                    break
        
        # 3. Final Fallback: use native system commands if still unknown
        if detected_os == "unknown":
            self.log_callback("[*] Volatility could not detect OS. Falling back to native system info...")
            detected_os = CommandFallback.detect_os_from_system_info()
            
            if detected_os == "unknown":
                # Ultimate fallback: default to host OS from sys.platform
                from forensic_suite.utils.os_detector import get_local_os
                detected_os = get_local_os()
                self.log_callback(f"[!] All detection methods failed. Using local system default: {detected_os}")
            else:
                self.log_callback(f"[+] Fallback detection (System Info): {detected_os}")
        
        # 4. Resolve Plugins to run
        if not plugins:
            # Load default plugins for detected OS
            os_data = get_plugins_for_os(detected_os)
            plugins = []
            for category in os_data.values():
                plugins.extend(category.keys())
        
        results = {
            "metadata": {
                "dump_path": self.dump_path,
                "detected_os": detected_os,
                "analysis_time": datetime.now().isoformat(),
                "volatility_version": self.vol_manager.get_version(),
                "hashes": {
                    "md5": md5_res["hash"] if md5_res else "N/A",
                    "sha256": sha256_res["hash"] if sha256_res else "N/A"
                },
                "dump_size_bytes": os.path.getsize(self.dump_path) if os.path.exists(self.dump_path) else 0
            },
            "artifacts": {}
        }

        # 5. Execute Plugins
        for p_name in plugins:
            self.log_callback(f"[+] Executing plugin: {p_name}")
            
            # Check compatibility
            if not is_plugin_compatible(p_name, detected_os):
                self.log_callback(f"[!] Warning: Plugin {p_name} might not be compatible with {detected_os}")

            # Try Volatility
            res = self.vol_manager.execute_plugin(self.dump_path, p_name, log_callback=self.log_callback)
            
            plugin_result = None
            is_success = False
            
            if res["status"] == "success":
                parsed = ArtifactParser.parse(p_name, res["data"])
                # Even if status is success, Volatility might return empty list if it failed to find anything meaningful
                if parsed.get("count", 0) > 0 or parsed.get("data"):
                    plugin_result = parsed
                    self.log_callback(f"[+] {p_name} completed successfully. Artifacts found: {parsed.get('count', 'N/A')}")
                    is_success = True
                else:
                    self.log_callback(f"[*] {p_name} returned no data.")
                    plugin_result = {"status": "success", "data": [], "count": 0, "message": "No results found by Volatility."}

            if not is_success:
                error_msg = res.get('error', 'Unknown Volatility error')
                if res["status"] != "success":
                    self.log_callback(f"[-] {p_name} failed: {error_msg}")
                
                # 6. Fallback
                fallback_cat = CommandFallback.map_plugin_to_category(p_name)
                if fallback_cat:
                    self.log_callback(f"[*] Attempting native fallback for {fallback_cat}...")
                    f_res = CommandFallback.run_fallback(fallback_cat)
                    if f_res["status"] == "success":
                        # Parse the fallback output (it can be a string or structured data)
                        fallback_input = f_res.get("data", f_res.get("output"))
                        parsed_fallback = ArtifactParser.parse(p_name, fallback_input)
                        plugin_result = parsed_fallback
                        self.log_callback(f"[+] Fallback for {fallback_cat} successful.")
                        is_success = True
                    else:
                        fallback_err = f_res.get('error', 'Unknown fallback error')
                        self.log_callback(f"[-] Fallback failed: {fallback_err}")
                        plugin_result = {"status": "error", "error": f"Volatility: {error_msg} | Fallback: {fallback_err}"}
                else:
                    plugin_result = {"status": "error", "error": error_msg}
            
            # Always store the result
            if plugin_result:
                results["artifacts"][p_name] = plugin_result
                
        self.log_callback("[!] Analysis completed.")
        return results
