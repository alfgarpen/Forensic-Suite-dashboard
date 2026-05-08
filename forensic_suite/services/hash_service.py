import os
import hashlib
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class HashService:
    @staticmethod
    def calculate_hash(file_path: str, algorithm: str = 'md5') -> dict:
        """
        Calculates the cryptographic hash of a file using the specified algorithm.
        Returns a dictionary with the hash, algorithm, and timestamp.
        """
        if not os.path.exists(file_path):
            logger.error(f"File not found for hashing: {file_path}")
            return None

        hash_obj = None
        if algorithm.lower() == 'md5':
            hash_obj = hashlib.md5()
        elif algorithm.lower() == 'sha1':
            hash_obj = hashlib.sha1()
        elif algorithm.lower() == 'sha256':
            hash_obj = hashlib.sha256()
        else:
            logger.error(f"Unsupported hashing algorithm: {algorithm}")
            return None

        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_obj.update(chunk)
            
            result = {
                "hash": hash_obj.hexdigest(),
                "algorithm": algorithm.lower(),
                "timestamp": datetime.now().isoformat()
            }
            logger.info(f"Calculated {result['algorithm']} for {file_path}: {result['hash']}")
            return result
        except Exception as e:
            logger.error(f"Error calculating hash: {str(e)}")
            return None

    @staticmethod
    def verify_hash(file_path: str, expected_hash: str, algorithm: str = 'md5') -> bool:
        """Verifies if a file matches the expected hash."""
        result = HashService.calculate_hash(file_path, algorithm)
        if result and result['hash'] == expected_hash:
            return True
        return False
