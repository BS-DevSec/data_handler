import pandas as pd
from io import StringIO
from data_loader import DataLoader


# Test loading data
def test_load_data(mocker):
    mocker.patch('pandas.read_csv', return_value=pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]}))

    loader = DataLoader('offline_file.txt', 'online_file.txt')
    loader.load_data()

    assert isinstance(loader.offline_data, pd.DataFrame)
    assert isinstance(loader.online_data, pd.DataFrame)


# Test process_online_time_column
def test_process_online_time_column(mocker):
    data = pd.DataFrame({'Zeit': ['12:00:00', '13:00:00']})

    # Create an instance of DataLoader and mock the `online_data` attribute on the instance.
    loader = DataLoader('offline_file.txt', 'online_file.txt')
    mocker.patch.object(loader, 'online_data', data)

    loader.process_online_time_column()

    assert 'time' in loader.online_data.columns


# Test KLA data loading
def test_load_kla_data(mocker):
    mock_file_data = StringIO('Time;Value1;Value2\n12.03.2021 14:00:00;10;20\n')
    mocker.patch('builtins.open', mocker.mock_open(read_data=mock_file_data.read()))
    mocker.patch('pandas.read_csv',
                 return_value=pd.DataFrame({'Time': ['12.03.2021 14:00:00'], 'Value1': [10], 'Value2': [20]}))

    loader = DataLoader('offline_file.txt', 'online_file.txt')
    kla_data = loader.load_kla_data('kla_file.txt')

    assert 'Time' in kla_data.columns
