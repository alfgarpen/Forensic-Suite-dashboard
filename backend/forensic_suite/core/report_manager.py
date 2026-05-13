import os
from typing import Optional
from forensic_suite.core.reporting import Reporting
from forensic_suite.utils.file_utils import FileUtils

class ReportManager:
    def __init__(self, data_dir: str, templates_dir: str = 'templates'):
        self.data_dir = data_dir
        self.templates_dir = templates_dir
        self.reporter = Reporting(templates_dir)

    def generate(self, results_path: Optional[str] = None) -> dict:
        """
        Generates a report using results and active evidence metadata.
        """
        active_evidence = FileUtils.get_active_dump(self.data_dir)
        
        if not results_path:
            results_path = active_evidence.get('last_results', os.path.join(self.data_dir, 'results.json'))

        if not os.path.exists(results_path):
            return {"status": "error", "message": "Results not found. Run analysis first."}

        results_data = FileUtils.read_json(results_path)
        
        # Ensure metadata is updated with latest evidence info if available
        if active_evidence:
            results_data['metadata'].update({
                "dump_path": active_evidence.get('active_memory_dump'),
                "dump_hash_sha256": active_evidence.get('hash'),
                "acquisition_source": active_evidence.get('source'),
                "acquisition_time": active_evidence.get('timestamp')
            })

        output_html = os.path.join(self.data_dir, 'report.html')
        
        if self.reporter.generate_html_report(results_data, output_html):
            return {
                "status": "success", 
                "message": "Report generated.", 
                "report_url": "/download/report",
                "output_path": output_html
            }
        
        return {"status": "error", "message": "Failed to generate report."}
