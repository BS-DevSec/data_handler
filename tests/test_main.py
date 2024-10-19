from unittest.mock import patch, MagicMock
from main import MainApp
import pytest
from pathlib import Path


@pytest.fixture
def mock_config():
    config = MagicMock()
    config.get.side_effect = lambda section, key=None, default=None: {
        'data_loader': {'offline_file': 'offline.csv', 'online_file': 'online.csv'},
        'plotter': {'plot_dir': 'plot/'},
        'logging': {'level': 'DEBUG'},
        'data_processor': {'online_numeric_columns': []}
    }.get(section, default)
    return config


@pytest.fixture
def app(mock_config):
    return MainApp(mock_config, Path('/some/fake/path'))


def test_run_success(app):
    with patch.object(app.data_loader, 'load_data') as mock_load_data, \
            patch.object(app.data_loader, 'process_online_time_column'), \
            patch.object(app.data_loader, 'convert_columns_to_numeric'), \
            patch('data_processor.DataProcessor.extract_offline_columns'), \
            patch('data_processor.DataProcessor.calculate_feed_time'), \
            patch('data_processor.DataProcessor.get_valid_masks'), \
            patch('plotter.Plotter.plot_data'):
        app.run()

    mock_load_data.assert_called_once()


def test_run_kla_workflow_success(app):
    kla_file = Path('/some/fake/path/kla_data.txt')

    with patch.object(app.data_loader, 'load_kla_data'), \
            patch('data_processor.DataProcessor.preprocess_kla_data'), \
            patch('plotter.Plotter.plot_kla_data'):
        app.run_kla_workflow(kla_file)
