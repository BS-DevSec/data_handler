from main import MainApp
from unittest.mock import patch


# Test main workflow
@patch('data_loader.DataLoader.load_data')
@patch('data_loader.DataLoader.process_online_time_column')
@patch('data_loader.DataLoader.convert_columns_to_numeric')
@patch('data_processor.DataProcessor.extract_offline_columns')
@patch('data_processor.DataProcessor.calculate_feed_time')
@patch('data_processor.DataProcessor.get_valid_masks')
@patch('plotter.Plotter.plot_data')
def test_run(mock_load_data, mock_process_time, mock_convert, mock_extract, mock_calc, mock_masks, mock_plot):
    app = MainApp('offline_file.txt', 'online_file.txt')
    app.run()

    mock_load_data.assert_called_once()
    mock_process_time.assert_called_once()
    mock_convert.assert_called_once()
    mock_extract.assert_called_once()
    mock_calc.assert_called_once()
    mock_masks.assert_called_once()
    mock_plot.assert_called_once()
