import os
import shutil
import hashlib
from datetime import datetime
from forensic_suite.utils.file_utils import FileUtils
from forensic_suite.utils.os_detector import detect_os_from_dump

class EvidenceManager:
    def __init__(self, data_dir: str, upload_dir: str = 'uploads'):
        self.data_dir = data_dir
        self.upload_dir = upload_dir
        os.makedirs(self.upload_dir, exist_ok=True)
        os.makedirs(self.data_dir, exist_ok=True)

    def register_dump(self, file_path: str, source: str = "uploaded") -> dict:
        """
        Registers a memory dump file as the active evidence.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File {file_path} not found.")

        filename = os.path.basename(file_path)
        size = FileUtils.get_file_size(file_path)
        sha256 = self._calculate_sha256(file_path)
        detected_os = detect_os_from_dump(file_path)
        
        evidence_info = {
            "active_memory_dump": file_path,
            "filename": filename,
            "size_bytes": size,
            "size_human": FileUtils.format_size(size),
            "hash": sha256,
            "source": source,
            "timestamp": datetime.now().isoformat(),
            "detected_os": detected_os,
            "status": "ready_for_analysis"
        }
        
        FileUtils.set_active_dump(self.data_dir, evidence_info)
        return evidence_info

    def handle_upload(self, file_obj) -> dict:
        """
        Saves an uploaded file and registers it as evidence.
        """
        if not file_obj or file_obj.filename == '':
            raise ValueError("No file uploaded.")

        if not FileUtils.is_valid_extension(file_obj.filename):
            raise ValueError("Invalid file extension. Supported: .raw, .mem, .dmp")

        target_path = os.path.join(self.upload_dir, file_obj.filename)
        file_obj.save(target_path)
        
        return self.register_dump(target_path, source="uploaded")

    def get_active_evidence(self) -> dict:
        """
        Retrieves the current active evidence.
        """
        evidence = FileUtils.get_active_dump(self.data_dir)
        if evidence and evidence.get('active_memory_dump'):
            # Check if file still exists
            if not os.path.exists(evidence['active_memory_dump']):
                evidence['status'] = "file_missing"
        return evidence

    def _calculate_sha256(self, file_path: str) -> str:
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
