import logging
from forensic_suite.services.volatility_service import VolatilityService
from forensic_suite.services.yara_service import YaraService
from forensic_suite.detection.threat_detector import ThreatDetector
from forensic_suite.utils.file_utils import FileUtils

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
        results = {
            "system_info": {},
            "plugins": {},
            "yara": {},
            "correlations": {},
            "threats": {}
        }
        
        if plugins is None:
            plugins = self.vol_service.get_available_plugins()
            
        logger.info(f"Running Analysis on {self.dump_path} with plugins: {plugins}")

        # Extract system info if available
        info_plugin = self.vol_service.get_plugin("windows.info")
        if info_plugin and ("windows.info" in plugins):
            results["system_info"] = info_plugin.run(self.dump_path)
            
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
        
        pslist_res = plugins_results.get("windows.pslist", {})
        netscan_res = plugins_results.get("windows.netscan", {})
        
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
