# data_processor.py
import logging
from typing import Optional

import pandas as pd

# Configure logging
logger = logging.getLogger(__name__)

class DataProcessor:
    """Class to process data for plotting and analysis."""

    def __init__(self, offline_data: Optional[pd.DataFrame], online_data: Optional[pd.DataFrame]):
        """
        Initialize the DataProcessor with offline and online data.

        :param offline_data: DataFrame containing offline data.
        :param online_data: DataFrame containing online data.
        """
        self.offline_data = offline_data
        self.online_data = online_data

        # Initialize processed attributes
        self.time_biomass: Optional[pd.Series] = None
        self.time_glucose: Optional[pd.Series] = None
        self.time_ethanol: Optional[pd.Series] = None
        self.biomass: Optional[pd.Series] = None
        self.ethanol: Optional[pd.Series] = None
        self.glucose: Optional[pd.Series] = None

        self.time_feed_glucose_numeric: Optional[pd.Series] = None
        self.glucose_feed: Optional[pd.Series] = None

        self.valid_aeration_mask: Optional[pd.Series] = None
        self.valid_stirrer_mask: Optional[pd.Series] = None
        self.valid_feed_glucose_mask: Optional[pd.Series] = None

    def extract_offline_columns(self) -> None:
        """
        Extract and convert relevant columns from offline data.
        """
        if self.offline_data is None:
            logger.error("Offline data is not provided.")
            raise ValueError("Offline data is not provided.")

        required_columns = ['Zeit_BTM', 'Zeit_G', 'Zeit_E', 'BTM', 'EtOH', 'Glu']
        missing_columns = [col for col in required_columns if col not in self.offline_data.columns]
        if missing_columns:
            logger.error(f"Missing columns in offline data: {missing_columns}")
            raise KeyError(f"Missing columns in offline data: {missing_columns}")

        logger.info("Extracting and converting columns from offline data.")
        self.time_biomass = self.offline_data['Zeit_BTM']
        self.time_glucose = self.offline_data['Zeit_G']
        self.time_ethanol = self.offline_data['Zeit_E']
        self.biomass = pd.to_numeric(self.offline_data['BTM'], errors='coerce')
        self.ethanol = pd.to_numeric(self.offline_data['EtOH'], errors='coerce')
        self.glucose = pd.to_numeric(self.offline_data['Glu'], errors='coerce')
        logger.info("Offline columns extracted and converted successfully.")

    def calculate_feed_time(self) -> None:
        """
        Calculate the numeric feed time for glucose feeds in online data.
        """
        if self.online_data is None:
            logger.error("Online data is not provided.")
            raise ValueError("Online data is not provided.")

        required_columns = ['Zeit_FG', 'FGlucose']
        missing_columns = [col for col in required_columns if col not in self.online_data.columns]
        if missing_columns:
            logger.error(f"Missing columns in online data: {missing_columns}")
            raise KeyError(f"Missing columns in online data: {missing_columns}")

        logger.info("Calculating feed time for glucose feeds.")
        try:
            self.online_data['time_feed_glucose'] = pd.to_datetime(
                self.online_data['Zeit_FG'],
                format='%H:%M:%S',
                errors='coerce'
            )
            start_time_feed_glucose = self.online_data['time_feed_glucose'].min()
            self.time_feed_glucose_numeric = (
                self.online_data['time_feed_glucose'] - start_time_feed_glucose
            ).dt.total_seconds() / 3600  # Convert to hours
            self.glucose_feed = pd.to_numeric(self.online_data['FGlucose'], errors='coerce')
            logger.info("Feed time calculated successfully.")
        except Exception as e:
            logger.error(f"Error calculating feed time: {e}")
            raise

    def get_valid_masks(self) -> None:
        """
        Create masks for valid values in key columns.
        """
        if self.online_data is None:
            logger.error("Online data is not provided.")
            raise ValueError("Online data is not provided.")

        required_columns = ['FAirIn', 'NStirrer', 'time_feed_glucose', 'FGlucose']
        missing_columns = [col for col in required_columns if col not in self.online_data.columns]
        if missing_columns:
            logger.error(f"Missing columns in online data for masks: {missing_columns}")
            raise KeyError(f"Missing columns in online data for masks: {missing_columns}")

        logger.info("Creating valid masks for online data.")
        self.valid_aeration_mask = ~self.online_data['FAirIn'].isnull()
        self.valid_stirrer_mask = ~self.online_data['NStirrer'].isnull()
        self.valid_feed_glucose_mask = (
            ~self.online_data['time_feed_glucose'].isnull() &
            ~self.online_data['FGlucose'].isnull()
        )
        logger.info("Valid masks created successfully.")

    def preprocess_kla_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Perform additional data cleaning for KLA dataset.

        :param df: DataFrame containing KLA data.
        :return: Cleaned DataFrame.
        """
        logger.info("Preprocessing KLA data.")
        try:
            df.columns = df.columns.str.strip()
            df['Time'] = df['Time'].astype(str).str.strip()
            df['Time'] = pd.to_datetime(
                df['Time'],
                format='%d.%m.%Y %H:%M:%S',
                errors='coerce',
                dayfirst=True
            )

            num_invalid_times = df['Time'].isna().sum()
            if num_invalid_times > 0:
                logger.warning(f"{num_invalid_times} rows have invalid timestamps.")

            df = df.dropna(subset=['Time']).reset_index(drop=True)

            numeric_columns = df.columns.drop('Time')
            for col in numeric_columns:
                if df[col].dtype == object:
                    df[col] = pd.to_numeric(df[col].str.replace(',', '.'), errors='coerce')

            logger.info("KLA data preprocessed successfully.")
            return df
        except Exception as e:
            logger.error(f"Error preprocessing KLA data: {e}")
            raise
