import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from io import StringIO

# Configuration parameters
DELIMITER = ';'
DECIMAL = ','
FILE_PATH = '../data/data(kla)/Daten(klA)400rpm 3L.txt'  # Path to your CSV file
ENCODING = 'utf-16-le'  # File encoding


def find_data_start(file_path, delimiter=';'):
    """
    Finds the line where the actual data begins.
    """
    with open(file_path, 'r', encoding=ENCODING) as file:
        for i, line in enumerate(file):
            if line.startswith('Time'):
                header_line = line.strip()
                units_line = next(file, '').strip()  # Next line is the units line
                return i + 2, header_line, units_line  # Data starts two lines after 'Time'
    return 0, None, None


def read_data(file_path):
    """
    Reads the CSV file and processes it.
    """
    data_start, header_line, units_line = find_data_start(file_path, DELIMITER)

    if header_line is None:
        raise ValueError("Header with 'Time' was not found.")

    columns = [col.strip() for col in header_line.split(DELIMITER) if col.strip() != '']

    # Read the data lines
    with open(file_path, 'r', encoding=ENCODING) as file:
        for _ in range(data_start):
            next(file)  # Skip the first data_start lines (metadata + header + units)
        data_str = ''.join(file.readlines())

    # Use StringIO to read the data with pandas
    df = pd.read_csv(
        StringIO(data_str),
        delimiter=DELIMITER,
        decimal=DECIMAL,
        names=columns,
        usecols=columns,  # Only read the defined columns
        engine='python',
        skip_blank_lines=True
    )

    return df


def preprocess_data(df):
    """
    Performs additional data cleaning if necessary.
    """
    # Remove whitespace from column names
    df.columns = df.columns.str.strip()

    # Remove unnecessary whitespace from the 'Time' column
    df['Time'] = df['Time'].astype(str).str.strip()

    # Convert the 'Time' column to datetime with error handling
    df['Time'] = pd.to_datetime(df['Time'], format='%d.%m.%Y %H:%M:%S', errors='coerce', dayfirst=True)

    # Check if there are rows where the time was not parsed correctly
    num_invalid_times = df['Time'].isna().sum()
    if num_invalid_times > 0:
        print(f"Warning: {num_invalid_times} rows have invalid timestamps and were marked as NaT.")

    # Remove rows with NaT in the 'Time' column
    df = df.dropna(subset=['Time']).reset_index(drop=True)

    # Convert all numeric columns from strings to Floats
    numeric_columns = df.columns.drop('Time')
    for col in numeric_columns:
        # Since decimal=',' is already set, the values should be floats
        # If they are still strings, convert them
        if df[col].dtype == object:
            df[col] = pd.to_numeric(df[col].str.replace(',', '.'), errors='coerce')

    return df


def visualize_data(df):
    """
    Creates visualizations of the data.
    """
    sns.set(style="darkgrid")
    plt.figure(figsize=(14, 8))

    # Check if the columns are present before plotting
    plot_columns = ['spO2', 'sO2', 'sCO2', 'NStirrer', 'FAirIn', 'FO2In']
    colors = ['blue', 'green', 'red', 'orange', 'purple', 'brown']

    for col, color in zip(plot_columns, colors):
        if col in df.columns:
            plt.plot(df['Time'], df[col], label=f'{col}', color=color)
        else:
            print(f"Warning: Column '{col}' not found and will be skipped.")

    plt.xlabel('Time')
    plt.ylabel('Measurements')
    plt.title('Measurement Data Over Time')
    plt.legend()
    plt.tight_layout()
    plt.show()


def main():
    try:
        # Read data
        df = read_data(FILE_PATH)

        # Preprocess data
        df = preprocess_data(df)

        # Display first few rows to verify data
        print(df.head())

        # Check for NaT in the 'Time' column
        invalid_time_rows = df[df['Time'].isna()]
        if not invalid_time_rows.empty:
            print("The following rows have invalid timestamps:")
            print(invalid_time_rows)

        # Visualize data
        visualize_data(df)
    except FileNotFoundError:
        print(f"Error: The file '{FILE_PATH}' was not found.")
    except pd.errors.ParserError as e:
        print(f"Parser error while reading the file: {e}")
    except ValueError as e:
        print(f"Value error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
