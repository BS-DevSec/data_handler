# tests/test_plotter.py

import pytest
from unittest.mock import patch, MagicMock
import pandas as pd

from src.data_processor import DataProcessor
from src.plotter import Plotter

# Sample data for plotting
OFFLINE_DATA = pd.DataFrame({
    'Zeit_BTM': ['12:00:00', '13:00:00'],
    'Zeit_G': ['12:00:00', '13:00:00'],
    'Zeit_E': ['12:00:00', '13:00:00'],
    'BTM': [1.5, 1.6],
    'EtOH': [0.5, 0.6],
    'Glu': [2.0, 2.1]
})

ONLINE_DATA = pd.DataFrame({
    'Zeit': ['12:00:00.000', '13:00:00.000'],
    'spH': [7.0, 7.1],
    'spO2': [85, 86],
    'NStirrer': [100, 101],
    'sTR': [200, 201],
    'sCO2': [5, 6],
    'sO2': [20, 21],
    'FAirIn': [1.2, 1.3],
    'sVR': [10, 11],
    'FGlucose': [0.5, 0.6],
    'time_feed_glucose': [0.0, 1.0],
    'glucose_feed': [0.5, 0.6],
    'valid_feed_glucose_mask': [True, True],
    'valid_aeration_mask': [True, True],
    'valid_stirrer_mask': [True, True]
})

KLA_DATA = pd.DataFrame({
    'Time': pd.to_datetime(['2024-01-01 12:00:00', '2024-01-01 13:00:00']),
    'Measurement1': [1.0, 1.1],
    'Measurement2': [2.0, 2.1]
})


@pytest.fixture
def plotter_with_data():
    processor = DataProcessor(offline_data=OFFLINE_DATA.copy(), online_data=ONLINE_DATA.copy())
    processor.extract_offline_columns()
    processor.calculate_feed_time()
    processor.get_valid_masks()
    return Plotter(processor=processor)


@pytest.fixture
def plotter_without_data():
    return Plotter(processor=None)


def test_plot_data_success(plotter_with_data):
    with patch("matplotlib.pyplot.show") as mock_show, \
            patch("matplotlib.pyplot.tight_layout") as mock_tight_layout, \
            patch("matplotlib.pyplot.subplots") as mock_subplots:
        # Mock subplots
        mock_fig = MagicMock()
        mock_ax1 = MagicMock()
        mock_ax2 = MagicMock()
        mock_ax3 = MagicMock()
        mock_ax4 = MagicMock()
        mock_subplots.return_value = (mock_fig, (mock_ax1, mock_ax2, mock_ax3, mock_ax4))

        # Run plot_data
        plotter_with_data.plot_data()

        # Assertions
        mock_subplots.assert_called_once()
        mock_tight_layout.assert_called_once()
        mock_show.assert_called_once()


def test_plot_data_processor_not_set(plotter_without_data):
    with pytest.raises(ValueError, match=r"DataProcessor is not set. Use set_processor\(\) before plotting\."):
        plotter_without_data.plot_data()


def test_plot_kla_data_success(plotter_without_data, KLA_DATA):
    with patch("matplotlib.pyplot.show") as mock_show, \
            patch("matplotlib.pyplot.tight_layout") as mock_tight_layout, \
            patch("seaborn.set") as mock_sns_set, \
            patch("matplotlib.pyplot.figure") as mock_figure, \
            patch("matplotlib.pyplot.plot") as mock_plot, \
            patch("matplotlib.pyplot.xlabel") as mock_xlabel, \
            patch("matplotlib.pyplot.ylabel") as mock_ylabel, \
            patch("matplotlib.pyplot.title") as mock_title, \
            patch("matplotlib.pyplot.legend") as mock_legend:
        # Run plot_kla_data
        plotter_without_data.plot_kla_data(KLA_DATA)

        # Assertions
        mock_sns_set.assert_called_once_with(style="darkgrid")
        mock_figure.assert_called_once_with(figsize=(14, 8))
        assert mock_plot.call_count == 3  # Three columns plotted
        mock_xlabel.assert_called_once_with('Time')
        mock_ylabel.assert_called_once_with('Measurements')
        mock_title.assert_called_once_with('Measurement Data Over Time')
        mock_legend.assert_called_once()
        mock_tight_layout.assert_called_once()
        mock_show.assert_called_once()


def test_plot_kla_data_missing_columns(plotter_without_data, KLA_DATA):
    # Remove a column from KLA_DATA
    kla_data_missing_col = KLA_DATA.copy()
    kla_data_missing_col.drop(columns=['Measurement2'], inplace=True)

    with patch("logging.Logger.warning") as mock_logger_warning, \
            patch("matplotlib.pyplot.show") as mock_show, \
            patch("matplotlib.pyplot.tight_layout") as mock_tight_layout, \
            patch("seaborn.set") as mock_sns_set, \
            patch("matplotlib.pyplot.figure") as mock_figure, \
            patch("matplotlib.pyplot.plot") as mock_plot, \
            patch("matplotlib.pyplot.xlabel") as mock_xlabel, \
            patch("matplotlib.pyplot.ylabel") as mock_ylabel, \
            patch("matplotlib.pyplot.title") as mock_title, \
            patch("matplotlib.pyplot.legend") as mock_legend:
        # Run plot_kla_data
        plotter_without_data.plot_kla_data(kla_data_missing_col)

        # Assertions
        mock_sns_set.assert_called_once_with(style="darkgrid")
        mock_figure.assert_called_once_with(figsize=(14, 8))
        assert mock_plot.call_count == 2  # Two columns plotted
        mock_logger_warning.assert_called_once_with("Column 'FO2In' not found in KLA data and will be skipped.")
        mock_xlabel.assert_called_once_with('Time')
        mock_ylabel.assert_called_once_with('Measurements')
        mock_title.assert_called_once_with('Measurement Data Over Time')
        mock_legend.assert_called_once()
        mock_tight_layout.assert_called_once()
        mock_show.assert_called_once()
