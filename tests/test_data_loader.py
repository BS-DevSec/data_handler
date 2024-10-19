# tests/test_data_loader.py

import pytest
from pathlib import Path
import pandas as pd
from io import StringIO
from unittest.mock import mock_open, patch

from src.data_loader import DataLoader

# Sample data for offline and online CSV files
OFFLINE_CSV = """Zeit_BTM\tZeit_G\tZeit_E\tBTM\tEtOH\tGlu
12:00:00\t12:00:00\t12:00:00\t1.5\t0.5\t2.0
13:00:00\t13:00:00\t13:00:00\t1.6\t0.6\t2.1
"""

ONLINE_CSV = """Zeit\tspH\tspO2\tNStirrer\tsTR\tsCO2\tsO2\tFAirIn\tsVR\tFGlucose
12:00:00.000\t7.0\t85\t100\t200\t5\t20\t1.2\t10\t0.5
13:00:00.000\t7.1\t86\t101\t201\t6\t21\t1.3\t11\t0.6
"""

KLA_CSV = """Time;Measurement1;Measurement2
2024-01-01 12:00:00;1,0;2,0
2024-01-01 13:00:00;1,1;2,1
"""


@pytest.fixture
def mock_offline_file():
    return "data/hk18/offlindata_HK_45.txt"


@pytest.fixture
def mock_online_file():
    return "data/hk18/onlindata_HK_453.txt"


@pytest.fixture
def mock_kla_file():
    return "data/data(kla)/Daten(klA)400rpm 3L.txt"


@pytest.fixture
def data_loader(mock_offline_file, mock_online_file):
    return DataLoader(offline_file=mock_offline_file, online_file=mock_online_file)


def test_load_data_success(data_loader, mock_offline_file, mock_online_file):
    with patch("pandas.read_csv") as mock_read_csv:
        # Mock the offline and online dataframes
        mock_offline_df = pd.read_csv(StringIO(OFFLINE_CSV), sep='\t',
                                      na_values=['#NAN', 'NaN', 'nan', '#DIV/0!', 'inf', '-inf'], decimal=',')
        mock_online_df = pd.read_csv(StringIO(ONLINE_CSV), sep='\t',
                                     na_values=['#NAN', 'NaN', 'nan', '#DIV/0!', 'inf', '-inf'], decimal=',',
                                     encoding="utf-8")
        mock_read_csv.side_effect = [mock_offline_df, mock_online_df]

        data_loader.load_data()

        # Assertions
        assert data_loader.offline_data is not None
        assert data_loader.online_data is not None
        pd.testing.assert_frame_equal(data_loader.offline_data, mock_offline_df)
        pd.testing.assert_frame_equal(data_loader.online_data, mock_online_df)


def test_load_data_file_not_found(data_loader, mock_offline_file, mock_online_file):
    with patch("pandas.read_csv", side_effect=FileNotFoundError("File not found")):
        with pytest.raises(FileNotFoundError):
            data_loader.load_data()


def test_process_online_time_column_success(data_loader, mock_online_file):
    with patch("pandas.read_csv") as mock_read_csv:
        # Mock online data with 'Zeit' column
        mock_online_df = pd.DataFrame({
            'Zeit': ['12:00:00.000', '13:00:00.000'],
            'spH': [7.0, 7.1],
            'spO2': [85, 86],
            'NStirrer': [100, 101],
            'sTR': [200, 201],
            'sCO2': [5, 6],
            'sO2': [20, 21],
            'FAirIn': [1.2, 1.3],
            'sVR': [10, 11],
            'FGlucose': [0.5, 0.6]
        })
        data_loader.online_data = mock_online_df.copy()

        data_loader.process_online_time_column()

        # Check if 'time' column is added and correctly parsed
        assert 'time' in data_loader.online_data.columns
        assert pd.api.types.is_datetime64_any_dtype(data_loader.online_data['time'])
        assert data_loader.online_data['time'].iloc[0] == pd.to_datetime('12:00:00', format='%H:%M:%S')
        assert data_loader.online_data['time'].iloc[1] == pd.to_datetime('13:00:00', format='%H:%M:%S')


def test_process_online_time_column_missing_zeit(data_loader, mock_online_file):
    # Mock online data without 'Zeit' column
    mock_online_df = pd.DataFrame({
        'spH': [7.0, 7.1],
        'spO2': [85, 86],
        'NStirrer': [100, 101],
        'sTR': [200, 201],
        'sCO2': [5, 6],
        'sO2': [20, 21],
        'FAirIn': [1.2, 1.3],
        'sVR': [10, 11],
        'FGlucose': [0.5, 0.6]
    })
    data_loader.online_data = mock_online_df.copy()

    with pytest.raises(KeyError):
        data_loader.process_online_time_column()


def test_convert_columns_to_numeric_online(data_loader, mock_online_file):
    with patch("pandas.read_csv") as mock_read_csv:
        # Mock online data with numeric columns as strings
        mock_online_df = pd.DataFrame({
            'spH': ['7.0', '7.1'],
            'spO2': ['85', '86'],
            'NStirrer': ['100', '101'],
            'sTR': ['200', '201'],
            'sCO2': ['5', '6'],
            'sO2': ['20', '21'],
            'FAirIn': ['1.2', '1.3'],
            'sVR': ['10', '11'],
            'FGlucose': ['0.5', '0.6']
        })
        data_loader.online_data = mock_online_df.copy()

        columns_to_convert = ['spH', 'spO2', 'NStirrer', 'sTR', 'sCO2', 'sO2', 'FAirIn', 'sVR', 'FGlucose']
        data_loader.convert_columns_to_numeric(columns=columns_to_convert, dataset='online')

        for col in columns_to_convert:
            assert pd.api.types.is_numeric_dtype(data_loader.online_data[col])


def test_convert_columns_to_numeric_offline(data_loader, mock_offline_file):
    with patch("pandas.read_csv") as mock_read_csv:
        # Mock offline data with numeric columns as strings
        mock_offline_df = pd.DataFrame({
            'Zeit_BTM': ['12:00:00', '13:00:00'],
            'Zeit_G': ['12:00:00', '13:00:00'],
            'Zeit_E': ['12:00:00', '13:00:00'],
            'BTM': ['1.5', '1.6'],
            'EtOH': ['0.5', '0.6'],
            'Glu': ['2.0', '2.1']
        })
        data_loader.offline_data = mock_offline_df.copy()

        columns_to_convert = ['BTM', 'EtOH', 'Glu']
        data_loader.convert_columns_to_numeric(columns=columns_to_convert, dataset='offline')

        for col in columns_to_convert:
            assert pd.api.types.is_numeric_dtype(data_loader.offline_data[col])


def test_convert_columns_to_numeric_missing_column(data_loader, mock_online_file):
    # Mock online data with some missing columns
    mock_online_df = pd.DataFrame({
        'spH': ['7.0', '7.1'],
        'spO2': ['85', '86'],
        # 'NStirrer' is missing
        'sTR': ['200', '201'],
        'sCO2': ['5', '6'],
        'sO2': ['20', '21'],
        'FAirIn': ['1.2', '1.3'],
        'sVR': ['10', '11'],
        'FGlucose': ['0.5', '0.6']
    })
    data_loader.online_data = mock_online_df.copy()

    columns_to_convert = ['spH', 'spO2', 'NStirrer', 'sTR', 'sCO2']
    with patch("logging.Logger.warning") as mock_logger_warning:
        data_loader.convert_columns_to_numeric(columns=columns_to_convert, dataset='online')
        # 'NStirrer' is missing, should log a warning
        mock_logger_warning.assert_called_with("Column 'NStirrer' not found in online data. Skipping.")
        # The existing columns should be converted
        for col in ['spH', 'spO2', 'sTR', 'sCO2']:
            assert pd.api.types.is_numeric_dtype(data_loader.online_data[col])


def test_find_data_start_success(data_loader, mock_kla_file):
    with patch("builtins.open", mock_open(read_data=KLA_CSV)) as mocked_file:
        data_start, header_line, units_line = data_loader.find_data_start(mock_kla_file)
        # Since 'Time' is at first line, data starts at line 2
        assert data_start == 2
        assert header_line == "Time;Measurement1;Measurement2"
        assert units_line is None  # Only one line of header


def test_find_data_start_not_found(data_loader, mock_kla_file):
    # Data without 'Time' header
    csv_data = """Header1;Header2;Header3
Data1;Data2;Data3
"""
    with patch("builtins.open", mock_open(read_data=csv_data)) as mocked_file:
        data_start, header_line, units_line = data_loader.find_data_start(mock_kla_file)
        assert data_start == 0
        assert header_line is None
        assert units_line is None


def test_load_kla_data_success(data_loader, mock_kla_file):
    with patch("builtins.open", mock_open(read_data=KLA_CSV)) as mocked_file:
        kla_data = data_loader.load_kla_data(mock_kla_file)
        # Expected DataFrame
        expected_df = pd.read_csv(
            StringIO(KLA_CSV),
            delimiter=';',
            decimal=',',
            names=['Time', 'Measurement1', 'Measurement2'],
            usecols=['Time', 'Measurement1', 'Measurement2'],
            engine='python',
            skip_blank_lines=True,
            header=0
        )
        expected_df['Time'] = pd.to_datetime(expected_df['Time'], format='%d.%m.%Y %H:%M:%S', errors='coerce',
                                             dayfirst=True)
        for col in ['Measurement1', 'Measurement2']:
            expected_df[col] = pd.to_numeric(expected_df[col].str.replace(',', '.'), errors='coerce')
        pd.testing.assert_frame_equal(kla_data, expected_df)


def test_load_kla_data_file_not_found(data_loader, mock_kla_file):
    with patch("builtins.open", side_effect=FileNotFoundError("File not found")):
        with pytest.raises(FileNotFoundError):
            data_loader.load_kla_data(mock_kla_file)


def test_load_kla_data_header_not_found(data_loader, mock_kla_file):
    # Data without 'Time' header
    csv_data = """Header1;Header2;Header3
Data1;Data2;Data3
"""
    with patch("builtins.open", mock_open(read_data=csv_data)) as mocked_file:
        with pytest.raises(ValueError, match="Header with 'Time' was not found."):
            data_loader.load_kla_data(mock_kla_file)
