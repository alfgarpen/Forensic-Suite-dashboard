import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

def setup_logger(name, log_file, level=logging.INFO):
    """Function to setup as many loggers as you want"""
    
    # Ensure logs directory exists
    log_path = Path(log_file).parent
    log_path.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s: %(message)s')

    # File handler with rotation
    handler = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Avoid duplicate handlers if setup_logger is called multiple times
    if not logger.handlers:
        logger.addHandler(handler)
        
        # Also log to console
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger

# Pre-defined loggers
def get_backend_logger():
    log_file = os.path.join(os.getcwd(), '..', 'logs', 'backend.log')
    return setup_logger('backend', log_file)

def get_analysis_logger():
    log_file = os.path.join(os.getcwd(), '..', 'logs', 'analysis.log')
    return setup_logger('analysis', log_file)

def get_error_logger():
    log_file = os.path.join(os.getcwd(), '..', 'logs', 'errors.log')
    return setup_logger('errors', logging.ERROR)
