import os
import sys

def get_local_os() -> str:
    """
    Returns the current machine's OS as 'windows', 'linux', or 'mac'.
    """
    if sys.platform == "win32":
        return "windows"
    elif sys.platform.startswith("linux"):
        return "linux"
    elif sys.platform == "darwin":
        return "mac"
    return "unknown"

def detect_os_from_dump(dump_path: str) -> str:
    """
    Attempts to detect the OS of a memory dump by checking its file header.
    """
    if not os.path.exists(dump_path):
        return "unknown"
        
    try:
        with open(dump_path, 'rb') as f:
            header = f.read(16)
            
            # Check for ELF (Linux)
            if header.startswith(b'\x7fELF'):
                return "linux"
                
            # Check for Windows Memory Dump (PAGEDUMP/PAGEDU64)
            if header.startswith(b'PAGEDU64') or header.startswith(b'PAGEDUMP'):
                return "windows"
                
            # Check for Windows Minidump
            if header.startswith(b'MDMP'):
                return "windows"

            # Check for LiME (Linux Memory Extractor) - starts with 'LiME' (\x4c\x69\x4d\x45)
            if header.startswith(b'LiME'):
                return "linux"
                
            # Fallback to extension
            ext = os.path.splitext(dump_path)[1].lower()
            if ext in ['.mem', '.dmp', '.vmem']:
                return "windows"
            elif ext in ['.lime', '.elf']:
                return "linux"
            elif ext == '.raw':
                # .raw is ambiguous, keep as unknown to trigger advanced detection
                return "unknown"
                
    except Exception:
        pass
        
    return "unknown"
