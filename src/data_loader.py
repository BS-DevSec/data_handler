from io import StringIO
import logging
from typing import List, Optional, Tuple

import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Constants
NA_VALUES = ['#NAN', 'NaN', 'nan', '#DIV/0!', 'inf', '-inf']
COLUMN_SEPARATOR = '\t'
DECIMAL_SEPARATOR = ','


class DataLoader:
    """Class to handle loading and processing of offline, online, and KLA data."""

    def __init__(self, offline_file: str, online_file: str):
        """
        Initialize the DataLoader with paths to offline and online data files.

        :param offline_file: Path to the offline data file.
        :param online_file: Path to the online data file.
        """
        self.offline_file = offline_file
        self.online_file = online_file
        self.offline_data: Optional[pd.DataFrame] = None
        self.online_data: Optional[pd.DataFrame] = None

    def load_data(self) -> None:
        """
        Load offline and online data from their respective files into pandas DataFrames.
        """
        try:
            logger.info(f"Loading offline data from {self.offline_file}")
            self.offline_data = pd.read_csv(
                self.offline_file,
                sep=COLUMN_SEPARATOR,
                na_values=NA_VALUES,
                decimal=DECIMAL_SEPARATOR
            )
            logger.info("Offline data loaded successfully.")

            logger.info(f"Loading online data from {self.online_file}")
            self.online_data = pd.read_csv(
                self.online_file,
                sep=COLUMN_SEPARATOR,
                na_values=NA_VALUES,
                decimal=DECIMAL_SEPARATOR,
                encoding="utf-8"
            )
            logger.info("Online data loaded successfully.")
        except FileNotFoundError as e:
            logger.error(f"File not found: {e.filename}")
            raise
        except pd.errors.ParserError as e:
            logger.error(f"Error parsing CSV file: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error while loading data: {e}")
            raise

    def process_online_time_column(self) -> None:
        """
        Clean the 'Zeit' column in online data and convert it to a datetime object.
        Assumes the presence of a 'Zeit' column in the online_data DataFrame.
        """
        if self.online_data is None:
            logger.error("Online data is not loaded. Call load_data() first.")
            raise ValueError("Online data is not loaded.")

        if 'Zeit' not in self.online_data.columns:
            logger.error("'Zeit' column not found in online data.")
            raise KeyError("'Zeit' column not found in online data.")

        logger.info("Processing 'Zeit' column in online data.")
        try:
            self.online_data['time'] = self.online_data['Zeit'].str.split('.').str[0]
            self.online_data['time'] = pd.to_datetime(
                self.online_data['time'],
                format='%H:%M:%S',
                errors='coerce'
            )
            logger.info("'Zeit' column processed successfully.")
        except Exception as e:
            logger.error(f"Error processing 'Zeit' column: {e}")
            raise

    def convert_columns_to_numeric(self, columns: List[str], dataset: str = 'online') -> None:
        """
        Convert specified columns in the selected dataset to numeric types.

        :param columns: List of column names to convert.
        :param dataset: Which dataset to convert columns for ('online' or 'offline').
        """
        data = self._get_dataset(dataset)
        if data is None:
            logger.error(f"{dataset.capitalize()} data is not loaded.")
            raise ValueError(f"{dataset.capitalize()} data is not loaded.")

        logger.info(f"Converting columns {columns} to numeric in {dataset} data.")
        for column in columns:
            if column not in data.columns:
                logger.warning(f"Column '{column}' not found in {dataset} data. Skipping.")
                continue
            try:
                data[column] = pd.to_numeric(data[column], errors='coerce')
                logger.info(f"Column '{column}' converted to numeric.")
            except Exception as e:
                logger.error(f"Error converting column '{column}' to numeric: {e}")
                raise

    def find_data_start(self, file_path: str, delimiter: str = ';') -> Tuple[int, Optional[str], Optional[str]]:
        """
        Finds the line where the actual data begins in the specified file.

        :param file_path: Path to the file to search.
        :param delimiter: Delimiter used in the file.
        :return: Tuple containing the data start line number, header line, and units line.
        """
        logger.info(f"Finding data start in file: {file_path}")
        try:
            with open(file_path, 'r', encoding='utf-16-le') as file:
                for i, line in enumerate(file):
                    if line.startswith('Time'):
                        header_line = line.strip()
                        units_line = next(file, '').strip()
                        logger.info(f"Data starts at line {i + 2}")
                        return i + 2, header_line, units_line
            logger.warning("Header with 'Time' was not found.")
            return 0, None, None
        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            raise
        except Exception as e:
            logger.error(f"Error while finding data start: {e}")
            raise

    def load_kla_data(self, file_path: str) -> pd.DataFrame:
        """
        Loads and processes data from the KLA dataset.

        :param file_path: Path to the KLA data file.
        :return: DataFrame containing the loaded KLA data.
        """
        logger.info(f"Loading KLA data from {file_path}")
        data_start, header_line, units_line = self.find_data_start(file_path)

        if header_line is None:
            logger.error("Header with 'Time' was not found.")
            raise ValueError("Header with 'Time' was not found.")

        columns = [col.strip() for col in header_line.split(';') if col.strip()]
        logger.debug(f"Columns found: {columns}")

        try:
            with open(file_path, 'r', encoding='utf-16-le') as file:
                for _ in range(data_start):
                    next(file)
                data_str = ''.join(file.readlines())

            kla_data = pd.read_csv(
                StringIO(data_str),
                delimiter=';',
                decimal=',',
                names=columns,
                usecols=columns,
                engine='python',
                skip_blank_lines=True
            )
            logger.info("KLA data loaded successfully.")
            return kla_data
        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            raise
        except pd.errors.ParserError as e:
            logger.error(f"Error parsing KLA CSV file: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error while loading KLA data: {e}")
            raise

    def _get_dataset(self, dataset: str) -> Optional[pd.DataFrame]:
        """
        Helper method to retrieve the specified dataset.

        :param dataset: 'online' or 'offline'.
        :return: The corresponding DataFrame or None.
        """
        if dataset.lower() == 'online':
            return self.online_data
        elif dataset.lower() == 'offline':
            return self.offline_data
        else:
            logger.error("Dataset must be either 'online' or 'offline'.")
            raise ValueError("Dataset must be either 'online' or 'offline'.")
