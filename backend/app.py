import os
from flask import Flask
from forensic_suite.api.routes import api_bp
from forensic_suite.utils.logger import get_backend_logger

logger = get_backend_logger()

def create_app():
    # Templates are now in ../frontend/templates
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend', 'templates'))
    static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend', 'static'))
    
    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
    
    # Register blueprints
    app.register_blueprint(api_bp)
    
    logger.info("Forensic Suite Dashboard initialized.")
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5001, host='0.0.0.0')
