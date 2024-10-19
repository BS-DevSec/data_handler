
# Data Handling Project

This project processes offline and online data related to a main culture simulation. It loads data from CSV files, processes it, and visualizes key metrics like glucose, biomass, ethanol, CO2, O2, and more.

## Project Structure

```bash
DataHandler/
│
├── data/                     # Directory containing data files
│   ├── offlindata_HK_45.txt  # Offline data file (TXT)
│   ├── onlindata_HK_453.txt  # Online data file (TXT)
│   ├── excel/                # Excel data files (if needed)
│   │   ├── offlindata_HK_45.xlsx
│   │   ├── onlindata_HK_453.xlsx
│
├── src/                      # Source code directory
│   ├── data_loader.py        # DataLoader class for loading data
│   ├── data_processor.py     # DataProcessor class for processing data
│   ├── plotter.py            # Plotter class for visualizing the data
│   ├── main.py               # Main application script
│
├── tools/                    # Tools directory
│   ├── excel_converter.py  # Excel-to-TXT conversion tool
│
└── README.md                 # Project description and instructions
```

## Installation

1. **Clone the repository**:

   ```bash
   git clone <repository-url>
   cd my_project
   ```

2. **Set up a virtual environment** (optional but recommended):

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install the required packages**:

   This project requires Python 3.7+ and some external libraries like `pandas` and `matplotlib`. You can install the dependencies using `pip`.

   ```bash
   pip install pandas matplotlib
   ```

4. **Place your data files in the correct directory**:

   Ensure that the following files are in the `data/` directory:
   - `offlindata_HK_45.txt` (Offline data)
   - `onlindata_HK_453.txt` (Online data)

   You can also use Excel files (`.xlsx`) for input, but ensure they are located in the `data/excel/` directory. The tool in the `tools/` folder can convert them to TXT files if necessary.

## Using the Excel-to-TXT Converter

If you need to convert the Excel files to tab-separated TXT files, you can use the provided tool in the `tools/` directory.

### Running the Converter

1. The converter script `excel_converter.py` is located in the `tools/` folder.
2. You can run the converter as a standalone script:

   ```bash
   python tools/excel_converter.py
   ```

3. The script will automatically convert the Excel files located in `data/excel/` into tab-separated TXT files and save them in the `data/` directory.

### Customizing the Converter

You can customize the script to change the input and output directories or file names by modifying the paths inside `excel_converter.py`.

## Running the Application

To run the application, execute the `main.py` script located in the `src/` directory. The script will load the data, process it, and display various plots.

From the `DataHandler/` directory, run the following command:

```bash
python src/main.py
```

### What the Application Does:

1. **Loads data**: The offline and online data are loaded from the `data/` folder.
2. **Processes data**: The script processes the time columns, converts them to numeric values, and creates masks for valid data.
3. **Visualizes data**: The processed data is visualized in a series of plots that display metrics like glucose, biomass, ethanol, CO2, O2, and more.

### Customizing Data File Locations

If your data files are stored in a different location, you can modify the paths in the `main.py` script:

```python
if __name__ == "__main__":
    # Modify these paths if your data files are in a different directory
    offline_file_path = '../data/offlindata_HK_45.txt'
    online_file_path = '../data/onlindata_HK_453.txt'

    # Initialize and run the main application
    app = MainApp(offline_file_path, online_file_path)
    app.run()
```

## Code Structure

### 1. `DataLoader` Class (`data_loader.py`)
This class handles the loading of both offline and online data files. It also cleans and converts time columns into a usable format.

- **Methods**:
  - `load_data()`: Loads data from CSV files.
  - `process_online_time_column()`: Cleans and processes the 'time' column in the online data.
  - `convert_columns_to_numeric(columns)`: Converts specified columns to numeric data.

### 2. `DataProcessor` Class (`data_processor.py`)
This class processes the loaded data by extracting relevant columns and calculating the feed times for glucose.

- **Methods**:
  - `extract_offline_columns()`: Extracts relevant columns from the offline data.
  - `calculate_feed_time()`: Calculates the numeric time for glucose feeds.
  - `get_valid_masks()`: Creates masks to filter out invalid data.

### 3. `Plotter` Class (`plotter.py`)
This class handles the visualization of the processed data. It generates several plots, including glucose, biomass, ethanol, CO2, O2, etc.

- **Methods**:
  - `plot_data()`: Creates and displays all the necessary plots.

### 4. `MainApp` Class (`main.py`)
This is the main orchestrator of the application. It loads, processes, and visualizes the data using the above classes.

- **Methods**:
  - `run()`: Runs the entire application workflow.

## Troubleshooting

1. **FileNotFoundError**: 
   Ensure that your data files are located in the `data/` folder and that the file paths in `main.py` are correct.
   
2. **Missing dependencies**: 
   Make sure all required libraries are installed. If necessary, run:

   ```bash
   pip install pandas matplotlib
   ```

## License

This project is licensed under the MIT License.
