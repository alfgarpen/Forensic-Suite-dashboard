from flask import Flask, render_template, request, jsonify, send_file
import os
import psutil

# Import custom scripts
import scripts.memory_acquisition as acq
import scripts.analyze_dump as ad
import scripts.generate_report as gr

app = Flask(__name__)
# Keep everything simple, use current execution context
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
os.makedirs(DATA_DIR, exist_ok=True)

@app.route('/')
def dashboard():
    return render_template('index.html')

@app.route('/api/system_info')
def system_info():
    """Returns basic system info"""
    mem = psutil.virtual_memory()
    return jsonify({
        'ram_total_gb': round(mem.total / (1024**3), 2),
        'cpu_percent': psutil.cpu_percent(),
        'os_name': os.name
    })

@app.route('/api/plugins', methods=['GET'])
def get_plugins():
    """Returns available Volatility plugins"""
    return jsonify({'status': 'success', 'plugins': ad.get_available_plugins()})

@app.route('/api/acquire', methods=['POST'])
def acquire_memory():
    """Endpoint to trigger memory acquisition or file upload"""
    output_raw = os.path.join(DATA_DIR, 'memory.raw')
    
    if 'file' in request.files:
        file = request.files['file']
        if file.filename != '':
            file.save(output_raw)
            # Create a hash for the uploaded file
            aq_instance = acq.MemoryAcquisition()
            file_hash = aq_instance.verify_hash(output_raw)
            return jsonify({'status': 'success', 'message': 'File uploaded.', 'raw_path': output_raw, 'hash': file_hash})
    
    # If no file uploaded, execute acquisition
    aq_instance = acq.MemoryAcquisition()
    out = aq_instance.acquire(output_raw)
    if out:
        file_hash = aq_instance.verify_hash(out)
        return jsonify({'status': 'success', 'message': 'Memory acquired successfully.', 'raw_path': out, 'hash': file_hash})
    
    return jsonify({'status': 'error', 'message': 'Acquisition failed.'}), 500

@app.route('/api/analyze', methods=['POST'])
def analyze_dump():
    data = request.get_json(silent=True) or {}
    dump_path = data.get('dump_path', os.path.join(DATA_DIR, 'memory.raw'))
    plugins = data.get('plugins', ['windows.info', 'windows.pslist', 'windows.netscan'])
    output_json = os.path.join(DATA_DIR, 'results.json')
    
    if not os.path.exists(dump_path):
        return jsonify({'status': 'error', 'message': f'Dump file {dump_path} not found.'}), 404
        
    analyzer = ad.DumpAnalyzer(dump_path)
    analyzer.detect_os()
    results = analyzer.run_plugins(plugins)
    
    with open(output_json, 'w') as f:
        import json
        json.dump(results, f, indent=4)
        
    return jsonify({'status': 'success', 'message': 'Analysis complete.', 'results_path': output_json, 'data': results})

@app.route('/api/report', methods=['POST'])
def generate_report():
    data = request.get_json(silent=True) or {}
    results_path = data.get('results_path', os.path.join(DATA_DIR, 'results.json'))
    output_html = os.path.join(DATA_DIR, 'report.html')
    templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    
    generator = gr.ReportGenerator(templates_dir)
    success = generator.generate(results_path, output_html)
    
    if success:
        return jsonify({'status': 'success', 'message': 'Report generated.', 'report_url': '/download/report'})
    
    return jsonify({'status': 'error', 'message': 'Failed to generate report.'}), 500

@app.route('/download/report')
def download_report():
    report_path = os.path.join(DATA_DIR, 'report.html')
    if os.path.exists(report_path):
        return send_file(report_path, as_attachment=True)
    return "Report not found", 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)
