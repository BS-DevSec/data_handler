# config_loader.py
import yaml
from pathlib import Path
from typing import Any, Dict, Optional

class ConfigLoader:
    """Class to load and provide access to configuration settings."""

    def __init__(self, config_path: Path):
        """
        Initialize the ConfigLoader with the path to the configuration file.

        :param config_path: Path to the config.yaml file.
        """
        self.config = self._load_config(config_path)
        self.validate_config()  # Optional: Validate configurations upon loading

    @staticmethod
    def _load_config(config_path: Path) -> Dict[str, Any]:
        """
        Load the YAML configuration file.

        :param config_path: Path to the config.yaml file.
        :return: Dictionary containing configuration parameters.
        """
        try:
            with open(config_path, 'r') as file:
                config = yaml.safe_load(file)
            return config
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found at {config_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing the configuration file: {e}")

    def get(self, section: str, key: Optional[str] = None, default=None):
        """
        Retrieve a configuration value or an entire section.

        :param section: Section in the YAML file.
        :param key: Key within the section (optional).
        :param default: Default value if key or section is not found.
        :return: Configuration value or section dictionary.
        """
        if key is None:
            return self.config.get(section, default)
        return self.config.get(section, {}).get(key, default)

    def validate_config(self):
        """
        Validate the presence of essential configuration sections and keys.

        Raises:
            ValueError: If required sections or keys are missing.
        """
        required_sections = ['data_loader', 'data_processor', 'plotter', 'logging']
        for section in required_sections:
            if section not in self.config:
                raise ValueError(f"Missing required configuration section: '{section}'")

        # Example: Validate specific keys within sections
        data_loader_keys = ['offline_file', 'online_file', 'kla_dir', 'column_separator', 'decimal_separator', 'encoding']
        for key in data_loader_keys:
            if key not in self.config['data_loader']:
                raise ValueError(f"Missing required key '{key}' in 'data_loader' section")

        data_processor_keys = ['online_numeric_columns']
        for key in data_processor_keys:
            if key not in self.config['data_processor']:
                raise ValueError(f"Missing required key '{key}' in 'data_processor' section")

        plotter_keys = ['figsize_main', 'figsize_kla', 'style', 'plot_dir', 'dpi']
        for key in plotter_keys:
            if key not in self.config['plotter']:
                raise ValueError(f"Missing required key '{key}' in 'plotter' section")

        logging_keys = ['level', 'format', 'handlers']
        for key in logging_keys:
            if key not in self.config['logging']:
                raise ValueError(f"Missing required key '{key}' in 'logging' section")
