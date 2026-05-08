import logging
from datetime import datetime
from forensic_suite.services.volatility_service import VolatilityService
from forensic_suite.services.yara_service import YaraService
from forensic_suite.detection.threat_detector import ThreatDetector
from forensic_suite.utils.file_utils import FileUtils
from forensic_suite.services.hash_service import HashService
from forensic_suite.utils.os_detector import detect_os_from_dump
import os

logger = logging.getLogger(__name__)

class AnalysisEngine:
    def __init__(self, dump_path: str):
        self.dump_path = dump_path
        self.vol_service = VolatilityService()
        self.yara_service = YaraService()
        self.threat_detector = ThreatDetector()
        
    def run_analysis(self, plugins: list = None, run_yara: bool = True) -> dict:
        """
        Executes requested plugins and YARA rules.
        """
        # Calculate file stats for the report
        file_size = os.path.getsize(self.dump_path) if os.path.exists(self.dump_path) else 0
        md5 = HashService.calculate_hash(self.dump_path, 'md5') if os.path.exists(self.dump_path) else None
        sha256 = HashService.calculate_hash(self.dump_path, 'sha256') if os.path.exists(self.dump_path) else None
        detected_os = detect_os_from_dump(self.dump_path)

        results = {
            "metadata": {
                "dump_path": self.dump_path,
                "dump_filename": os.path.basename(self.dump_path),
                "dump_size_bytes": file_size,
                "detected_os": detected_os,
                "hashes": {
                    "md5": md5['hash'] if md5 else "N/A",
                    "sha256": sha256['hash'] if sha256 else "N/A"
                },
                "analysis_time": datetime.now().isoformat()
            },
            "system_info": {},
            "plugins": {},
            "yara": {},
            "correlations": {},
            "threats": {}
        }
        
        if plugins is None:
            all_plugins = self.vol_service.get_available_plugins()
            if detected_os != "unknown":
                # Filter plugins to match detected OS (e.g. windows.pslist)
                plugins = [p for p in all_plugins if p.startswith(detected_os)]
                if not plugins: # Fallback if no specific plugins found
                    plugins = all_plugins
            else:
                plugins = all_plugins
            
        logger.info(f"Running Analysis on {self.dump_path} (OS: {detected_os}) with plugins: {plugins}")

        # Extract system info if available
        # Prioritize info plugin that matches detected OS
        info_order = []
        if detected_os == "windows":
            info_order = ["windows.info", "linux.info"]
        elif detected_os == "linux":
            info_order = ["linux.info", "windows.info"]
        else:
            info_order = ["windows.info", "linux.info"]

        for info_plugin_name in info_order:
            info_plugin = self.vol_service.get_plugin(info_plugin_name)
            if info_plugin and (info_plugin_name in plugins):
                results["system_info"] = info_plugin.run(self.dump_path)
                break
            
        # Run specific plugins
        for p_name in plugins:
            plugin = self.vol_service.get_plugin(p_name)
            if plugin:
                try:
                    results["plugins"][p_name] = plugin.run(self.dump_path)
                except Exception as e:
                    logger.error(f"Plugin {p_name} failed: {e}")
                    results["plugins"][p_name] = {"error": str(e)}
            else:
                results["plugins"][p_name] = {"error": "Plugin not found"}

        # Run YARA
        if run_yara:
            results["yara"] = self.yara_service.scan_dump(self.dump_path)
            
        # Correlate findings
        results["correlations"] = self.correlate(results["plugins"])
        
        # Detect Threats
        results["threats"] = self.threat_detector.analyze(results)
        
        return results

    def correlate(self, plugins_results: dict) -> dict:
        """
        Correlates processes and connections.
        """
        correlations = {}
        
        # Try Windows then Linux
        pslist_res = plugins_results.get("windows.pslist", plugins_results.get("linux.pslist", {}))
        netscan_res = plugins_results.get("windows.netscan", plugins_results.get("linux.netstat", {}))
        
        active_pids = set()
        if pslist_res.get("status") == "success":
            for proc in pslist_res.get("processes", []):
                active_pids.add(proc.get("pid"))
                
        if netscan_res.get("status") == "success":
            missing_process_for_conn = []
            for conn in netscan_res.get("connections", []):
                pid = conn.get("pid")
                if pid and pid not in active_pids and pid != 0:
                    missing_process_for_conn.append(conn)
                    
            if missing_process_for_conn:
                correlations["connections_missing_process"] = missing_process_for_conn
                
        return correlations
