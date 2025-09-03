import os
import shutil
import argparse
from datetime import datetime
import hashlib
import sys

def get_file_hash(filepath, block_size=65536):
    """
    Generates an MD5 hash of a file to check for identity.
    """
    try:
        hasher = hashlib.md5()
        with open(filepath, 'rb') as f:
            buf = f.read(block_size)
            while len(buf) > 0:
                hasher.update(buf)
                buf = f.read(block_size)
        return hasher.hexdigest()
    except Exception as e:
        print(f"Error: Could not read file to generate hash for '{filepath}': {e}", file=sys.stderr)
        return None

def find_latest_backup(destination_dir):
    """
    Finds the path to the most recent backup folder in the destination directory.
    """
    backup_folders = []
    try:
        for entry in os.listdir(destination_dir):
            if os.path.isdir(os.path.join(destination_dir, entry)):
                try:
                    # Attempt to parse the timestamp from the folder name
                    datetime.strptime(entry, '%Y-%m-%d_%H-%M-%S')
                    backup_folders.append(entry)
                except ValueError:
                    # Not a timestamped backup folder, so we ignore it
                    continue
        backup_folders.sort(reverse=True)
        return os.path.join(destination_dir, backup_folders[0]) if backup_folders else None
    except Exception as e:
        print(f"Error: Could not find latest backup folder: {e}", file=sys.stderr)
        return None

def run_backup(source_dir, destination_dir, full_backup, dry_run=False):
    """
    Copies files from a source to a destination folder, with options for
    incremental or full backups.

    Args:
        source_dir (str): The path to the source folder.
        destination_dir (str): The path to the destination folder.
        full_backup (bool): If True, performs a full backup. If False,
                            performs an incremental backup.
        dry_run (bool): If True, simulates the backup without moving files.
    """
    # 1. Validate source and destination paths
    if not os.path.isdir(source_dir):
        print(f"Error: Source path '{source_dir}' is not a valid directory.", file=sys.stderr)
        return
    if not os.path.isdir(destination_dir):
        print(f"Error: Destination path '{destination_dir}' is not a valid directory.", file=sys.stderr)
        return

    # 2. Prepare the new backup directory with a timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    backup_folder_name = timestamp
    backup_path = os.path.join(destination_dir, backup_folder_name)
    log_file_path = os.path.join(backup_path, 'backup_log.txt')

    if dry_run:
        print("\n*** DRY RUN MODE: No files will be copied. ***\n")
    
    print(f"Starting {'FULL' if full_backup else 'INCREMENTAL'} backup from '{source_dir}'...")

    # Create a log list to store actions
    log_messages = []
    
    # Create the destination directory if it doesn't exist
    try:
        os.makedirs(backup_path, exist_ok=True)
        log_messages.append(f"Created new backup directory: '{backup_path}'")
    except OSError as e:
        print(f"Error: Failed to create destination directory '{backup_path}': {e}", file=sys.stderr)
        return
    
    # For incremental backup, find the latest backup folder to compare against
    latest_backup_dir = None
    if not full_backup:
        latest_backup_dir = find_latest_backup(destination_dir)
        if latest_backup_dir:
            print(f"  > Comparing to latest backup at: '{latest_backup_dir}'")
            log_messages.append(f"Performing incremental backup against: '{latest_backup_dir}'")
        else:
            print("  > No previous backups found. Performing a full backup instead.")
            log_messages.append("No previous backups found. Performing a full backup.")

    # 3. Iterate through files and copy them
    files_to_copy = 0
    files_skipped = 0
    total_files = 0

    for root, _, files in os.walk(source_dir):
        for filename in files:
            total_files += 1
            source_file = os.path.join(root, filename)
            relative_path = os.path.relpath(source_file, source_dir)
            destination_file = os.path.join(backup_path, relative_path)
            
            # Check if file already exists in the latest backup for incremental mode
            if not full_backup and latest_backup_dir:
                latest_backup_file = os.path.join(latest_backup_dir, relative_path)
                if os.path.exists(latest_backup_file):
                    # Check if files are identical
                    try:
                        if os.path.getsize(source_file) == os.path.getsize(latest_backup_file):
                            print(f"  > Skipping identical file: '{relative_path}'")
                            log_messages.append(f"Skipped identical file: '{relative_path}'")
                            files_skipped += 1
                            continue # Skip the copy operation
                        else:
                            print(f"  > Found updated file: '{relative_path}'")
                            log_messages.append(f"Found updated file: '{relative_path}'")
                    except OSError as e:
                        print(f"Error checking file size for '{relative_path}': {e}. Copying anyway.", file=sys.stderr)
            
            # Create subdirectories in the destination if they don't exist
            os.makedirs(os.path.dirname(destination_file), exist_ok=True)

            # Copy the file
            if not dry_run:
                try:
                    shutil.copy2(source_file, destination_file)
                    print(f"  > Copied '{relative_path}'")
                    log_messages.append(f"Copied: '{relative_path}'")
                    files_to_copy += 1
                except shutil.SameFileError:
                    print(f"  > Warning: File '{relative_path}' is already in destination.", file=sys.stderr)
                    log_messages.append(f"Warning: Skipped '{relative_path}' because it already exists in the destination.")
                    files_skipped += 1
                except PermissionError as e:
                    print(f"  > Error: Permission denied for '{relative_path}'. Skipping.", file=sys.stderr)
                    log_messages.append(f"Permission denied. Skipped: '{relative_path}'")
                    files_skipped += 1
                except Exception as e:
                    print(f"  > Unexpected error copying '{relative_path}': {e}", file=sys.stderr)
                    log_messages.append(f"Unexpected error. Skipped: '{relative_path}' due to error: {e}")
                    files_skipped += 1
            else:
                print(f"  > (Dry Run) Would copy '{relative_path}'")
                log_messages.append(f"(Dry Run) Would copy: '{relative_path}'")
                files_to_copy += 1

    # Write the log file
    try:
        with open(log_file_path, 'w', encoding='utf-8') as log_file:
            log_file.write(f"Backup Log: {timestamp}\n")
            log_file.write(f"Source: {source_dir}\n")
            log_file.write(f"Destination: {destination_dir}\n")
            log_file.write(f"Backup Type: {'Full' if full_backup else 'Incremental'}\n")
            log_file.write(f"Dry Run: {'Yes' if dry_run else 'No'}\n\n")
            log_file.write("--- Actions ---\n")
            for message in log_messages:
                log_file.write(message + '\n')
        print(f"\nBackup log saved to '{log_file_path}'")
    except Exception as e:
        print(f"\nError: Could not write backup log file: {e}", file=sys.stderr)
    
    # Print the summary
    print("\n--- Backup Summary ---")
    print(f"Total files in source: {total_files}")
    print(f"Files {'would be ' if dry_run else ''}copied: {files_to_copy}")
    print(f"Files skipped: {files_skipped}")
    print("----------------------")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="A script to back up files from a source directory to a destination with full and incremental options."
    )
    parser.add_argument(
        "source_dir",
        help="The path to the source directory to be backed up."
    )
    parser.add_argument(
        "destination_dir",
        help="The path to the destination directory for the backup."
    )
    parser.add_argument(
        "-f", "--full",
        action="store_true",
        help="Performs a full backup, copying all files regardless of existence in previous backups."
    )
    parser.add_argument(
        "-i", "--incremental",
        action="store_true",
        help="Performs an incremental backup, copying only new or modified files. This is the default behavior."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulates the backup process without actually copying or deleting any files."
    )
    
    args = parser.parse_args()

    # Determine backup type (incremental is default if no flags are specified)
    is_full_backup = args.full
    if args.incremental and not args.full:
        is_full_backup = False
    elif not args.incremental and not args.full:
        is_full_backup = False

    run_backup(args.source_dir, args.destination_dir, is_full_backup, args.dry_run)
