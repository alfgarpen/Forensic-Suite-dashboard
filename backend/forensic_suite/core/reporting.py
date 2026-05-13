import os
import logging
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

logger = logging.getLogger(__name__)

class Reporting:
    def __init__(self, templates_dir: str = 'templates'):
        self.templates_dir = templates_dir
        
    def generate_html_report(self, results_data: dict, output_path: str) -> bool:
        """
        Generates an HTML report from analysis results using the original Jinja2 template.
        Includes an executive summary mapping the threats and severity.
        """
        logger.info(f"Generating report at {output_path}...")
        try:
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            
            env = Environment(loader=FileSystemLoader(self.templates_dir))
            template = env.get_template('report_template.html')

            alerts = results_data.get("threats", {}).get("alerts", [])
            severity = results_data.get("threats", {}).get("severity", "low")
            
            # Use 'artifacts' instead of 'plugins'
            artifacts_dict = results_data.get("artifacts", results_data.get("plugins", {}))
            plugins_run = list(artifacts_dict.keys())
            
            # Handle metadata
            metadata = results_data.get("metadata", {})
            detected_os = metadata.get("detected_os", "Unknown")
            vol_ver = metadata.get("volatility_version", "N/A")
            os_profile = f"{detected_os} (via Volatility {vol_ver})"
            
            findings = {}
            for p_name, p_data in artifacts_dict.items():
                if p_data.get("status") == "success":
                    if "items" in p_data:
                        findings[p_name] = p_data["items"]
                    elif "data" in p_data:
                        findings[p_name] = p_data["data"]
                    elif "output" in p_data: # Fallback output
                        findings[p_name] = {"Raw Output": p_data["output"]}
                    else:
                        findings[p_name] = {k: v for k, v in p_data.items() if k != "status"}
                else:
                    findings[p_name] = {"Error": p_data.get("error", "Failed")}

            dump_path = metadata.get("dump_path", "memory.raw")
            dump_filename = os.path.basename(dump_path)
            dump_hashes = metadata.get("hashes", {"md5": "N/A", "sha256": "N/A"})
            dump_size = metadata.get("dump_size_bytes", 0)

            html_content = template.render(
                dump_file=dump_filename,
                dump_hashes=dump_hashes,
                dump_size=dump_size,
                os_profile=os_profile.strip(),
                plugins_run=plugins_run,
                findings=findings,
                alerts=alerts,
                severity=severity,
                generation_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
                
            return True
        except Exception as e:
            logger.error(f"Failed to generate report: {e}")
            return False
