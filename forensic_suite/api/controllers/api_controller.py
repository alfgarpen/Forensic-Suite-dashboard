import os
import logging
from forensic_suite.core.evidence_manager import EvidenceManager
from forensic_suite.core.analysis_manager import AnalysisManager
from forensic_suite.core.report_manager import ReportManager

logger = logging.getLogger(__name__)

class ApiController:
    # Class-level managers to maintain state across requests
    _evidence_mgr = None
    _analysis_mgr = None
    _report_mgr = None

    @classmethod
    def _get_managers(cls, data_dir: str):
        if cls._evidence_mgr is None:
            cls._evidence_mgr = EvidenceManager(data_dir)
        if cls._analysis_mgr is None:
            cls._analysis_mgr = AnalysisManager(data_dir)
        if cls._report_mgr is None:
            cls._report_mgr = ReportManager(data_dir)
        return cls._evidence_mgr, cls._analysis_mgr, cls._report_mgr

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
        ev_mgr, _, _ = ApiController._get_managers(data_dir)
        try:
            if request_files and 'file' in request_files:
                file = request_files['file']
                res = ev_mgr.handle_upload(file)
                return {
                    'status': 'success', 
                    'message': 'File uploaded and set as active evidence.', 
                    'active_dump': res
                }
            
            # Local acquisition (simplified for this task)
            from forensic_suite.core.acquisition import Acquisition
            acq = Acquisition()
            output_raw = os.path.join(data_dir, 'memory.raw')
            out = acq.acquire_memory(output_raw)
            if out:
                res = ev_mgr.register_dump(out, source="local_acquisition")
                return {
                    'status': 'success', 
                    'message': 'Memory acquired and set as active evidence.', 
                    'active_dump': res
                }
            
            return {'status': 'error', 'message': 'Acquisition failed.'}, 500
        except Exception as e:
            logger.error(f"Error in acquire: {e}")
            return {'status': 'error', 'message': str(e)}, 400

    @staticmethod
    def analyze_async(data: dict, data_dir: str):
        ev_mgr, an_mgr, _ = ApiController._get_managers(data_dir)
        
        active = ev_mgr.get_active_evidence()
        dump_path = data.get('dump_path') or active.get('active_memory_dump')
        
        if not dump_path or not os.path.exists(dump_path):
            return {'status': 'error', 'message': 'No valid dump path found for analysis.'}, 404

        plugins = data.get('plugins')
        job_id = an_mgr.start_analysis(dump_path, plugins)

        return {
            'status': 'success', 
            'message': 'Analysis started.', 
            'job_id': job_id, 
            'dump_used': dump_path
        }

    @staticmethod
    def get_job_status(job_id: str):
        # We need a data_dir to initialize managers if not already done, 
        # but in practice, they will be initialized by the first call.
        # Assuming data_dir is fixed.
        if ApiController._analysis_mgr is None:
            return {'status': 'error', 'message': 'Analysis manager not initialized.'}, 500
        return ApiController._analysis_mgr.get_job_status(job_id)

    @staticmethod
    def report(data: dict, data_dir: str):
        _, _, rep_mgr = ApiController._get_managers(data_dir)
        res = rep_mgr.generate(data.get('results_path'))
        
        if res['status'] == 'success':
            return res
        return res, 400

    @staticmethod
    def _update_active_dump(path: str, data_dir: str):
        """Compatibility method for existing routes"""
        ev_mgr, _, _ = ApiController._get_managers(data_dir)
        return ev_mgr.register_dump(path, source="manual_update")
