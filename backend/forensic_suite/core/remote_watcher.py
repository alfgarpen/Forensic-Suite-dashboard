import time
import os
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from forensic_suite.core.remote_transfer import RemoteTransferManager

class ReportHandler(FileSystemEventHandler):
    def __init__(self, manager):
        self.manager = manager

    def on_created(self, event):
        if event.is_directory:
            return
        
        # We only care about .html reports
        if event.src_path.endswith(".html"):
            # Wait a bit to ensure the file is fully written
            time.sleep(1)
            print(f"New report detected: {event.src_path}")
            self.manager.transfer_file(event.src_path)

def start_watcher(path_to_watch):
    manager = RemoteTransferManager()
    event_handler = ReportHandler(manager)
    observer = Observer()
    observer.schedule(event_handler, path_to_watch, recursive=False)
    
    print(f"Starting watcher on: {path_to_watch}")
    observer.start()
    
    try:
        while True:
            # Also periodic retry of failed transfers every 5 minutes
            time.sleep(300)
            manager.retry_failed()
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    # Default path to watch
    reports_path = str(Path.home() / "Documentos" / "Reportes")
    if not os.path.exists(reports_path):
        os.makedirs(reports_path, exist_ok=True)
        
    start_watcher(reports_path)
