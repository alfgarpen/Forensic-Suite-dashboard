import os
import uuid
import threading
from datetime import datetime
from forensic_suite.core.acquisition import Acquisition
from forensic_suite.core.analysis_engine import AnalysisEngine
from forensic_suite.core.reporting import Reporting
from forensic_suite.utils.file_utils import FileUtils
from forensic_suite.services.hash_service import HashService
import logging

logger = logging.getLogger(__name__)

# In-memory job storage
jobs = {}

def start_analysis_job(job_id: str, dump_path: str, plugins: list, output_json: str, data_dir: str):
    jobs[job_id] = {"status": "running", "result": None}
    try:
        engine = AnalysisEngine(dump_path)
        results = engine.run_analysis(plugins)
        FileUtils.write_json(output_json, results)
        
        # Link results to active dump if applicable
        active = FileUtils.get_active_dump(data_dir)
        if active.get('path') == dump_path:
            active['last_results'] = output_json
            FileUtils.set_active_dump(data_dir, active)
            
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
    def _update_active_dump(path: str, data_dir: str):
        md5 = HashService.calculate_hash(path, 'md5')
        sha1 = HashService.calculate_hash(path, 'sha1')
        sha256 = HashService.calculate_hash(path, 'sha256')
        
        dump_info = {
            "path": path,
            "uploaded_at": datetime.now().isoformat(),
            "hashes": {
                "md5": md5['hash'] if md5 else "",
                "sha1": sha1['hash'] if sha1 else "",
                "sha256": sha256['hash'] if sha256 else ""
            },
            "type": os.path.splitext(path)[1][1:].lower()
        }
        FileUtils.set_active_dump(data_dir, dump_info)
        return dump_info

    @staticmethod
    def acquire(request_files, data_dir: str):
        try:
            acq = Acquisition()

            if request_files and 'file' in request_files:
                file = request_files['file']
                if file.filename != '':
                    if not FileUtils.is_valid_extension(file.filename):
                        return {'status': 'error', 'message': 'Invalid file extension. Only .raw and .mem are allowed.'}, 400
                    
                    output_path = os.path.join(data_dir, file.filename)
                    temp_path = os.path.join(data_dir, f"temp_{uuid.uuid4().hex}_{file.filename}")
                    file.save(temp_path)
                    out = acq.process_upload(temp_path, output_path)
                    os.remove(temp_path)
                    
                    if out:
                        dump_info = ApiController._update_active_dump(out, data_dir)
                        return {
                            'status': 'success', 
                            'message': 'File uploaded and set as active dump.', 
                            'active_dump': dump_info,
                            'hash': dump_info['hashes']['md5'],  # Compatibility
                            'raw_path': out                      # Compatibility
                        }
                    else:
                        return {'status': 'error', 'message': 'Failed to process upload.'}, 500

            # Local acquisition (mock)
            output_raw = os.path.join(data_dir, 'memory.raw')
            out = acq.acquire_memory(output_raw)
            if out:
                dump_info = ApiController._update_active_dump(out, data_dir)
                return {
                    'status': 'success', 
                    'message': 'Memory acquired successfully and set as active dump.', 
                    'active_dump': dump_info,
                    'hash': dump_info['hashes']['md5'],  # Compatibility
                    'raw_path': out                      # Compatibility
                }
            
            return {'status': 'error', 'message': 'Acquisition failed.'}, 500
        except Exception as e:
            logger.error(f"Error in acquire: {e}")
            return {'status': 'error', 'message': f'Internal server error: {str(e)}'}, 500

    @staticmethod
    def analyze_async(data: dict, data_dir: str):
        dump_path = data.get('dump_path')
        
        if not dump_path:
            active = FileUtils.get_active_dump(data_dir)
            if not active or not active.get('path'):
                return {'status': 'error', 'message': 'No dump path provided and no active dump found.'}, 404
            dump_path = active['path']

        if not os.path.exists(dump_path):
            return {'status': 'error', 'message': f'Dump file {dump_path} not found.'}, 404

        plugins = data.get('plugins', None)
        output_json = os.path.join(data_dir, 'results.json')
        
        job_id = str(uuid.uuid4())
        jobs[job_id] = {"status": "pending"}

        thread = threading.Thread(target=start_analysis_job, args=(job_id, dump_path, plugins, output_json, data_dir))
        thread.start()

        return {'status': 'success', 'message': 'Analysis started.', 'job_id': job_id, 'dump_used': dump_path}

    @staticmethod
    def get_job_status(job_id: str):
        if job_id not in jobs:
            return {'status': 'error', 'message': 'Job not found.'}, 404
        return jobs[job_id]

    @staticmethod
    def report(data: dict, data_dir: str):
        results_path = data.get('results_path')
        
        if not results_path:
            active = FileUtils.get_active_dump(data_dir)
            results_path = active.get('last_results', os.path.join(data_dir, 'results.json'))

        if not os.path.exists(results_path):
            return {'status': 'error', 'message': f'Results file {results_path} not found. Run analysis first.'}, 404

        output_html = os.path.join(data_dir, 'report.html')
        results_data = FileUtils.read_json(results_path)

        reporter = Reporting()
        if reporter.generate_html_report(results_data, output_html):
             return {'status': 'success', 'message': 'Report generated.', 'report_url': '/download/report'}
             
        return {'status': 'error', 'message': 'Failed to generate report.'}, 500
