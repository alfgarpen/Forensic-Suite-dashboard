import os
import uuid
import threading
from typing import List, Dict, Optional
from forensic_suite.core.analysis_engine import AnalysisEngine
from forensic_suite.utils.file_utils import FileUtils

class AnalysisManager:
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.jobs = {}

    def start_analysis(self, dump_path: str, plugins: Optional[List[str]] = None) -> str:
        job_id = str(uuid.uuid4())
        self.jobs[job_id] = {"status": "pending", "dump_path": dump_path}
        
        output_json = os.path.join(self.data_dir, 'results.json')
        
        thread = threading.Thread(
            target=self._run_analysis_thread, 
            args=(job_id, dump_path, plugins, output_json)
        )
        thread.start()
        
        return job_id

    def _run_analysis_thread(self, job_id: str, dump_path: str, plugins: Optional[List[str]], output_json: str):
        self.jobs[job_id]["status"] = "running"
        try:
            engine = AnalysisEngine(dump_path)
            results = engine.run_analysis(plugins)
            FileUtils.write_json(output_json, results)
            
            # Update evidence state with last results
            active = FileUtils.get_active_dump(self.data_dir)
            if active.get('active_memory_dump') == dump_path:
                active['last_results'] = output_json
                active['status'] = 'analysis_completed'
                FileUtils.set_active_dump(self.data_dir, active)
                
            self.jobs[job_id].update({
                "status": "completed",
                "result": results,
                "output_file": output_json
            })
        except Exception as e:
            self.jobs[job_id].update({
                "status": "failed",
                "error": str(e)
            })

    def get_job_status(self, job_id: str) -> Dict:
        return self.jobs.get(job_id, {"status": "error", "message": "Job not found"})
