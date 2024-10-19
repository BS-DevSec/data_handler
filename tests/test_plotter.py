import matplotlib
import pandas as pd
from plotter import Plotter
from data_processor import DataProcessor

# Switch to a non-interactive backend
matplotlib.use('Agg')


# Test plot_data without actual plotting
def test_plot_data(mocker):
    mocker.patch('matplotlib.pyplot.show')  # Prevent actual plot display

    # Mock valid data for testing
    online_data = pd.DataFrame({
        'time': [1, 2],
        'spO2': [90, 95],
        'sCO2': [5, 6],
        'sVR': [10, 12],
        'FAirIn': [1, 2],
        'spH': [7.0, 7.2],
        'NStirrer': [100, 150],
        'FGlucose': [0.5, 0.7],
        'Zeit_FG': ['12:00:00', '13:00:00'],
        'sO2': [21, 22]  # Add this column for plotting
    })

    # Simulating valid time series data for glucose, biomass, and ethanol
    offline_data = pd.DataFrame({
        'Zeit_BTM': [1, 2],
        'Zeit_G': [1, 2],
        'Zeit_E': [1, 2],
        'BTM': [10, 20],
        'EtOH': [5, 15],
        'Glu': [100, 200]
    })

    processor = DataProcessor(offline_data, online_data)
    processor.extract_offline_columns()
    processor.calculate_feed_time()
    processor.get_valid_masks()

    plotter = Plotter(processor)
    plotter.plot_data()

# Test KLA plot
def test_plot_kla_data(mocker):
    mocker.patch('matplotlib.pyplot.show')  # Prevent actual plot display
    kla_data = pd.DataFrame({'Time': pd.to_datetime(['2021-03-12 14:00:00', '2021-03-12 15:00:00']), 'spO2': [90, 95]})

    plotter = Plotter()
    plotter.plot_kla_data(kla_data)