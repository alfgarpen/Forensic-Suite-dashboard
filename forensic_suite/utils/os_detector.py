import os

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
                
            # Fallback to extension
            ext = os.path.splitext(dump_path)[1].lower()
            if ext == '.mem':
                return "windows"
            elif ext == '.raw':
                return "unknown" # Could be either
                
    except Exception:
        pass
        
    return "unknown"
