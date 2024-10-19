import pytest
import pandas as pd
from data_processor import DataProcessor


@pytest.fixture
def processor():
    offline_data = pd.DataFrame({
        'Zeit_BTM': ['12:00', '13:00'],
        'Zeit_G': ['12:00', '13:00'],  # Add missing Zeit_G column
        'Zeit_E': ['12:00', '13:00'],  # Add missing Zeit_E column
        'BTM': ['1.0', '2.0'],
        'EtOH': ['0.1', '0.2'],
        'Glu': ['10', '20'],
    })
    online_data = pd.DataFrame({
        'Zeit_FG': ['12:00', '13:00'],
        'FGlucose': ['5.0', '6.0']
    })
    return DataProcessor(offline_data=offline_data, online_data=online_data)


def test_extract_offline_columns_success(processor):
    processor.extract_offline_columns()

    assert processor.biomass is not None
    assert processor.ethanol is not None
    assert processor.glucose is not None


def test_extract_offline_columns_missing_columns(processor):
    processor.offline_data.drop(columns=['BTM'], inplace=True)

    with pytest.raises(KeyError):
        processor.extract_offline_columns()


def test_calculate_feed_time_success(processor):
    processor.calculate_feed_time()

    assert processor.time_feed_glucose_numeric is not None
    assert processor.glucose_feed is not None


def test_calculate_feed_time_missing_columns(processor):
    processor.online_data.drop(columns=['Zeit_FG'], inplace=True)

    with pytest.raises(KeyError):
        processor.calculate_feed_time()


def test_get_valid_masks_success(processor):
    processor.online_data = pd.DataFrame({
        'FAirIn': [1, 2],
        'NStirrer': [100, 200],
        'time_feed_glucose': ['12:00', '13:00'],
        'FGlucose': [10, 20]
    })

    processor.get_valid_masks()

    assert processor.valid_aeration_mask is not None
    assert processor.valid_stirrer_mask is not None
    assert processor.valid_feed_glucose_mask is not None


def test_preprocess_kla_data_success(processor):
    kla_data = pd.DataFrame({
        'Time': ['01.01.2020 00:00:00', '02.01.2020 00:00:00'],
        'SomeColumn': ['1,0', '2,0']
    })

    processed_data = processor.preprocess_kla_data(kla_data)

    assert 'Time' in processed_data.columns
    assert pd.api.types.is_numeric_dtype(processed_data['SomeColumn'])
