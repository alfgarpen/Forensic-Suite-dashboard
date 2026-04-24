import click
import psutil
import hashlib
import os
import time

class MemoryAcquisition:
    def __init__(self):
        self.algorithm = 'md5'

    def _detect_ram_size(self):
        return psutil.virtual_memory().total

    def _validate_permissions(self):
        # In a real environment, we'd check for Administrator/root privileges.
        return True

    def acquire(self, output_path):
        if not self._validate_permissions():
            click.echo("Error: Administrator privileges required to acquire memory.")
            return None

        ram_size = self._detect_ram_size()
        ram_gb = ram_size / (1024**3)
        click.echo(f"System RAM detected: {ram_gb:.2f} GB")
        
        click.echo(f"Acquiring memory to {output_path}...")
        
        # Simulate memory acquisition
        with click.progressbar(range(100), label='Dumping RAM') as bar:
            for _ in bar:
                time.sleep(0.02) # Mock wait
        
        # Create a mock .raw file
        try:
            with open(output_path, 'wb') as f:
                # Write a very small mock payload as representation of the RAW file
                f.write(b"MOCK_MEMORY_DUMP_DATA_START" + os.urandom(1024) + b"MOCK_MEMORY_DUMP_DATA_END")
        except Exception as e:
            click.echo(f"Error writing to output file: {e}")
            return None
        
        return output_path

    def verify_hash(self, filepath, algo='md5'):
        hash_func = getattr(hashlib, algo)()
        if not os.path.exists(filepath):
            return None

        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_func.update(chunk)
                
        h = hash_func.hexdigest()
        hash_file = filepath + ".hash"
        with open(hash_file, 'w') as f:
            f.write(h)
        click.echo(f"Hash ({algo}): {h}")
        click.echo(f"Hash saved to {hash_file}")
        return h

@click.command()
@click.option('--output', '-o', default='data/dump.raw', help='Path to output the memory dump.')
@click.option('--algo', '-a', default='md5', help='Hashing algorithm (md5, sha1, sha256).')
def main(output, algo):
    """Acquires system RAM and generates cryptographic hash."""
    click.echo("--- Digital Forensics: Memory Acquisition ---")
    acq = MemoryAcquisition()
    # Create dir if not exists
    os.makedirs(os.path.dirname(os.path.abspath(output)), exist_ok=True)
    out = acq.acquire(output)
    if out:
        acq.verify_hash(out, algo)
        click.echo(f"Acquisition complete. Output: {out}")

if __name__ == '__main__':
    main()
