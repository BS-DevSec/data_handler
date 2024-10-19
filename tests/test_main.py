# tests/test_main.py

import pytest
from unittest.mock import patch, MagicMock

from src.main import MainApp


@patch("src.main.DataLoader")
@patch("src.main.DataProcessor")
@patch("src.main.Plotter")
def test_run_main_workflow_success(mock_plotter_class, mock_data_processor_class, mock_data_loader_class):
    # Setup mocks
    mock_data_loader = MagicMock()
    mock_data_loader_class.return_value = mock_data_loader
    mock_data_loader.offline_data = MagicMock()
    mock_data_loader.online_data = MagicMock()

    mock_data_processor = MagicMock()
    mock_data_processor_class.return_value = mock_data_processor

    mock_plotter = MagicMock()
    mock_plotter_class.return_value = mock_plotter

    # Initialize MainApp
    app = MainApp(offline_file="data/hk18/offlindata_HK_45.txt", online_file="data/hk18/onlindata_HK_453.txt")

    # Run the main workflow
    app.run()

    # Assertions
    mock_data_loader_class.assert_called_once_with(offline_file="data/hk18/offlindata_HK_45.txt",
                                                   online_file="data/hk18/onlindata_HK_453.txt")
    mock_data_loader.load_data.assert_called_once()
    mock_data_loader.process_online_time_column.assert_called_once()
    mock_data_loader.convert_columns_to_numeric.assert_called_once_with(
        ['spH', 'spO2', 'NStirrer', 'sTR', 'sCO2', 'sO2', 'FAirIn', 'sVR', 'FGlucose'],
        dataset='online'
    )
    mock_data_processor_class.assert_called_once_with(
        offline_data=mock_data_loader.offline_data,
        online_data=mock_data_loader.online_data
    )
    mock_data_processor.extract_offline_columns.assert_called_once()
    mock_data_processor.calculate_feed_time.assert_called_once()
    mock_data_processor.get_valid_masks.assert_called_once()
    mock_plotter_class.assert_called_once_with(processor=mock_data_processor)
    mock_plotter.plot_data.assert_called_once()


@patch("src.main.DataLoader")
@patch("src.main.DataProcessor")
@patch("src.main.Plotter")
def test_run_main_workflow_exception(mock_plotter_class, mock_data_processor_class, mock_data_loader_class):
    # Setup mocks
    mock_data_loader = MagicMock()
    mock_data_loader_class.return_value = mock_data_loader
    mock_data_loader.load_data.side_effect = Exception("Loading error")

    # Initialize MainApp
    app = MainApp(offline_file="data/hk18/offlindata_HK_45.txt", online_file="data/hk18/onlindata_HK_453.txt")

    # Run the main workflow and capture logs
    with patch("src.main.logger") as mock_logger:
        app.run()
        mock_logger.error.assert_called_with("An error occurred during the main workflow: Loading error")


@patch("src.main.DataLoader")
@patch("src.main.DataProcessor")
@patch("src.main.Plotter")
def test_run_kla_workflow_success(mock_plotter_class, mock_data_processor_class, mock_data_loader_class):
    # Setup mocks
    mock_data_loader = MagicMock()
    mock_data_loader_class.return_value = mock_data_loader
    mock_data_loader.load_kla_data.return_value = MagicMock()

    mock_kla_processor = MagicMock()
    mock_data_processor_class.return_value = mock_kla_processor
    mock_kla_processor.preprocess_kla_data.return_value = MagicMock()

    mock_kla_plotter = MagicMock()
    mock_plotter_class.return_value = mock_kla_plotter

    # Initialize MainApp
    app = MainApp(offline_file="dummy_offline.txt", online_file="dummy_online.txt")

    # Run the KLA workflow
    app.run_kla_workflow(kla_file="data/data(kla)/Daten(klA)400rpm 3L.txt")

    # Assertions
    mock_data_loader_class.assert_called_once_with(offline_file="dummy_offline.txt", online_file="dummy_online.txt")
    mock_data_loader.load_kla_data.assert_called_once_with("data/data(kla)/Daten(klA)400rpm 3L.txt")
    mock_data_processor_class.assert_called_once_with(
        offline_data=None,
        online_data=None
    )
    mock_kla_processor.preprocess_kla_data.assert_called_once()
    mock_plotter_class.assert_called_once_with(processor=None)
    mock_kla_plotter.plot_kla_data.assert_called_once()


@patch("src.main.DataLoader")
@patch("src.main.DataProcessor")
@patch("src.main.Plotter")
def test_run_kla_workflow_exception(mock_plotter_class, mock_data_processor_class, mock_data_loader_class):
    # Setup mocks
    mock_data_loader = MagicMock()
    mock_data_loader_class.return_value = mock_data_loader
    mock_data_loader.load_kla_data.side_effect = Exception("KLA Loading error")

    # Initialize MainApp
    app = MainApp(offline_file="dummy_offline.txt", online_file="dummy_online.txt")

    # Run the KLA workflow and capture logs
    with patch("src.main.logger") as mock_logger:
        app.run_kla_workflow(kla_file="data/data(kla)/Daten(klA)400rpm 3L.txt")
        mock_logger.error.assert_called_with("An error occurred during the KLA workflow: KLA Loading error")
