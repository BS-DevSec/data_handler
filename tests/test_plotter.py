from unittest.mock import patch, MagicMock
import pandas as pd
import pytest
from plotter import Plotter
import numpy as np
import matplotlib.axes


@pytest.fixture
def mock_processor():
    processor = MagicMock()
    processor.time_glucose = [1, 2, 3]
    processor.glucose = [10, 20, 30]
    processor.time_biomass = [1, 2, 3]
    processor.biomass = [5, 15, 25]
    processor.time_ethanol = [1, 2, 3]
    processor.ethanol = [2, 4, 6]
    processor.online_data = pd.DataFrame({
        'time': [1, 2, 3],
        'sCO2': [10, 20, 30],
        'sO2': [15, 25, 35],
        'spO2': [18, 28, 38],
        'NStirrer': [100, 200, 300],
        'FAirIn': [1, 2, 3],
        'FGlucose': [10, 20, 30],
        'sVR': [50, 100, 150],
        'spH': [7.1, 7.2, 7.3]
    })
    processor.valid_feed_glucose_mask = np.array([True, True, True])  # Use NumPy array for boolean masking
    processor.time_feed_glucose_numeric = np.array([1, 2, 3])  # Use NumPy array for numeric values
    processor.glucose_feed = np.array([0.5, 1.0, 1.5])  # Use NumPy array for glucose feed
    processor.valid_stirrer_mask = [True, True, True]
    processor.valid_aeration_mask = [True, True, True]
    return processor


@pytest.fixture
def plotter(mock_processor):
    config = {'plot_dir': '/some/fake/path'}
    return Plotter(processor=mock_processor, config=config)


def test_plot_data_success(plotter):
    # Mock axes with and without legend data
    mock_ax1 = MagicMock(spec=matplotlib.axes.Axes)
    mock_ax1.get_legend_handles_labels.return_value = (['handle1'], ['Glucose'])

    mock_ax2 = MagicMock(spec=matplotlib.axes.Axes)
    mock_ax2.get_legend_handles_labels.return_value = (['handle2'], ['CO2'])

    mock_ax3 = MagicMock(spec=matplotlib.axes.Axes)
    mock_ax3.get_legend_handles_labels.return_value = (['handle3'], ['spO2'])

    mock_ax4 = MagicMock(spec=matplotlib.axes.Axes)
    mock_ax4.get_legend_handles_labels.return_value = (['handle4'], ['Volume'])

    mock_ax1y2 = MagicMock(spec=matplotlib.axes.Axes)
    mock_ax1y2.get_legend_handles_labels.return_value = (['handle1y2'], ['Biomass', 'Ethanol'])

    mock_ax2y2 = MagicMock(spec=matplotlib.axes.Axes)
    mock_ax2y2.get_legend_handles_labels.return_value = (['handle2y2'], ['O2'])

    mock_ax3y2 = MagicMock(spec=matplotlib.axes.Axes)
    mock_ax3y2.get_legend_handles_labels.return_value = (['handle3y2'], ['Glucose Feed'])

    mock_ax4y2 = MagicMock(spec=matplotlib.axes.Axes)
    mock_ax4y2.get_legend_handles_labels.return_value = (['handle4y2'], ['Stirrer Speed'])

    # Set up twin axes
    mock_ax1.twinx.return_value = mock_ax1y2
    mock_ax2.twinx.return_value = mock_ax2y2
    mock_ax3.twinx.return_value = mock_ax3y2
    mock_ax4.twinx.return_value = mock_ax4y2

    # Assuming plt.subplots(4, ...) returns a figure and an array of 4 axes
    with patch('plotter.plt.subplots', return_value=(MagicMock(), np.array([mock_ax1, mock_ax2, mock_ax3, mock_ax4]))):
        with patch('plotter.plt.savefig'), patch('plotter.plt.show'):
            plotter.plot_data()

    # Ensure all mocks return a tuple of two lists
    for ax in [mock_ax1, mock_ax2, mock_ax3, mock_ax4, mock_ax1y2, mock_ax2y2, mock_ax3y2, mock_ax4y2]:
        handles, labels = ax.get_legend_handles_labels()
        assert isinstance(handles, list)
        assert isinstance(labels, list)
