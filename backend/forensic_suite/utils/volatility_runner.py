import subprocess
import json
import logging
import os
import sys

logger = logging.getLogger(__name__)

class VolatilityRunner:
    @staticmethod
    def run_plugin(dump_path: str, plugin_name: str, options: list = None) -> dict:
        """
        Runs a Volatility 3 plugin via subprocess and returns the parsed JSON output.
        """
        if options is None:
            options = []
            
        # Use python -m volatility3.cli to ensure it's using the correct environment
        cmd = [sys.executable, "-m", "volatility3.cli", "-f", dump_path, "-r", "json", plugin_name] + options
        
        logger.info(f"Executing Volatility 3: {' '.join(cmd)}")
        
        try:
            # We use a longer timeout for Volatility
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            
            if result.returncode != 0:
                logger.error(f"Volatility 3 failed with return code {result.returncode}")
                logger.error(f"Stderr: {result.stderr}")
                return {"status": "error", "error": result.stderr or "Unknown error"}
                
            try:
                data = json.loads(result.stdout)
                return {"status": "success", "data": data}
            except json.JSONDecodeError:
                # Sometimes Volatility outputs headers before JSON or mixed content
                # Try to find the JSON part
                start = result.stdout.find('[')
                if start != -1:
                    try:
                        data = json.loads(result.stdout[start:])
                        return {"status": "success", "data": data}
                    except:
                        pass
                return {"status": "error", "error": "Failed to parse Volatility JSON output"}
                
        except subprocess.TimeoutExpired:
            logger.error("Volatility 3 analysis timed out")
            return {"status": "error", "error": "Analysis timed out"}
        except Exception as e:
            logger.error(f"Exception running Volatility 3: {e}")
            return {"status": "error", "error": str(e)}
