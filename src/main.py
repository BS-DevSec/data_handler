# main.py
import logging
from pathlib import Path
from typing import Optional

from data_loader import DataLoader
from data_processor import DataProcessor
from plotter import Plotter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MainApp:
    """Main application class to orchestrate data loading, processing, and plotting."""

    def __init__(self, offline_file: Path, online_file: Path, plot_dir: Path):
        """
        Initialize the MainApp with paths to offline and online data files.

        :param offline_file: Path to the offline data file.
        :param online_file: Path to the online data file.
        :param plot_dir: Path to the directory where plots will be saved.
        """
        self.data_loader = DataLoader(str(offline_file), str(online_file))
        self.data_processor: Optional[DataProcessor] = None
        self.plotter: Optional[Plotter] = None
        self.plot_dir = plot_dir

    def run(self) -> None:
        """
        Execute the main workflow: load data, process it, and generate plots.
        """
        logger.info("Starting main workflow.")
        try:
            # Step 1: Load and process data
            self.data_loader.load_data()
            self.data_loader.process_online_time_column()
            self.data_loader.convert_columns_to_numeric(
                ['spH', 'spO2', 'NStirrer', 'sTR', 'sCO2', 'sO2', 'FAirIn', 'sVR', 'FGlucose'],
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
            self.plotter = Plotter(processor=self.data_processor, plot_dir=self.plot_dir)
            self.plotter.plot_data()

            logger.info("Main workflow completed successfully.")
        except Exception as e:
            logger.error(f"An error occurred during the main workflow: {e}")

    def run_kla_workflow(self, kla_file: Path) -> None:
        """
        Execute the KLA workflow: load KLA data, preprocess it, and generate plots.

        :param kla_file: Path to the KLA data file.
        """
        logger.info("Starting KLA workflow.")
        try:
            # Step 1: Load KLA data
            kla_data = self.data_loader.load_kla_data(str(kla_file))

            # Step 2: Preprocess the KLA data
            # For KLA data, we don't need offline/online data
            kla_processor = DataProcessor(offline_data=None, online_data=None)
            kla_data = kla_processor.preprocess_kla_data(kla_data)

            # Step 3: Initialize plotter with plot_dir and plot KLA data
            kla_plotter = Plotter(plot_dir=self.plot_dir)
            kla_plotter.plot_kla_data(kla_data)

            logger.info("KLA workflow completed successfully.")
        except Exception as e:
            logger.error(f"An error occurred during the KLA workflow: {e}")

def main():
    # Determine the absolute path to the project root
    script_path = Path(__file__).resolve()
    project_root = script_path.parent.parent  # Assuming src is directly under project root

    # Define paths to the data files relative to the project root
    offline_file_path = project_root / 'data' / 'hk18' / 'offlindata_HK_45.txt'
    online_file_path = project_root / 'data' / 'hk18' / 'onlindata_HK_453.txt'
    kla_file_path = project_root / 'data' / 'data(kla)' / 'Daten(klA)400rpm 3L.txt'

    # Define the plot directory relative to the project root
    plot_dir_path = project_root / 'plots'

    # Check if the data files exist before proceeding
    for file_path in [offline_file_path, online_file_path, kla_file_path]:
        if not file_path.is_file():
            logger.error(f"Required file not found: {file_path}")
            return  # Exit the program if any file is missing

    # Initialize and run the main application
    app = MainApp(
        offline_file=offline_file_path,
        online_file=online_file_path,
        plot_dir=plot_dir_path
    )
    app.run()
    app.run_kla_workflow(kla_file=kla_file_path)

if __name__ == "__main__":
    main()
