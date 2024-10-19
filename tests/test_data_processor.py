# tests/test_data_processor.py

import pytest
import pandas as pd
from unittest.mock import patch

from src.data_processor import DataProcessor

# Sample offline and online data
OFFLINE_DATA = pd.DataFrame({
    'Zeit_BTM': ['12:00:00', '13:00:00'],
    'Zeit_G': ['12:00:00', '13:00:00'],
    'Zeit_E': ['12:00:00', '13:00:00'],
    'BTM': ['1.5', '1.6'],
    'EtOH': ['0.5', '0.6'],
    'Glu': ['2.0', '2.1']
})

ONLINE_DATA = pd.DataFrame({
    'Zeit': ['12:00:00.000', '13:00:00.000'],
    'spH': ['7.0', '7.1'],
    'spO2': ['85', '86'],
    'NStirrer': ['100', '101'],
    'sTR': ['200', '201'],
    'sCO2': ['5', '6'],
    'sO2': ['20', '21'],
    'FAirIn': ['1.2', '1.3'],
    'sVR': ['10', '11'],
    'FGlucose': ['0.5', '0.6']
})

KLA_DATA_RAW = pd.DataFrame({
    'Time': ['2024-01-01 12:00:00', '2024-01-01 13:00:00'],
    'Measurement1': ['1,0', '1,1'],
    'Measurement2': ['2,0', '2,1']
})

KLA_DATA_PROCESSED = pd.DataFrame({
    'Time': pd.to_datetime(['2024-01-01 12:00:00', '2024-01-01 13:00:00'], format='%d.%m.%Y %H:%M:%S', dayfirst=True),
    'Measurement1': [1.0, 1.1],
    'Measurement2': [2.0, 2.1]
})


@pytest.fixture
def data_processor_with_data():
    return DataProcessor(offline_data=OFFLINE_DATA.copy(), online_data=ONLINE_DATA.copy())


@pytest.fixture
def data_processor_without_data():
    return DataProcessor(offline_data=None, online_data=None)


def test_extract_offline_columns_success(data_processor_with_data):
    data_processor_with_data.extract_offline_columns()

    # Assertions
    assert data_processor_with_data.time_biomass.equals(pd.Series(['12:00:00', '13:00:00']))
    assert data_processor_with_data.time_glucose.equals(pd.Series(['12:00:00', '13:00:00']))
    assert data_processor_with_data.time_ethanol.equals(pd.Series(['12:00:00', '13:00:00']))
    assert data_processor_with_data.biomass.equals(pd.Series([1.5, 1.6]))
    assert data_processor_with_data.ethanol.equals(pd.Series([0.5, 0.6]))
    assert data_processor_with_data.glucose.equals(pd.Series([2.0, 2.1]))


def test_extract_offline_columns_missing_offline_data(data_processor_without_data):
    with pytest.raises(ValueError, match="Offline data is not provided."):
        data_processor_without_data.extract_offline_columns()


def test_extract_offline_columns_missing_columns(data_processor_with_data):
    # Remove a required column
    data_processor_with_data.offline_data.drop(columns=['BTM'], inplace=True)

    with pytest.raises(KeyError, match=r"Missing columns in offline data: \['BTM'\]"):
        data_processor_with_data.extract_offline_columns()


def test_calculate_feed_time_success(data_processor_with_data):
    # Ensure 'Zeit_FG' and 'FGlucose' are present
    # Since 'Zeit_FG' is not in ONLINE_DATA, let's add it
    data_processor_with_data.online_data['Zeit_FG'] = ['12:30:00', '13:30:00']
    data_processor_with_data.calculate_feed_time()

    # Assertions
    assert data_processor_with_data.time_feed_glucose_numeric.equals(pd.Series([0.0, 1.0]))
    assert data_processor_with_data.glucose_feed.equals(pd.Series([0.5, 0.6]))


def test_calculate_feed_time_missing_online_data(data_processor_without_data):
    with pytest.raises(ValueError, match="Online data is not provided."):
        data_processor_without_data.calculate_feed_time()


def test_calculate_feed_time_missing_columns(data_processor_with_data):
    # Remove required columns
    data_processor_with_data.online_data.drop(columns=['Zeit_FG', 'FGlucose'], inplace=True)

    with pytest.raises(KeyError, match=r"Missing columns in online data: \['Zeit_FG', 'FGlucose'\]"):
        data_processor_with_data.calculate_feed_time()


def test_get_valid_masks_success(data_processor_with_data):
    # Add 'Zeit_FG' and 'FGlucose' to online_data
    data_processor_with_data.online_data['Zeit_FG'] = ['12:30:00', '13:30:00']
    data_processor_with_data.online_data['FGlucose'] = [0.5, 0.6]
    data_processor_with_data.calculate_feed_time()
    data_processor_with_data.get_valid_masks()

    # Assertions
    assert data_processor_with_data.valid_aeration_mask.equals(pd.Series([True, True]))
    assert data_processor_with_data.valid_stirrer_mask.equals(pd.Series([True, True]))
    assert data_processor_with_data.valid_feed_glucose_mask.equals(pd.Series([True, True]))


def test_get_valid_masks_missing_online_data(data_processor_without_data):
    with pytest.raises(ValueError, match="Online data is not provided."):
        data_processor_without_data.get_valid_masks()


def test_get_valid_masks_missing_columns(data_processor_with_data):
    # Remove required columns
    data_processor_with_data.online_data.drop(columns=['FAirIn', 'NStirrer', 'time_feed_glucose', 'FGlucose'],
                                              inplace=True)

    with pytest.raises(KeyError,
                       match=r"Missing columns in online data for masks: \['FAirIn', 'NStirrer', 'time_feed_glucose', 'FGlucose'\]"):
        data_processor_with_data.get_valid_masks()


def test_preprocess_kla_data_success(data_processor_without_data):
    processed_kla = data_processor_without_data.preprocess_kla_data(KLA_DATA_RAW.copy())

    # Assertions
    pd.testing.assert_frame_equal(processed_kla, KLA_DATA_PROCESSED)


def test_preprocess_kla_data_invalid_times(data_processor_without_data):
    # Add an invalid time entry
    kla_data_invalid = KLA_DATA_RAW.copy()
    kla_data_invalid = kla_data_invalid.append({'Time': 'invalid_time', 'Measurement1': '1,2', 'Measurement2': '2,2'},
                                               ignore_index=True)

    with patch("logging.Logger.warning") as mock_logger_warning:
        processed_kla = data_processor_without_data.preprocess_kla_data(kla_data_invalid)
        # Should log a warning for invalid timestamps
        mock_logger_warning.assert_called_with("1 rows have invalid timestamps.")

    # Assertions
    expected_df = KLA_DATA_PROCESSED.copy()
    pd.testing.assert_frame_equal(processed_kla, expected_df)


def test_preprocess_kla_data_missing_time(data_processor_without_data):
    # Remove 'Time' column
    kla_data_missing_time = KLA_DATA_RAW.copy()
    kla_data_missing_time.drop(columns=['Time'], inplace=True)

    with patch("logging.Logger.error") as mock_logger_error:
        with pytest.raises(KeyError, match="Cannot dropna subset"):
            data_processor_without_data.preprocess_kla_data(kla_data_missing_time)
