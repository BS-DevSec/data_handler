import os
import pandas as pd

# Define function to clean and convert Excel sheets to tab-separated TXT files
def clean_and_convert_to_txt(sheet_data, output_txt_file):
    """Cleans the sheet data by removing spaces and saving as a tab-separated TXT file."""
    # Remove spaces from column names
    sheet_data.columns = sheet_data.columns.str.replace(' ', '', regex=False)

    # Remove spaces from all cells (including numeric and mixed types)
    sheet_data_cleaned = sheet_data.astype(str).apply(lambda x: x.str.replace(' ', '', regex=False))

    # Save the cleaned data into a tab-separated TXT file
    sheet_data_cleaned.to_csv(output_txt_file, sep='\t', index=False)

def convert_excel_to_txt(excel_file_1, excel_file_2, output_dir):
    """Converts two Excel files into tab-separated TXT files and saves them to the output directory."""
    # Load the Excel sheets from both files
    data_1 = pd.read_excel(excel_file_1, sheet_name=None)  # Load all sheets from the first file
    data_2 = pd.read_excel(excel_file_2, sheet_name=None)  # Load all sheets from the second file

    # Print available sheet names for debugging
    print(f"Available sheets in {os.path.basename(excel_file_1)}: {list(data_1.keys())}")
    print(f"Available sheets in {os.path.basename(excel_file_2)}: {list(data_2.keys())}")

    # Define the output paths for the cleaned TXT files in the output directory
    output_cleaned_txt_1 = os.path.join(output_dir, 'onlindata_HK_453.txt')
    output_cleaned_txt_2 = os.path.join(output_dir, 'offlindata_HK_45.txt')

    # Ensure correct sheet name access (adjust based on sheet names in your Excel files)
    clean_and_convert_to_txt(data_1['onlindata_HK_453'], output_cleaned_txt_1)
    clean_and_convert_to_txt(data_2['offlindata_HK_45'], output_cleaned_txt_2)

    print(f'Files have been cleaned and converted to {output_cleaned_txt_1} and {output_cleaned_txt_2}')

if __name__ == "__main__":
    # Define paths to the Excel files in the `data/excel/` directory
    excel_file_1 = '../data/excel/onlindata_HK_453.xlsx'
    excel_file_2 = '../data/excel/offlindata_HK_45.xlsx'

    # Output directory where the TXT files will be saved
    output_dir = '../data'

    # Convert Excel to TXT
    convert_excel_to_txt(excel_file_1, excel_file_2, output_dir)
