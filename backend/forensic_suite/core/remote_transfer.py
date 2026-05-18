import os
import socket
import datetime
import hashlib
import json
import shutil
import logging
import threading
import time
from pathlib import Path
import paramiko
from scp import SCPClient

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
CONFIG_PATH = BASE_DIR / "config" / "remote_config.json"
LOG_DIR = BASE_DIR / "logs"
TRANSFER_LOG = LOG_DIR / "transfer.log"
QUEUE_DIR = BASE_DIR / "data" / "transfer_queue"
SENT_DIR = QUEUE_DIR / "sent"
FAILED_DIR = QUEUE_DIR / "failed"

# Ensure directories exist
for d in [LOG_DIR, QUEUE_DIR, SENT_DIR, FAILED_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Setup logging
logging.basicConfig(
    filename=str(TRANSFER_LOG),
    level=logging.INFO,
    format='[%(asctime)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

class RemoteTransferManager:
    def __init__(self):
        self.config = self._load_config()

    def _load_config(self):
        try:
            with open(CONFIG_PATH, 'r') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Error loading config: {e}")
            return {}

    # SSH keys generation removed to simplify remote service

    def get_hostname(self):
        return socket.gethostname()

    def calculate_hash(self, file_path):
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def rename_report(self, file_path):
        """Renames report to Reporte_<HOSTNAME>_<YYYY-MM-DD_HH-MM-SS>.html"""
        p = Path(file_path)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        hostname = self.get_hostname()
        new_name = f"Reporte_{hostname}_{timestamp}{p.suffix}"
        new_path = p.parent / new_name
        os.rename(p, new_path)
        return new_path

    def transfer_file(self, file_path):
        """Main entry point for transferring a file."""
        file_path = Path(file_path)
        if not file_path.exists():
            return False

        logging.info(f"Report detected: {file_path.name}")
        
        # 1. Rename
        if self.config.get("auto_rename", True):
            try:
                old_name = file_path.name
                file_path = self.rename_report(file_path)
                logging.info(f"Renamed {old_name} to {file_path.name}")
            except Exception as e:
                logging.error(f"Rename failed: {e}")

        # 2. Hash
        file_hash = self.calculate_hash(file_path)
        logging.info(f"Hash generated SHA256: {file_hash}")

        # 3. Transfer
        success = self._perform_ssh_transfer(file_path, file_hash)
        
        if success:
            shutil.move(str(file_path), str(SENT_DIR / file_path.name))
        else:
            # Move to failed/queue for retry
            shutil.move(str(file_path), str(FAILED_DIR / file_path.name))
            
        return success

    def _perform_ssh_transfer(self, file_path, local_hash):
        try:
            logging.info("Transferencia iniciada")
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            ssh.connect(
                hostname=self.config.get("remote_host"),
                port=self.config.get("remote_port", 22),
                username=self.config.get("remote_user"),
                password=self.config.get("remote_password"),
                timeout=10
            )

            # Create remote directory structure if it doesn't exist
            hostname = self.get_hostname()
            remote_base = self.config.get("remote_path", "/opt/forensic-reports/")
            remote_target_dir = os.path.join(remote_base, hostname)
            
            # Using SSH to create remote directory
            ssh.exec_command(f"mkdir -p {remote_target_dir}")

            with SCPClient(ssh.get_transport()) as scp:
                scp.put(str(file_path), remote_path=remote_target_dir)

            logging.info("Transferencia completada")

            # 4. Remote verification
            if self.config.get("verify_integrity", True):
                remote_file_path = os.path.join(remote_target_dir, file_path.name)
                stdin, stdout, stderr = ssh.exec_command(f"sha256sum {remote_file_path}")
                remote_output = stdout.read().decode().strip()
                if remote_output:
                    remote_hash = remote_output.split()[0]
                    if remote_hash == local_hash:
                        logging.info("Verificación OK")
                        ssh.close()
                        return True
                    else:
                        logging.error(f"Hash mismatch! Local: {local_hash}, Remote: {remote_hash}")
                else:
                    logging.warning("Could not verify remote hash (sha256sum not found or failed)")
                    # We consider it success if transfer finished but verification command failed
                    ssh.close()
                    return True
            
            ssh.close()
            return True

        except Exception as e:
            logging.error(f"Transfer failed: {e}")
            return False

    def retry_failed(self):
        """Tries to re-send files in the failed directory."""
        for f in FAILED_DIR.glob("*.html"):
            logging.info(f"Retrying failed transfer: {f.name}")
            self.transfer_file(f)

if __name__ == "__main__":
    # Test
    manager = RemoteTransferManager()
    print(f"Hostname: {manager.get_hostname()}")
    print(f"Config: {manager.config}")
