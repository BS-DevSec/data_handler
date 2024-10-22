
# Data Handler Project

This project is designed to load, process, and visualize offline, online, and KLA data for analysis, particularly for biochemical and fermentation simulations. It includes modules for configuration loading, data processing, and plotting. The project also contains unit tests to ensure the robustness of each component.

## Table of Contents
- [Installation](#installation)
- [Project Structure](#project-structure)
- [Usage](#usage)
- [Configuration](#configuration)
- [Tests](#tests)
- [Requirements](#requirements)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/data_handler.git
   cd data_handler
   ```

2. Install the required dependencies using `pip`:
   ```bash
   pip install -r requirements.txt
   ```

3. Alternatively, you can install the package using `setup.py`:
   ```bash
   python setup.py install
   ```
4. Automated installing process
 - Setup Virtual Environment and Install Dependencies

   This project uses a virtual environment for managing dependencies. You can automatically set up a virtual environment and install all the necessary dependencies by using the `setup_and_run.py` script.

   #### Steps:
   1. Ensure that Python is installed on your machine.
   2. Run the following command to execute the script:

      - **On Windows**:
        ```bash
        python setup_and_run.py
        ```

      - **On Linux/Mac**:
        ```bash
        python3 setup_and_run.py
        ```

   The script will:
      - Create a virtual environment (if not already created).
      - Install all dependencies from `requirements.txt`.
      - Run the main Python application located at `src/main.py`.

## Project Structure

```
data_handler/
├── data/                         # Contains the data files used in the analysis
│   ├── data(kla)/                # KLA data files
│   ├── excel/                    # Excel files to be converted to TXT
│   └── hk18/                     # Offline and online data files for HK18
├── logs/                         # Application logs
├── plots/                        # Generated plot images
├── src/                          # Source code for data loading, processing, and plotting
│   ├── config_loader.py          # Configuration loading module
│   ├── data_loader.py            # Data loading and pre-processing module
│   ├── data_processor.py         # Data processing for analysis and plotting
│   ├── plotter.py                # Handles plotting using matplotlib and seaborn
│   └── main.py                   # Main entry point for running the workflow
├── tests/                        # Unit tests for all components
├── tools/                        # Additional tools (like Excel to TXT converter)
│   └── excel_converter.py        # Excel converter tool
├── config.yaml                   # Configuration file for setting up file paths and processing options
├── requirements.txt              # List of dependencies
├── setup.py                      # Setup script for packaging the project
└── setup_and_run.py              # Script to automatically set up and run the app
```

## Usage

To run the project, ensure that the required data files are placed in the correct directories (`data/`), and then run the main script:

```bash
python src/main.py
```

This will load the data, process it, and generate the necessary plots in the `plots/` directory.

### Example KLA Workflow

To process KLA data specifically, use the `run_kla_workflow` method in `MainApp`:

```python
app.run_kla_workflow(kla_file=Path('path/to/kla_data.txt'))
```

## Configuration

The configuration file `config.yaml` controls various aspects of data loading, processing, and plotting. Key sections include:

- **data_loader**: Paths and options for loading offline, online, and KLA data.
- **data_processor**: Options for data processing, including numeric columns.
- **plotter**: Plotting styles and options.
- **logging**: Logging configurations for tracking workflow execution.

Example configuration:

```yaml
data_loader:
  offline_file: 'data/offline.txt'
  online_file: 'data/online.txt'
  kla_dir: 'data/data(kla)/'
  column_separator: ','
  decimal_separator: '.'
  encoding: 'utf-8'

plotter:
  plot_dir: 'plots/'
  figsize_main: [17, 12]
  dpi: 300

logging:
  level: 'DEBUG'
  format: '%(asctime)s [%(levelname)s] %(message)s'
  handlers:
    - type: stream
    - type: file
      filename: 'logs/application.log'
```

## Tests

Unit tests are located in the `tests/` directory. To run the tests, execute:

```bash
pytest
```

This will execute all tests and provide coverage reports for the different modules.

## Requirements

The project dependencies are listed in the `requirements.txt` file. You can install them using:

```bash
pip install -r requirements.txt
```

Key dependencies:
- pandas
- matplotlib
- seaborn
- PyYAML
- pytest
- pytest-mock
