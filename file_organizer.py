import os
import shutil
import argparse
import sys

def organize_files(folder_path, dry_run=False):
    """
    Organizes files in a given directory into subfolders based on their file extension.

    Args:
        folder_path (str): The path to the folder to organize.
        dry_run (bool): If True, a dry run is performed, and no files are moved.
                        Defaults to False.
    """
    # Check if the provided path is a valid directory
    if not os.path.isdir(folder_path):
        print(f"Error: The path '{folder_path}' is not a valid directory.")
        sys.exit(1)

    print(f"Starting file organization in '{folder_path}'...")
    if dry_run:
        print("\n*** This is a DRY RUN. No files will be moved. ***\n")

    # Get a list of all items in the folder
    try:
        all_items = os.listdir(folder_path)
    except PermissionError:
        print(f"Error: Permission denied to access folder '{folder_path}'.")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred while listing files: {e}")
        sys.exit(1)
        
    file_count = 0
    move_count = 0

    # Iterate over all items in the directory
    for item in all_items:
        item_path = os.path.join(folder_path, item)

        # Check if the item is a file (and not a folder)
        if os.path.isfile(item_path):
            file_count += 1
            # Get the file extension and convert to lowercase for consistency
            _, file_extension = os.path.splitext(item)
            file_extension = file_extension.lower().strip('.')

            # If there is no extension (e.g., a file named 'README'), use a special folder
            if not file_extension:
                file_extension = "no_extension"

            # Create the destination folder path
            destination_folder = os.path.join(folder_path, file_extension)

            # Check if the destination folder exists. If not, create it.
            if not os.path.exists(destination_folder):
                try:
                    os.makedirs(destination_folder)
                    print(f"  > Created folder: '{file_extension}'")
                except OSError as e:
                    print(f"  > Error creating folder '{file_extension}': {e}. Skipping file '{item}'.")
                    continue

            # Define the new path for the file
            destination_path = os.path.join(destination_folder, item)

            # Move the file unless it's a dry run
            if not dry_run:
                try:
                    shutil.move(item_path, destination_path)
                    move_count += 1
                    print(f"  > Moved '{item}' -> '{file_extension}/'")
                except shutil.SameFileError:
                    print(f"  > Warning: File '{item}' is already in its correct folder. Skipping.")
                except Exception as e:
                    print(f"  > Error moving '{item}': {e}. Skipping.")
            else:
                print(f"  > (Dry Run) Would move '{item}' -> '{file_extension}/'")

    print("\n--- Summary ---")
    if dry_run:
        print(f"Dry run complete. Found {file_count} files to be organized.")
    else:
        print(f"Organization complete. Moved {move_count} of {file_count} files.")
        print("Note: Files already in their correct subfolders were not moved.")
    print("-" * 15)

if __name__ == "__main__":
    # Set up the command-line argument parser
    parser = argparse.ArgumentParser(
        description="Organize files in a folder into subfolders based on their file extension."
    )
    parser.add_argument(
        "folder_path",
        help="The path to the folder you want to organize."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate the organization process without actually moving any files."
    )

    args = parser.parse_args()

    # Call the main function with the provided arguments
    organize_files(args.folder_path, args.dry_run)
