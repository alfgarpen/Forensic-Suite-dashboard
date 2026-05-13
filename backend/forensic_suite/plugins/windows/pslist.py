import os
import logging
from forensic_suite.plugins.base_plugin import BasePlugin
from forensic_suite.utils.volatility_runner import VolatilityRunner

logger = logging.getLogger(__name__)

class WindowsPsListPlugin(BasePlugin):
    @property
    def name(self) -> str:
        return "windows.pslist"
        
    def run(self, dump_path: str) -> dict:
        logger.info(f"Running real Volatility 3 pslist on {dump_path}")
        
        result = VolatilityRunner.run_plugin(dump_path, "windows.pslist.PsList")
        
        if result["status"] == "error":
            return {"status": "error", "error": result["error"]}
            
        # Parse Volatility 3 JSON format
        # Volatility 3 JSON is usually a list of dicts with keys like 'PID', 'PPID', 'ImageFileName'
        ps_list = []
        try:
            for entry in result["data"]:
                ps_list.append({
                    "pid": entry.get("PID", entry.get("Pid", "N/A")),
                    "name": entry.get("ImageFileName", entry.get("Name", "Unknown")),
                    "ppid": entry.get("PPID", entry.get("PPid", "N/A")),
                    "offset": hex(entry.get("Offset", 0)) if "Offset" in entry else "N/A"
                })
        except Exception as e:
            logger.error(f"Error parsing Volatility output: {e}")
            return {"status": "error", "error": f"Parsing error: {str(e)}"}
            
        return {
            "status": "success",
            "processes": ps_list,
            "count": len(ps_list)
        }
