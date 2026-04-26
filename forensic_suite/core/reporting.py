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
            
            # Map new JSON structure to original Jinja logic
            plugins_dict = results_data.get("plugins", {})
            plugins_run = list(plugins_dict.keys())
            
            os_info = results_data.get("system_info", {})
            os_profile = os_info.get("os_version", "Unknown") + " " + os_info.get("architecture", "Unknown")
            
            findings = {}
            for p_name, p_data in plugins_dict.items():
                if p_data.get("status") == "success":
                    if "processes" in p_data:
                        findings[p_name] = p_data["processes"]
                    elif "connections" in p_data:
                        findings[p_name] = p_data["connections"]
                    else:
                        findings[p_name] = {k: v for k, v in p_data.items() if k != "status"}
                else:
                    findings[p_name] = {"Error": p_data.get("error", "Failed")}

            html_content = template.render(
                dump_file="memory.raw",  # Defaulting locally since we don't store it in results directly now
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
