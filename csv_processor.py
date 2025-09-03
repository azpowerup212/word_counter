import os
import sys
import argparse
import pandas as pd
from collections import Counter

def process_csv(filepath, output_path=None, delimiter=None):
    """
    Reads and analyzes a single CSV file, calculating statistics and reporting on its content.

    Args:
        filepath (str): The path to the CSV file.
        output_path (str, optional): The path to export the summary to. Defaults to None.
        delimiter (str, optional): The delimiter to use for parsing the CSV. If None,
                                   pandas will try to detect it automatically.
    """
    print(f"\n--- Processing '{filepath}' ---")
    try:
        # A list of common encodings to try
        encodings_to_try = ['utf-8', 'latin1', 'utf-16']
        df = None

        # Loop through the encodings to find one that works
        for encoding in encodings_to_try:
            try:
                df = pd.read_csv(filepath, delimiter=delimiter, encoding=encoding)
                print(f"  > File successfully read with '{encoding}' encoding.")
                break # Exit the loop if the read is successful
            except UnicodeDecodeError:
                print(f"  > '{encoding}' encoding failed. Trying next...")
                continue # Try the next encoding in the list
            except pd.errors.ParserError:
                # If pandas can't parse it with a given delimiter, we'll try to autodetect later.
                # Just continue to the next encoding for now.
                continue

        # Check if a DataFrame was successfully created
        if df is None:
            print("Error: Could not read file with any tested encoding.")
            return

        # If no delimiter was specified, try to detect it
        if delimiter is None and df.shape[1] == 1:
            print("  > Auto-detection failed. Trying common delimiters...")
            try_delimiters = [';', '\t', '|']
            for d in try_delimiters:
                try:
                    df = pd.read_csv(filepath, delimiter=d)
                    if df.shape[1] > 1:
                        print(f"  > Delimiter detected as '{d}'.")
                        break
                except Exception:
                    continue # Skip if the delimiter causes another error

        if df is None or df.empty:
            print("  > Warning: File is empty or could not be parsed with common delimiters.")
            return

        # 1. Shows basic info (rows, columns)
        num_rows, num_cols = df.shape
        print(f"  > Total Rows: {num_rows}")
        print(f"  > Total Columns: {num_cols}")

        # Summary data structure
        summary = {
            'Column': [],
            'Data Type': [],
            'Missing Values': [],
            'Stats': []
        }

        # 4. Detects and reports missing values
        missing_values = df.isnull().sum()

        # 2. Calculates statistics for numeric columns
        # 3. Shows unique values count for text columns
        for col in df.columns:
            column_data = df[col]
            missing_count = missing_values[col]

            summary['Column'].append(col)
            summary['Missing Values'].append(f"{missing_count} ({missing_count/num_rows:.2%})")

            # Check if the column is numeric
            if pd.api.types.is_numeric_dtype(column_data):
                summary['Data Type'].append('Numeric')
                stats = {
                    'mean': column_data.mean(),
                    'min': column_data.min(),
                    'max': column_data.max()
                }
                summary['Stats'].append(stats)
            # Otherwise, it's a text/categorical column
            else:
                summary['Data Type'].append('Text')
                unique_count = column_data.nunique()
                stats = {
                    'unique_count': unique_count
                }
                summary['Stats'].append(stats)
        
        # Display the formatted summary
        print("\n  > Column-wise Summary:")
        print("    " + "="*70)
        for i, col in enumerate(summary['Column']):
            data_type = summary['Data Type'][i]
            missing_str = summary['Missing Values'][i]
            stats = summary['Stats'][i]

            print(f"    - Column: '{col}'")
            print(f"      - Data Type: {data_type}")
            print(f"      - Missing: {missing_str}")
            if data_type == 'Numeric':
                print(f"      - Mean: {stats['mean']:.2f}, Min: {stats['min']:.2f}, Max: {stats['max']:.2f}")
            else:
                print(f"      - Unique Values: {stats['unique_count']}")
            print("    " + "-"*70)

        # 5. Can export summary to a new CSV file
        if output_path:
            summary_df = pd.DataFrame(summary)
            summary_df['Stats'] = summary_df['Stats'].astype(str) # Convert dict to string for CSV
            try:
                summary_df.to_csv(output_path, index=False)
                print(f"\n  > Summary successfully exported to '{output_path}'")
            except Exception as e:
                print(f"  > Error exporting summary to '{output_path}': {e}")

    except FileNotFoundError:
        print(f"Error: The file '{filepath}' was not found.")
    except pd.errors.ParserError as e:
        print(f"Error: Failed to parse '{filepath}'. Please check the format. Details: {e}")
    except Exception as e:
        print(f"An unexpected error occurred while processing '{filepath}': {e}")

if __name__ == "__main__":
    # Set up the command-line argument parser
    parser = argparse.ArgumentParser(
        description="A script to process and analyze one or more CSV files."
    )
    parser.add_argument(
        "csv_files",
        nargs="+",  # This allows for one or more file arguments
        help="One or more CSV file paths to process."
    )
    parser.add_argument(
        "-o", "--output",
        help="Path to a new CSV file to export the summary to."
    )
    parser.add_argument(
        "-d", "--delimiter",
        help="Specify the delimiter (e.g., ',' or ';'). If not specified, pandas will attempt to detect it."
    )

    args = parser.parse_args()

    # Process each log file and collect the results
    for csv_file in args.csv_files:
        process_csv(csv_file, args.output, args.delimiter)
