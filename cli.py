import sys
import os

# Add root to pythonpath
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from forensic_suite.cli.commands import cli

if __name__ == '__main__':
    cli()
