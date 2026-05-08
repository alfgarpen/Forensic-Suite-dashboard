import os
import logging
import datetime
import os
from forensic_suite.plugins.base_plugin import BasePlugin
from forensic_suite.utils.volatility_runner import VolatilityRunner

logger = logging.getLogger(__name__)

class WindowsInfoPlugin(BasePlugin):
    @property
    def name(self) -> str:
        return "windows.info"
        
    def run(self, dump_path: str) -> dict:
        logger.info(f"Running real Volatility 3 info on {dump_path}")
        
        result = VolatilityRunner.run_plugin(dump_path, "windows.info.Info")
        
        if result["status"] == "error":
             return {"status": "error", "error": result["error"]}

        # Parse Volatility 3 JSON format
        info_data = {}
        try:
            for entry in result["data"]:
                var = entry.get("Variable", "Unknown")
                val = entry.get("Value", "Unknown")
                info_data[var] = val
        except Exception as e:
            logger.error(f"Error parsing Volatility output: {e}")

        return {
            "status": "success",
            "os_version": info_data.get("MajorOperatingSystemVersion", "Windows (Extracted)"),
            "architecture": info_data.get("Machine", "Unknown"),
            "kernel_base": info_data.get("KernelBase", "Unknown"),
            "analyzed_file": os.path.basename(dump_path),
            "raw_data": info_data,
            "system_time": datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        }
