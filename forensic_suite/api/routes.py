import os
from flask import Blueprint, jsonify, request, send_file, render_template

from forensic_suite.api.controllers.api_controller import ApiController
from forensic_suite.services.volatility_service import VolatilityService
from forensic_suite.utils.file_utils import FileUtils

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
    from forensic_suite.core.plugin_registry import PLUGIN_REGISTRY
    from forensic_suite.utils.file_utils import FileUtils
    
    active = FileUtils.get_active_dump(DATA_DIR)
    detected_os = active.get('detected_os', 'windows') if active else 'windows'
    
    # Get plugins for detected OS or windows as default
    os_plugins = PLUGIN_REGISTRY.get(detected_os.lower(), PLUGIN_REGISTRY['windows'])
    
    formatted_categories = []
    for cat_name, plugins in os_plugins.items():
        category = {
            'name': cat_name,
            'plugins': []
        }
        for p_id, p_desc in plugins.items():
            category['plugins'].append({
                'id': p_id,
                'name': p_id.split('.')[-1].capitalize(),
                'description': p_desc
            })
        formatted_categories.append(category)
        
    return jsonify({
        'status': 'success', 
        'categories': formatted_categories,
        'detected_os': detected_os
    })

@api_bp.route('/api/acquire', methods=['POST'])
def acquire_memory():
    res = ApiController.acquire(request.files, DATA_DIR)
    if isinstance(res, tuple):
        return jsonify(res[0]), res[1]
    return jsonify(res), 200

@api_bp.route('/api/analyze', methods=['POST'])
def analyze_dump():
    data = request.get_json(silent=True) or {}
    res = ApiController.analyze_async(data, DATA_DIR)
    if isinstance(res, tuple):
        return jsonify(res[0]), res[1]
    return jsonify(res), 200

@api_bp.route('/api/status/<job_id>', methods=['GET'])
def get_status(job_id):
    res = ApiController.get_job_status(job_id)
    if isinstance(res, tuple):
        return jsonify(res[0]), res[1]
    return jsonify(res), 200

@api_bp.route('/api/report', methods=['POST'])
def generate_report():
    data = request.get_json(silent=True) or {}
    res = ApiController.report(data, DATA_DIR)
    if isinstance(res, tuple):
        return jsonify(res[0]), res[1]
    return jsonify(res), 200

@api_bp.route('/api/current_dump', methods=['GET', 'POST'])
def current_dump():
    if request.method == 'GET':
        active = FileUtils.get_active_dump(DATA_DIR)
        return jsonify(active)
    
    # POST to update active dump manually
    data = request.get_json(silent=True) or {}
    path = data.get('path')
    if not path or not os.path.exists(path):
        return jsonify({'status': 'error', 'message': f'Invalid path: {path}'}), 400
    
    if not FileUtils.is_valid_extension(path):
        return jsonify({'status': 'error', 'message': 'Invalid extension. Only .raw and .mem are allowed.'}), 400
        
    dump_info = ApiController._update_active_dump(path, DATA_DIR)
    return jsonify({'status': 'success', 'message': 'Active dump updated.', 'active_dump': dump_info})

@api_bp.route('/download/report', methods=['GET'])
def download_report():
    report_path = os.path.join(DATA_DIR, 'report.html')
    if os.path.exists(report_path):
        return send_file(report_path, as_attachment=True)
    return "Report not found", 404
