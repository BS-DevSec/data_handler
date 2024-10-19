# main.py
import logging
from pathlib import Path
from typing import Optional, Any, Dict
import glob

from config_loader import ConfigLoader
from data_loader import DataLoader
from data_processor import DataProcessor
from plotter import Plotter


def setup_logging(logging_config: Dict[str, Any]) -> None:
    """
    Configure logging based on the provided configuration.

    :param logging_config: Dictionary containing logging configuration.
    """
    level_str = logging_config.get('level', 'INFO').upper()
    level = getattr(logging, level_str, logging.INFO)
    format_str = logging_config.get('format', '%(asctime)s [%(levelname)s] %(name)s: %(message)s')
    handlers = []
    for handler in logging_config.get('handlers', []):
        if handler.get('type') == 'stream':
            handlers.append(logging.StreamHandler())
        elif handler.get('type') == 'file':
            filename = handler.get('filename', 'application.log')
            handlers.append(logging.FileHandler(filename))
        # Add more handler types if needed

    logging.basicConfig(
        level=level,
        format=format_str,
        handlers=handlers
    )


logger = logging.getLogger(__name__)


class MainApp:
    """Main application class to orchestrate data loading, processing, and plotting."""

    def __init__(self, config: ConfigLoader, project_root: Path):
        """
        Initialize the MainApp with configuration settings and project root.

        :param config: Instance of ConfigLoader containing configuration parameters.
        :param project_root: Path object representing the project root directory.
        """
        self.config = config
        self.data_loader = DataLoader(config, project_root)
        self.data_processor: Optional[DataProcessor] = None
        self.plotter: Optional[Plotter] = None

    def run(self) -> None:
        """
        Execute the main workflow: load data, process it, and generate plots.
        """
        logger.info("Starting main workflow.")
        try:
            # Step 1: Load and process data
            self.data_loader.load_data()
            self.data_loader.process_online_time_column()
            online_numeric_columns = self.config.get('data_processor', 'online_numeric_columns', [])
            self.data_loader.convert_columns_to_numeric(
                online_numeric_columns,
                dataset='online'
            )

            # Step 2: Initialize data processor and extract data
            self.data_processor = DataProcessor(
                offline_data=self.data_loader.offline_data,
                online_data=self.data_loader.online_data
            )
            self.data_processor.extract_offline_columns()
            self.data_processor.calculate_feed_time()
            self.data_processor.get_valid_masks()

            # Step 3: Initialize plotter with plot_dir and generate plots
            plotter_config = self.config.get('plotter')
            self.plotter = Plotter(
                processor=self.data_processor,
                config=plotter_config
            )
            self.plotter.plot_data()

            logger.info("Main workflow completed successfully.")
        except Exception as e:
            logger.error(f"An error occurred during the main workflow: {e}")

    def run_kla_workflow(self, kla_file: Path) -> None:
        """
        Execute the KLA workflow: load KLA data, preprocess it, and generate plots.

        :param kla_file: Path to the KLA data file.
        """
        logger.info(f"Starting KLA workflow for file: {kla_file.name}")
        try:
            # Step 1: Load KLA data
            kla_data = self.data_loader.load_kla_data(str(kla_file))

            # Step 2: Preprocess the KLA data
            # For KLA data, we don't need offline/online data
            kla_processor = DataProcessor(offline_data=None, online_data=None)
            kla_data = kla_processor.preprocess_kla_data(kla_data)

            # Step 3: Initialize plotter with plot_dir and plot KLA data
            plotter_config = self.config.get('plotter')
            kla_plotter = Plotter(
                config=plotter_config
            )
            kla_plotter.plot_kla_data(kla_data, kla_filename=kla_file.stem)

            logger.info(f"KLA workflow completed successfully for file: {kla_file.name}")
        except Exception as e:
            logger.error(f"An error occurred during the KLA workflow for file {kla_file.name}: {e}")


def main():
    # Determine the absolute path to the project root
    script_path = Path(__file__).resolve()
    project_root = script_path.parent.parent  # Adjust based on your project structure

    # Define the path to the configuration file
    config_path = project_root / 'config.yaml'

    # Load the configuration
    config = ConfigLoader(config_path)

    # Setup logging based on configuration
    logging_config = config.get('logging')
    setup_logging(logging_config)

    # Define paths to the data files relative to the project root
    data_loader_config = config.get('data_loader')
    offline_file_path = project_root / data_loader_config.get('offline_file', '')
    online_file_path = project_root / data_loader_config.get('online_file', '')
    kla_dir_path = project_root / data_loader_config.get('kla_dir', 'data/data(kla)/')

    # Define the plot directory relative to the project root
    plot_dir_path = project_root / config.get('plotter', 'plot_dir', 'plot')

    # Check if the main data files exist before proceeding
    for file_path in [offline_file_path, online_file_path]:
        if not file_path.is_file():
            logger.error(f"Required file not found: {file_path.resolve()}")
            return  # Exit the program if any file is missing

    # Check if the KLA directory exists
    if not kla_dir_path.is_dir():
        logger.error(f"KLA data directory not found: {kla_dir_path.resolve()}")
        return  # Exit the program if KLA directory is missing

    # Initialize and run the main application
    app = MainApp(config, project_root)
    app.run()

    # Iterate over all KLA data files and process them
    kla_files = sorted(kla_dir_path.glob('*.txt'))  # Adjust the pattern if needed

    if not kla_files:
        logger.warning(f"No KLA data files found in directory: {kla_dir_path.resolve()}")
    else:
        for kla_file in kla_files:
            app.run_kla_workflow(kla_file=kla_file)


if __name__ == "__main__":
    main()
