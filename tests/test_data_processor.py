import pandas as pd
from data_processor import DataProcessor


# Test extract_offline_columns
def test_extract_offline_columns():
    offline_data = pd.DataFrame({
        'Zeit_BTM': ['12:00:00', '13:00:00'],
        'Zeit_G': ['12:30:00', '13:30:00'],
        'Zeit_E': ['12:15:00', '13:15:00'],
        'BTM': [10, 20],
        'EtOH': [5, 15],
        'Glu': [100, 200]
    })

    processor = DataProcessor(offline_data, None)
    processor.extract_offline_columns()

    assert processor.biomass is not None


# Test calculate_feed_time
def test_calculate_feed_time():
    online_data = pd.DataFrame({'Zeit_FG': ['12:00:00', '13:00:00'], 'FGlucose': [100, 200]})

    processor = DataProcessor(None, online_data)
    processor.calculate_feed_time()

    assert processor.time_feed_glucose_numeric is not None


# Test valid masks generation
def test_get_valid_masks():
    online_data = pd.DataFrame({
        'FAirIn': [1, None, 2],
        'NStirrer': [100, 150, None],
        'time_feed_glucose': [1.0, None, 2.0],
        'FGlucose': [None, 10.0, 15.0]
    })

    processor = DataProcessor(None, online_data)
    processor.get_valid_masks()

    assert processor.valid_aeration_mask.sum() == 2
