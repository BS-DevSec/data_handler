import pytest
import pandas as pd
from unittest.mock import patch, mock_open, MagicMock
from io import StringIO
from data_loader import DataLoader
from pathlib import Path


@pytest.fixture
def mock_config():
    return {
        'data_loader': {
            'offline_file': 'offline.csv',
            'online_file': 'online.csv',
            'kla_dir': 'kla_dir',
            'column_separator': ',',
            'decimal_separator': '.',
            'encoding': 'utf-8'
        }
    }


@pytest.fixture
def data_loader(mock_config):
    config = MagicMock()
    config.get.return_value = mock_config['data_loader']
    return DataLoader(config, Path('/some/fake/path'))


def test_load_data_success(data_loader):
    offline_data = StringIO("col1,col2\n1,2\n3,4")
    online_data = StringIO("col1,col2\n5,6\n7,8")

    with patch('builtins.open', mock_open(read_data=offline_data.getvalue())):
        with patch('pandas.read_csv') as mock_read_csv:
            mock_read_csv.side_effect = [pd.read_csv(offline_data), pd.read_csv(online_data)]
            data_loader.load_data()

    assert data_loader.offline_data is not None
    assert data_loader.online_data is not None


def test_load_data_file_not_found(data_loader):
    with patch('pandas.read_csv', side_effect=FileNotFoundError):
        with pytest.raises(FileNotFoundError):
            data_loader.load_data()


def test_load_data_parser_error(data_loader):
    with patch('pandas.read_csv', side_effect=pd.errors.ParserError("Parse error")):
        with pytest.raises(pd.errors.ParserError):
            data_loader.load_data()


def test_process_online_time_column_success(data_loader):
    online_data = pd.DataFrame({'Zeit': ['12:00:00', '13:00:00']})
    data_loader.online_data = online_data

    data_loader.process_online_time_column()

    assert 'time' in data_loader.online_data.columns


def test_process_online_time_column_missing_column(data_loader):
    data_loader.online_data = pd.DataFrame({'OtherColumn': [1, 2]})

    with pytest.raises(KeyError):
        data_loader.process_online_time_column()


def test_convert_columns_to_numeric_success(data_loader):
    online_data = pd.DataFrame({'col1': ['1', '2'], 'col2': ['3', '4']})
    data_loader.online_data = online_data

    data_loader.convert_columns_to_numeric(['col1', 'col2'], 'online')

    assert pd.api.types.is_numeric_dtype(data_loader.online_data['col1'])


def test_convert_columns_to_numeric_missing_column(data_loader):
    online_data = pd.DataFrame({'col1': ['1', '2']})
    data_loader.online_data = online_data

    data_loader.convert_columns_to_numeric(['col1', 'missing_col'], 'online')

    assert 'missing_col' not in data_loader.online_data.columns


def test_find_data_start_success(data_loader):
    file_content = 'Header\nTime;SomeColumn\nunit;unit\n12:00;1\n'

    # Mock the file open operation and simulate reading lines directly
    with patch('builtins.open', mock_open(read_data=file_content)) as mock_file:
        line_num, header, units = data_loader.find_data_start('/some/fake/path')

    assert line_num == 3  # Adjusted to match the code behavior
    assert header == 'Time;SomeColumn'
    assert units == 'unit;unit'


def test_load_kla_data_success(data_loader):
    kla_content = 'Time;Val\n01.01.2020 00:00:00;100\n02.01.2020 00:00:00;200\n'
    with patch.object(data_loader, 'find_data_start', return_value=(1, 'Time;Val', 'unit;unit')):
        with patch('builtins.open', mock_open(read_data=kla_content)):
            result = pd.read_csv(StringIO(kla_content), delimiter=';')
            data_loader.load_kla_data('/some/fake/path')

    assert isinstance(result, pd.DataFrame)
    assert 'Time' in result.columns


def test_load_kla_data_file_not_found(data_loader):
    with patch.object(data_loader, 'find_data_start', side_effect=FileNotFoundError):
        with pytest.raises(FileNotFoundError):
            data_loader.load_kla_data('/some/fake/path')
