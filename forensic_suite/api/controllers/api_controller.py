import os
import uuid
import threading
from forensic_suite.core.acquisition import Acquisition
from forensic_suite.core.analysis_engine import AnalysisEngine
from forensic_suite.core.reporting import Reporting
from forensic_suite.utils.file_utils import FileUtils

# In-memory job storage
jobs = {}

def start_analysis_job(job_id: str, dump_path: str, plugins: list, output_json: str):
    jobs[job_id] = {"status": "running", "result": None}
    try:
        engine = AnalysisEngine(dump_path)
        results = engine.run_analysis(plugins)
        FileUtils.write_json(output_json, results)
        jobs[job_id] = {"status": "completed", "result": results, "output_file": output_json}
    except Exception as e:
        jobs[job_id] = {"status": "failed", "error": str(e)}

class ApiController:
    @staticmethod
    def get_system_info():
        import psutil
        mem = psutil.virtual_memory()
        return {
            'ram_total_gb': round(mem.total / (1024**3), 2),
            'cpu_percent': psutil.cpu_percent(),
            'os_name': os.name
        }

    @staticmethod
    def acquire(request_files, data_dir: str):
        output_raw = os.path.join(data_dir, 'memory.raw')
        acq = Acquisition()

        if request_files and 'file' in request_files:
            file = request_files['file']
            if file.filename != '':
                temp_path = os.path.join(data_dir, f"temp_{uuid.uuid4().hex}_{file.filename}")
                file.save(temp_path)
                out = acq.process_upload(temp_path, output_raw)
                os.remove(temp_path)
                if out:
                    file_hash = acq.verify_dump(out)
                    return {'status': 'success', 'message': 'File uploaded.', 'raw_path': out, 'hash': file_hash['hash'] if file_hash else ''}

        out = acq.acquire_memory(output_raw)
        if out:
            file_hash = acq.verify_dump(out)
            return {'status': 'success', 'message': 'Memory acquired successfully.', 'raw_path': out, 'hash': file_hash['hash'] if file_hash else ''}
        
        return {'status': 'error', 'message': 'Acquisition failed.'}, 500

    @staticmethod
    def analyze_async(data: dict, data_dir: str):
        dump_path = data.get('dump_path', os.path.join(data_dir, 'memory.raw'))
        plugins = data.get('plugins', None)
        output_json = os.path.join(data_dir, 'results.json')
        
        if not os.path.exists(dump_path):
            return {'status': 'error', 'message': f'Dump file {dump_path} not found.'}, 404

        job_id = str(uuid.uuid4())
        jobs[job_id] = {"status": "pending"}

        thread = threading.Thread(target=start_analysis_job, args=(job_id, dump_path, plugins, output_json))
        thread.start()

        return {'status': 'success', 'message': 'Analysis started.', 'job_id': job_id}

    @staticmethod
    def get_job_status(job_id: str):
        if job_id not in jobs:
            return {'status': 'error', 'message': 'Job not found.'}, 404
        return jobs[job_id]

    @staticmethod
    def report(data: dict, data_dir: str):
        results_path = data.get('results_path', os.path.join(data_dir, 'results.json'))
        output_html = os.path.join(data_dir, 'report.html')
        
        results_data = FileUtils.read_json(results_path)
        if not results_data:
            return {'status': 'error', 'message': f'Results file {results_path} not found or empty.'}, 404

        reporter = Reporting()
        if reporter.generate_html_report(results_data, output_html):
             return {'status': 'success', 'message': 'Report generated.', 'report_url': '/download/report'}
             
        return {'status': 'error', 'message': 'Failed to generate report.'}, 500
