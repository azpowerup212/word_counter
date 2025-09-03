import os
import sys
import re
import argparse
from collections import Counter
from datetime import datetime

def parse_log_file(filepath):
    """
    Parses a single log file to count log levels, find timestamps, and
    identify common error messages.

    Args:
        filepath (str): The path to the log file.

    Returns:
        A dictionary with parsing results, or None if the file cannot be processed.
    """
    # Initialize counts and lists for this file
    log_counts = {
        'ERROR': 0,
        'WARNING': 0,
        'INFO': 0
    }
    error_messages = []
    first_timestamp = None
    last_timestamp = None
    line_number = 0

    try:
        # Try to open the file with utf-8 encoding first
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                lines = file.readlines()
        except UnicodeDecodeError:
            # If that fails, try a more common alternative encoding, like utf-16
            print(f"  > File '{filepath}' is not UTF-8. Trying with 'utf-16'...")
            with open(filepath, 'r', encoding='utf-16') as file:
                lines = file.readlines()
        
        for line in lines:
            line_number += 1
            line = line.strip()
            if not line:
                continue

            # Use a regular expression to find a timestamp at the start of a line
            timestamp_match = re.match(r'\[?(\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2})\]?', line)
            if timestamp_match:
                current_timestamp = timestamp_match.group(1)
                if not first_timestamp:
                    first_timestamp = current_timestamp
                last_timestamp = current_timestamp
            
            # Check for log levels
            if "ERROR" in line:
                log_counts['ERROR'] += 1
                # Extract the error message, assuming it's after the "ERROR" keyword
                error_message = line.split("ERROR", 1)[1].strip()
                error_messages.append(error_message)
            elif "WARNING" in line:
                log_counts['WARNING'] += 1
            elif "INFO" in line:
                log_counts['INFO'] += 1

    except FileNotFoundError:
        print(f"Error: The file '{filepath}' was not found.")
        return None
    except PermissionError:
        print(f"Error: Permission denied to read file '{filepath}'.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while processing '{filepath}': {e}")
        return None

    # Return the collected data
    return {
        'filepath': filepath,
        'counts': log_counts,
        'first_timestamp': first_timestamp,
        'last_timestamp': last_timestamp,
        'error_messages': error_messages
    }

def print_summary(all_results):
    """
    Prints a formatted summary table of the log analysis results.

    Args:
        all_results (list): A list of dictionaries with results from each file.
    """
    total_error = 0
    total_warning = 0
    total_info = 0
    all_error_messages = []

    # Print the table header
    print("\n" + "="*80)
    print(" " * 15 + "Log File Analysis Summary")
    print("="*80)
    print(f"{'File':<30} | {'INFO':<8} | {'WARNING':<8} | {'ERROR':<8} | {'First Entry':<20} | {'Last Entry':<20}")
    print("-" * 80)

    # Print a row for each file's results
    for result in all_results:
        if result:
            counts = result['counts']
            print(f"{os.path.basename(result['filepath']):<30} | {counts['INFO']:<8} | {counts['WARNING']:<8} | {counts['ERROR']:<8} | {result['first_timestamp'] or 'N/A':<20} | {result['last_timestamp'] or 'N/A':<20}")
            
            # Aggregate totals and all error messages
            total_error += counts['ERROR']
            total_warning += counts['WARNING']
            total_info += counts['INFO']
            all_error_messages.extend(result['error_messages'])

    print("=" * 80)
    print(f"{'TOTALS':<30} | {total_info:<8} | {total_warning:<8} | {total_error:<8} |")
    print("=" * 80)

    # Find and print the most common error messages
    if all_error_messages:
        print("\nTop 5 Most Common Error Messages:")
        most_common_errors = Counter(all_error_messages).most_common(5)
        if most_common_errors:
            for message, count in most_common_errors:
                print(f"  - ({count} times) {message}")
    else:
        print("\nNo error messages found.")
    print("-" * 80)

if __name__ == "__main__":
    # Set up the command-line argument parser
    parser = argparse.ArgumentParser(
        description="A script to parse log files and generate a summary report."
    )
    parser.add_argument(
        "log_files",
        nargs="+",  # This allows for one or more file arguments
        help="One or more log file paths to process."
    )
    
    args = parser.parse_args()

    # Process each log file and collect the results
    results = []
    for log_file in args.log_files:
        result = parse_log_file(log_file)
        if result:
            results.append(result)

    # Print the final summary table
    if results:
        print_summary(results)
    else:
        print("\nNo log files were successfully processed.")
