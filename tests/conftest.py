# tests/conftest.py

import sys
from pathlib import Path

# Get the absolute path to the project root directory
project_root = Path(__file__).resolve().parent.parent

# Path to the src directory
src_path = project_root / 'src'

# Add src to sys.path if not already present
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Debugging line to verify sys.path modification
print("DEBUG: Added 'src' to sys.path:", str(src_path) in sys.path)
print("DEBUG: Current sys.path:", sys.path)
