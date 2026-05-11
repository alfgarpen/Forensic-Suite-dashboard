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
        
        # 1. Basic Metadata
        detected_os = detect_os_from_dump(self.dump_path)
        self.log_callback(f"[+] Initial OS detection: {detected_os}")
        
        # 2. Refine OS Detection if unknown using Volatility
        if detected_os == "unknown" and self.vol_manager.is_installed:
            self.log_callback("[*] Attempting advanced OS detection via Volatility banners...")
            # Try windows.info or linux.banner
            for probe in ["windows.info", "linux.banner"]:
                res = self.vol_manager.execute_plugin(self.dump_path, probe)
                if res["status"] == "success":
                    detected_os = "windows" if "windows" in probe else "linux"
                    self.log_callback(f"[+] Advanced detection confirmed: {detected_os}")
                    break
        
        # 3. Final Fallback: use local system info if still unknown
        if detected_os == "unknown":
            from forensic_suite.utils.os_detector import get_local_os
            self.log_callback("[*] Volatility could not detect OS. Falling back to local system info...")
            detected_os = get_local_os()
            self.log_callback(f"[+] Fallback detection (Local OS): {detected_os}")
        
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
                "volatility_version": self.vol_manager.get_version()
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
            
            if res["status"] == "success":
                parsed = ArtifactParser.parse(p_name, res["data"])
                results["artifacts"][p_name] = parsed
                self.log_callback(f"[+] {p_name} completed successfully. Artifacts found: {parsed.get('count', 'N/A')}")
            else:
                self.log_callback(f"[-] {p_name} failed: {res.get('error')}")
                
                # 6. Fallback
                fallback_cat = CommandFallback.map_plugin_to_category(p_name)
                if fallback_cat:
                    self.log_callback(f"[*] Attempting native fallback for {fallback_cat}...")
                    f_res = CommandFallback.run_fallback(fallback_cat)
                    if f_res["status"] == "success":
                        # Parse the fallback output (it's a string)
                        parsed_fallback = ArtifactParser.parse(f"fallback.{fallback_cat}", f_res["output"])
                        results["artifacts"][f"fallback.{fallback_cat}"] = parsed_fallback
                        self.log_callback(f"[+] Fallback for {fallback_cat} successful.")
                    else:
                        self.log_callback(f"[-] Fallback failed: {f_res.get('error')}")
                
        self.log_callback("[!] Analysis completed.")
        return results
