import os
import json
import logging

logger = logging.getLogger(__name__)

class FileUtils:
    @staticmethod
    def read_json(file_path: str) -> dict:
        if not os.path.exists(file_path):
            return {}
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error reading JSON from {file_path}: {e}")
            return {}

    @staticmethod
    def write_json(file_path: str, data: dict, indent: int = 4) -> bool:
        try:
            os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=indent)
            return True
        except Exception as e:
            logger.error(f"Error writing JSON to {file_path}: {e}")
            return False

    @staticmethod
    def ensure_dir(dir_path: str) -> bool:
        try:
            os.makedirs(dir_path, exist_ok=True)
            return True
        except Exception as e:
            logger.error(f"Error ensuring directory {dir_path}: {e}")
            return False
