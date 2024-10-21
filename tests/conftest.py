# tests/conftest.py
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for all tests

import sys
import pytest
import pandas as pd
from pathlib import Path

@pytest.fixture
def KLA_DATA():
    data = {
        'Time': ['2024-01-01 12:00:00', '2024-01-01 13:00:00'],
        'Measurement1': [1.0, 2.0],
        'Measurement2': [3.0, 4.0]
    }
    return pd.DataFrame(data)

@pytest.fixture
def KLA_DATA_RAW():
    raw_data = """Time;Measurement1;Measurement2
2024-01-01 12:00:00;1,0;3,0
2024-01-01 13:00:00;2,0;4,0"""
    return raw_data

@pytest.fixture
def KLA_DATA_PROCESSED():
    processed_data = pd.DataFrame({
        'Time': pd.to_datetime(['2024-01-01 12:00:00', '2024-01-01 13:00:00'], format='%Y-%m-%d %H:%M:%S'),
        'Measurement1': [1.0, 2.0],
        'Measurement2': [3.0, 4.0]
    })
    return processed_data

@pytest.fixture(scope='session', autouse=True)
def add_src_to_sys_path():
    """
    Adds the 'src' directory to sys.path for all tests.
    """
    project_root = Path(__file__).resolve().parent.parent
    src_path = project_root / 'src'
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    # Optional: Uncomment the next line to debug sys.path during testing
    print("sys.path:", sys.path)
