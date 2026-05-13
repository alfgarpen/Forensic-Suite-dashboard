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

    @staticmethod
    def is_valid_extension(filename: str) -> bool:
        allowed = {'.raw', '.mem', '.dmp', '.lime'}
        return os.path.splitext(filename)[1].lower() in allowed

    @staticmethod
    def get_file_size(file_path: str) -> int:
        if os.path.exists(file_path):
            return os.path.getsize(file_path)
        return 0

    @staticmethod
    def format_size(size_bytes: int) -> str:
        if size_bytes == 0:
            return "0B"
        size_name = ("B", "KB", "MB", "GB", "TB")
        import math
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return "%s %s" % (s, size_name[i])

    @staticmethod
    def get_active_dump(data_dir: str) -> dict:
        state_file = os.path.join(data_dir, 'current_dump.json')
        return FileUtils.read_json(state_file)

    @staticmethod
    def set_active_dump(data_dir: str, dump_info: dict) -> bool:
        state_file = os.path.join(data_dir, 'current_dump.json')
        return FileUtils.write_json(state_file, dump_info)
