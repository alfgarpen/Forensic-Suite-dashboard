import os
from flask import Blueprint, jsonify, request, send_file, render_template

from forensic_suite.api.controllers.api_controller import ApiController
from forensic_suite.services.volatility_service import VolatilityService

api_bp = Blueprint('api', __name__)
# Try to reach the root templates dir, assuming app is running from root
DATA_DIR = os.path.join(os.getcwd(), 'data')
os.makedirs(DATA_DIR, exist_ok=True)

@api_bp.route('/')
def dashboard():
    return render_template('index.html')

@api_bp.route('/api/system_info', methods=['GET'])
def system_info():
    return jsonify(ApiController.get_system_info())

@api_bp.route('/api/plugins', methods=['GET'])
def get_plugins():
    vol_service = VolatilityService()
    plugins_list = vol_service.get_available_plugins()
    # Format required by the frontend: list of dicts with 'id', 'name', and 'description'
    plugins = []
    for p in plugins_list:
        plugin_instance = vol_service.get_plugin(p)
        plugins.append({
            'id': p,
            'name': plugin_instance.name,
            'description': f"{p} module via dynamic engine"
        })
    return jsonify({'status': 'success', 'plugins': plugins})

@api_bp.route('/api/acquire', methods=['POST'])
def acquire_memory():
    res = ApiController.acquire(request.files, DATA_DIR)
    status_code = 500 if type(res) is tuple and res[1] == 500 else 200
    return jsonify(res[0] if type(res) is tuple else res), status_code

@api_bp.route('/api/analyze', methods=['POST'])
def analyze_dump():
    data = request.get_json(silent=True) or {}
    res = ApiController.analyze_async(data, DATA_DIR)
    status_code = 404 if type(res) is tuple and res[1] == 404 else 200
    return jsonify(res[0] if type(res) is tuple else res), status_code

@api_bp.route('/api/status/<job_id>', methods=['GET'])
def get_status(job_id):
    res = ApiController.get_job_status(job_id)
    status_code = 404 if type(res) is tuple and res[1] == 404 else 200
    return jsonify(res[0] if type(res) is tuple else res), status_code

@api_bp.route('/api/report', methods=['POST'])
def generate_report():
    data = request.get_json(silent=True) or {}
    res = ApiController.report(data, DATA_DIR)
    status_code = res[1] if type(res) is tuple else 200
    return jsonify(res[0] if type(res) is tuple else res), status_code

@api_bp.route('/download/report', methods=['GET'])
def download_report():
    report_path = os.path.join(DATA_DIR, 'report.html')
    if os.path.exists(report_path):
        return send_file(report_path, as_attachment=True)
    return "Report not found", 404
