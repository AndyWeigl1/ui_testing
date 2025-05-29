#!/usr/bin/env python3
"""
Schneider National Attachments Saver
Saves email attachments from selected Outlook emails to the Schneider import bills folder.
"""

import sys
import os
import pythoncom
import win32com.client
import psutil
from win32com.client import Dispatch, gencache
from datetime import datetime


class LogLevel:
    DEBUG = "[DEBUG]"
    INFO = "[INFO]"
    SUCCESS = "[SUCCESS]"
    WARNING = "[WARNING]"
    ERROR = "[ERROR]"


def log(level, message):
    """Print a log message with timestamp and level"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{timestamp} {level} {message}")
    sys.stdout.flush()  # Force immediate output


def find_path_with_components(folder_components):
    """Find a path containing the specified folder components."""
    log(LogLevel.DEBUG, f"Searching for path with components: {folder_components}")

    home_dir = os.path.expanduser('~')
    # Define all possible base directories
    possible_bases = [
        os.path.join(home_dir, 'Kodiak Cakes'),
        os.path.join(home_dir, 'OneDrive - Kodiak Cakes')
    ]

    # Define possible entry points from each base
    possible_entry_points = [
        ['Kodiak Cakes Team Site - Public'],
        ['Kodiak Cakes Team Site - Accounting', 'Public'],
        ['']  # Empty entry point for direct access
    ]

    for base in possible_bases:
        log(LogLevel.DEBUG, f"Checking base directory: {base}")
        if not os.path.exists(base):
            log(LogLevel.DEBUG, f"Base directory does not exist: {base}")
            continue

        for entry_point in possible_entry_points:
            current_path = base
            for entry in entry_point:
                if entry:  # Skip empty entry
                    test_path = os.path.join(current_path, entry)
                    if not os.path.exists(test_path):
                        break
                    current_path = test_path

            result = find_components_flexible(current_path, folder_components)
            if result:
                log(LogLevel.DEBUG, f"Found valid path: {result}")
                return result

    log(LogLevel.DEBUG, "No valid path found")
    return None


def find_components_flexible(start_path, components, depth=0, max_depth=3):
    """Recursively find folder components with flexible matching."""
    if depth > max_depth:
        return None
    if not components:
        return start_path

    next_component = components[0]
    direct_path = os.path.join(start_path, next_component)

    if os.path.exists(direct_path):
        result = find_components_flexible(direct_path, components[1:], depth, max_depth)
        if result:
            return result

    try:
        for item in os.listdir(start_path):
            item_path = os.path.join(start_path, item)
            if os.path.isdir(item_path):
                if item.startswith('.'):
                    continue
                if item == next_component:
                    result = find_components_flexible(item_path, components[1:], depth, max_depth)
                    if result:
                        return result
                result = find_components_flexible(item_path, components, depth + 1, max_depth)
                if result:
                    return result
    except (PermissionError, FileNotFoundError) as e:
        log(LogLevel.DEBUG, f"Access denied or file not found: {e}")
        pass

    return None


def get_folder_path(components):
    """Get the full path for the specified folder components."""
    path = find_path_with_components(components)
    if not path:
        log(LogLevel.ERROR, f"Could not find a valid path containing the components: {components}")
        return None
    return path


def get_po_workbook():
    """Get path to the POs by Division workbook."""
    folder_components = ['Vendors', 'Schneider National Inc', 'Imports', 'POs by Division.xlsx']
    return get_folder_path(folder_components)


def get_import_bills_folder_path():
    """Get path to the import bills folder."""
    folder_components = ['Vendors', 'Schneider National Inc', 'Imports', 'Bills']
    return get_folder_path(folder_components)


def get_schneider_report_folder():
    """Get path to the Schneider report folder."""
    folder_components = ['Vendors', 'Schneider National Inc', 'Imports', 'Schneider Report']
    return get_folder_path(folder_components)


def get_upload_template():
    """Get path to the upload template."""
    folder_components = ['Vendors', 'Schneider National Inc', 'Imports', 'Schneider Upload Template.xlsx']
    return get_folder_path(folder_components)


def get_csv_upload_base_folder():
    """Get path to the CSV uploads folder."""
    folder_components = ['Vendors', 'Schneider National Inc', 'Imports', 'CSV Uploads']
    return get_folder_path(folder_components)


def is_outlook_open():
    """Check if Outlook is currently running."""
    log(LogLevel.DEBUG, "Checking if Outlook is running...")
    for process in psutil.process_iter(['name']):
        if process.info['name'] == "OUTLOOK.EXE":
            log(LogLevel.DEBUG, "Outlook process found")
            return True
    log(LogLevel.DEBUG, "Outlook process not found")
    return False


def save_attachments_from_selected_emails(folder_path):
    """Save attachments from selected emails in Outlook to the specified folder."""
    log(LogLevel.DEBUG, "Initializing COM library for Outlook integration...")
    pythoncom.CoInitialize()  # Initialize COM library

    try:
        log(LogLevel.INFO, "Connecting to Outlook application...")
        outlook = Dispatch("Outlook.Application")
        gencache.EnsureDispatch(outlook.Application)
        namespace = outlook.GetNamespace("MAPI")
        explorer = outlook.ActiveExplorer()
        selection = explorer.Selection

        if not selection:
            log(LogLevel.WARNING, "No emails selected in Outlook")
            return 0

        log(LogLevel.INFO, f"Found {len(selection)} selected email(s)")

        if not os.path.exists(folder_path):
            log(LogLevel.INFO, f"Creating directory: {folder_path}")
            os.makedirs(folder_path)

        saved_count = 0
        total_attachments = 0

        for i, item in enumerate(selection, 1):
            log(LogLevel.DEBUG, f"Processing email {i}/{len(selection)}")

            if item.Class == win32com.client.constants.olMail:
                email_subject = getattr(item, 'Subject', 'No Subject')
                log(LogLevel.INFO, f"Processing email: {email_subject[:50]}...")

                if item.Attachments.Count == 0:
                    log(LogLevel.DEBUG, f"No attachments found in email: {email_subject[:30]}...")
                    continue

                for attachment in item.Attachments:
                    total_attachments += 1
                    attachment_name = attachment.FileName
                    save_path = os.path.join(folder_path, attachment_name)

                    try:
                        # Check if file already exists
                        if os.path.exists(save_path):
                            log(LogLevel.WARNING, f"File already exists, skipping: {attachment_name}")
                            continue

                        attachment.SaveAsFile(save_path)
                        saved_count += 1
                        log(LogLevel.SUCCESS, f"Saved attachment: {attachment_name}")

                    except Exception as e:
                        log(LogLevel.ERROR, f"Failed to save attachment {attachment_name}: {str(e)}")
            else:
                log(LogLevel.DEBUG, f"Skipping non-email item in selection")

        log(LogLevel.INFO, f"Processing complete: {saved_count}/{total_attachments} attachments saved")
        return saved_count

    except Exception as e:
        log(LogLevel.ERROR, f"Error during attachment processing: {str(e)}")
        return 0
    finally:
        log(LogLevel.DEBUG, "Uninitializing COM library")
        pythoncom.CoUninitialize()  # Uninitialize COM library when done


def main():
    """Main function to execute the attachment saving process."""
    log(LogLevel.INFO, "Starting Schneider National attachment saver...")

    # Get required folder paths
    log(LogLevel.INFO, "Locating required folders...")
    import_bills_folder = get_import_bills_folder_path()
    schneider_report_folder = get_schneider_report_folder()
    csv_uploads_base_folder = get_csv_upload_base_folder()

    # Validate all required folders are found
    if not import_bills_folder:
        log(LogLevel.ERROR, "Import bills folder could not be found")
        return 1
    if not schneider_report_folder:
        log(LogLevel.ERROR, "Schneider report folder could not be found")
        return 1
    if not csv_uploads_base_folder:
        log(LogLevel.ERROR, "CSV uploads folder could not be found")
        return 1

    log(LogLevel.SUCCESS, f"Import bills folder: {import_bills_folder}")
    log(LogLevel.DEBUG, f"Schneider report folder: {schneider_report_folder}")
    log(LogLevel.DEBUG, f"CSV uploads folder: {csv_uploads_base_folder}")

    # Check if Outlook is running
    if not is_outlook_open():
        log(LogLevel.ERROR, "Outlook is not open. Please open Outlook and select the emails to process, then retry.")
        return 1

    log(LogLevel.SUCCESS, "Outlook is running")

    # Save attachments from selected emails
    log(LogLevel.DEBUG, "Starting attachment extraction from selected emails...")
    saved_count = save_attachments_from_selected_emails(import_bills_folder)

    if saved_count > 0:
        log(LogLevel.SUCCESS, f"Operation completed successfully! Saved {saved_count} attachment(s)")
    else:
        log(LogLevel.WARNING, "No attachments were saved. Please check that you have selected emails with attachments.")

    return 0


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        log(LogLevel.WARNING, "Script interrupted by user")
        sys.exit(1)
    except Exception as e:
        log(LogLevel.ERROR, f"Unexpected error: {str(e)}")
        sys.exit(1)