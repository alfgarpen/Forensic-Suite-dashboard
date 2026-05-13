import os
from flask import Blueprint, jsonify, request, send_file, render_template

from forensic_suite.api.controllers.api_controller import ApiController
from forensic_suite.services.volatility_service import VolatilityService
from forensic_suite.utils.file_utils import FileUtils

api_bp = Blueprint('api', __name__)
# Project root is 3 levels up from backend/forensic_suite/api/routes.py
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
DATA_DIR = os.path.join(BASE_DIR, 'data')
REPORTS_DIR = os.path.join(BASE_DIR, 'reports')
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

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
        return jsonify({'status': 'error', 'message': 'Invalid extension. Supported: .raw, .mem, .dmp, .lime'}), 400
        
    dump_info = ApiController._update_active_dump(path, DATA_DIR)
    return jsonify({'status': 'success', 'message': 'Active dump updated.', 'active_dump': dump_info})

@api_bp.route('/download/report', methods=['GET'])
def download_report():
    # Priority 1: Specific report requested via query param
    filename = request.args.get('file')
    if filename:
        report_path = os.path.join(REPORTS_DIR, filename)
        if os.path.exists(report_path):
            return send_file(report_path, as_attachment=False) # View in browser

    # Priority 2: Generic 'report.html' in DATA_DIR (legacy/active)
    report_path = os.path.join(DATA_DIR, 'report.html')
    if os.path.exists(report_path):
        return send_file(report_path, as_attachment=False)
    
    # Priority 3: Latest report in REPORTS_DIR
    try:
        reports = [f for f in os.listdir(REPORTS_DIR) if f.endswith('.html')]
        if reports:
            latest_report = max([os.path.join(REPORTS_DIR, f) for f in reports], key=os.path.getmtime)
            return send_file(latest_report, as_attachment=False)
    except Exception:
        pass

    return "Report not found", 404

@api_bp.route('/api/results', methods=['GET'])
def get_results():
    """Returns the latest analysis results JSON for inline table preview."""
    import json
    results_path = os.path.join(DATA_DIR, 'results.json')
    if not os.path.exists(results_path):
        return jsonify({'status': 'error', 'message': 'No results found'}), 404
    try:
        with open(results_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
