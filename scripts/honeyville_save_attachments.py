#!/usr/bin/env python3
"""
Honeyville Attachments Saver
Saves email attachments from selected Outlook emails to Honeyville folders.
"""

import sys
import os
import pythoncom
import win32com.client
import psutil
from win32com.client import Dispatch, gencache
from datetime import datetime
import json
import pdfplumber
import re
from io import BytesIO
import shutil
import glob


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


def load_script_settings():
    """Load saved path configurations for this script"""
    settings_file = os.path.join("config", "script_settings", "honeyville_attachments_saver_settings.json")

    if os.path.exists(settings_file):
        try:
            with open(settings_file, 'r') as f:
                settings = json.load(f)
                log(LogLevel.DEBUG, f"Loaded custom path configurations from {settings_file}")
                return settings
        except Exception as e:
            log(LogLevel.WARNING, f"Failed to load settings file: {e}")

    return {}


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


def get_folder_path(components, settings_key=None):
    """Get the full path for the specified folder components, checking settings first."""
    # Check if we have a configured path for this key
    if settings_key:
        settings = load_script_settings()
        configured_path = settings.get(settings_key)

        if configured_path and os.path.exists(configured_path):
            log(LogLevel.INFO, f"Using configured path for {settings_key}: {configured_path}")
            return configured_path
        elif configured_path:
            log(LogLevel.WARNING, f"Configured path for {settings_key} does not exist: {configured_path}")

    # Fall back to default path discovery
    path = find_path_with_components(components)
    if not path:
        log(LogLevel.ERROR, f"Could not find a valid path containing the components: {components}")
        return None
    return path


def get_od_invoice_folder_path():
    """Get path to the Honeyville shipments folder."""
    folder_components = ['Waffle-Dry', 'Honeyville', 'Shipments to RJW']
    return get_folder_path(folder_components, 'shipments_folder')


def get_invoice_folder_path():
    """Get path to the Honeyville data imports folder."""
    folder_components = ['Waffle-Dry', 'Honeyville', 'Data Imports']
    return get_folder_path(folder_components, 'data_imports_folder')


def is_outlook_open():
    """Check if Outlook is currently running."""
    log(LogLevel.DEBUG, "Checking if Outlook is running...")
    for process in psutil.process_iter(['name']):
        if process.info['name'] == "OUTLOOK.EXE":
            log(LogLevel.DEBUG, "Outlook process found")
            return True
    log(LogLevel.DEBUG, "Outlook process not found")
    return False


def extract_text_from_pdf(pdf_file_bytes):
    """Extract text from PDF bytes using pdfplumber."""
    text = ''
    try:
        with pdfplumber.open(BytesIO(pdf_file_bytes)) as pdf:
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted
        return text
    except Exception as e:
        raise Exception(f"Failed to extract text from PDF: {str(e)}")


def extract_invoice_data(text):
    """Extract invoice number and date from PDF text."""
    extracted_data = {}

    # Debug: Log first 500 characters to see what we're working with
    debug_text = text[:500].replace('\n', '\\n')
    log(LogLevel.DEBUG, f"First 500 chars of PDF text: {debug_text}")

    # Try to find invoice date using Honeyville-specific patterns
    invoice_date_match = re.search(r"Invoice Date:\s*(\d{1,2}/\d{1,2}/\d{4})", text)
    if invoice_date_match:
        extracted_data["Invoice Date"] = invoice_date_match.group(1).strip()
        log(LogLevel.DEBUG, f"Found invoice date: {extracted_data['Invoice Date']}")

    # Try to find invoice number using Honeyville-specific patterns
    invoice_match = re.search(r"Invoice:\s*([^\n\r]+)", text)
    if invoice_match:
        extracted_data["Invoice"] = invoice_match.group(1).strip()
        log(LogLevel.DEBUG, f"Found invoice number: {extracted_data['Invoice']}")

    # If no specific patterns found, try more general patterns
    if "Invoice Date" not in extracted_data:
        # Try more general date patterns
        date_patterns = [
            r"DATE[:\s]*(\d{1,2}/\d{1,2}/\d{4})",
            r"Date[:\s]*(\d{1,2}/\d{1,2}/\d{4})",
            r"INVOICE\s*Date[:\s]*(\d{1,2}/\d{1,2}/\d{4})"
        ]

        for pattern in date_patterns:
            date_match = re.search(pattern, text, re.IGNORECASE)
            if date_match:
                extracted_data["Invoice Date"] = date_match.group(1).strip()
                log(LogLevel.DEBUG, f"Found date using general pattern: {extracted_data['Invoice Date']}")
                break

    if "Invoice" not in extracted_data:
        # Try more general invoice patterns
        invoice_patterns = [
            r"INVOICE\s*#\s*[:\s]*([^\n\r]+)",
            r"INVOICE\s*NUMBER[:\s]*([^\n\r]+)",
            r"Invoice\s*#[:\s]*([^\n\r]+)",
            r"Invoice\s*Number[:\s]*([^\n\r]+)"
        ]

        for pattern in invoice_patterns:
            invoice_match = re.search(pattern, text, re.IGNORECASE)
            if invoice_match:
                extracted_data["Invoice"] = invoice_match.group(1).strip()
                log(LogLevel.DEBUG, f"Found invoice using general pattern: {extracted_data['Invoice']}")
                break

    return extracted_data


def save_attachments_from_selected_emails(invoice_folder, od_invoice_folder):
    """Save attachments from selected emails in Outlook to the specified folders."""
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

        # Clean up existing PDFs in data imports folder
        log(LogLevel.INFO, "Cleaning up existing PDF files in data imports folder...")
        pdf_files = glob.glob(os.path.join(invoice_folder, '*.pdf'))
        for pdf_file in pdf_files:
            try:
                os.remove(pdf_file)
                log(LogLevel.DEBUG, f"Deleted existing PDF: {pdf_file}")
            except Exception as e:
                log(LogLevel.WARNING, f"Error deleting {pdf_file}: {e}")

        saved_count = 0
        total_attachments = 0
        saved_files = []

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

                    # Save the attachment to a temporary file
                    temp_file_path = os.path.join(od_invoice_folder, attachment_name)

                    try:
                        attachment.SaveAsFile(temp_file_path)
                        log(LogLevel.DEBUG, f"Saved temporary file: {temp_file_path}")

                        # Read the temporary file as bytes for PDF processing
                        with open(temp_file_path, 'rb') as file:
                            pdf_file_bytes = file.read()

                        # Try to extract text and process the PDF
                        try:
                            pdf_text = extract_text_from_pdf(pdf_file_bytes)

                            # Extract invoice data (date and invoice number)
                            invoice_data = extract_invoice_data(pdf_text)

                            invoice_date = invoice_data.get("Invoice Date")
                            invoice_number = invoice_data.get("Invoice")

                            if not invoice_number:
                                log(LogLevel.WARNING, f"Invoice number not found in email '{email_subject}'. Using original filename.")
                                invoice_number = os.path.splitext(attachment_name)[0]
                            else:
                                # Remove the "-IN" suffix from invoice numbers if present
                                if invoice_number.endswith("-IN"):
                                    invoice_number = invoice_number[:-3]  # Remove the last 3 characters ("-IN")

                            # Generate filename with invoice number
                            file_extension = os.path.splitext(attachment_name)[1]
                            new_filename = f"{invoice_number}{file_extension}"

                            if invoice_date:
                                try:
                                    # Try to parse the date
                                    due_date = datetime.strptime(invoice_date, "%m/%d/%Y")

                                    year_folder = os.path.join(od_invoice_folder, str(due_date.year))
                                    month_folder = os.path.join(year_folder, f"{due_date.strftime('%m')} - {due_date.year}")

                                    # Create year and month folders if they don't exist
                                    if not os.path.exists(year_folder):
                                        os.makedirs(year_folder)
                                    if not os.path.exists(month_folder):
                                        os.makedirs(month_folder)

                                    # Move the temporary file to the correct folder with new filename
                                    final_file_path = os.path.join(month_folder, new_filename)
                                    shutil.move(temp_file_path, final_file_path)
                                    saved_files.append(final_file_path)
                                    log(LogLevel.SUCCESS, f"Saved invoice to organized folder: {final_file_path}")

                                    # Save the file to the additional folder with new filename
                                    additional_file_path = os.path.join(invoice_folder, new_filename)
                                    shutil.copy(final_file_path, additional_file_path)
                                    log(LogLevel.SUCCESS, f"Copied invoice to data imports: {additional_file_path}")

                                    saved_count += 1

                                except ValueError as e:
                                    log(LogLevel.WARNING, f"Invalid date format in email '{email_subject}': {e}")
                                    log(LogLevel.INFO, f"Saved to temporary folder: {temp_file_path}")
                                    saved_files.append(temp_file_path)
                                    saved_count += 1
                            else:
                                log(LogLevel.WARNING, f"Invoice date not found in email '{email_subject}'")
                                log(LogLevel.INFO, f"Saved to temporary folder: {temp_file_path}")
                                saved_files.append(temp_file_path)
                                saved_count += 1

                        except Exception as e:
                            log(LogLevel.ERROR, f"Error processing PDF {attachment_name}: {str(e)}")
                            # Clean up the temp file if processing failed
                            if os.path.exists(temp_file_path):
                                os.remove(temp_file_path)

                    except Exception as e:
                        log(LogLevel.ERROR, f"Error saving attachment {attachment_name}: {str(e)}")

            else:
                log(LogLevel.DEBUG, f"Skipping non-email item in selection")

        # Display summary
        display_summary(saved_files)

        log(LogLevel.INFO, f"Processing complete: {saved_count}/{total_attachments} attachments saved")
        return saved_count

    except Exception as e:
        log(LogLevel.ERROR, f"Error during attachment processing: {str(e)}")
        return 0
    finally:
        log(LogLevel.DEBUG, "Uninitializing COM library")
        pythoncom.CoUninitialize()  # Uninitialize COM library when done


def display_summary(saved_files):
    """Display a summary of saved files organized by folder."""
    if not saved_files:
        log(LogLevel.INFO, "No files were saved")
        return

    summary = {}
    for file_path in saved_files:
        folder, file_name = os.path.split(file_path)
        month_year_folder = os.path.basename(folder)  # Gets "05 - 2025"

        # Get the year folder by going up one level
        year_folder = os.path.basename(os.path.dirname(folder))  # Gets "2025"

        # Create a key that combines year and month-year
        folder_key = f"{year_folder} > {month_year_folder}"

        invoice_number = os.path.splitext(file_name)[0]  # Get filename without extension

        if folder_key not in summary:
            summary[folder_key] = []

        summary[folder_key].append(invoice_number)

    for folder_key, invoice_numbers in summary.items():
        log(LogLevel.SUCCESS, f"Invoices saved in Honeyville > Shipments to RJW > {folder_key}:")
        for invoice in invoice_numbers:
            log(LogLevel.INFO, f"  - {invoice}")


def main():
    """Main function to execute the attachment saving process."""
    log(LogLevel.INFO, "Starting Honeyville attachment saver...")

    # Get required folder paths
    log(LogLevel.INFO, "Locating required folders...")
    invoice_folder = get_invoice_folder_path()
    od_invoice_folder = get_od_invoice_folder_path()

    # Validate all required folders are found
    if not invoice_folder:
        log(LogLevel.ERROR, "Data imports folder could not be found")
        return 1
    if not od_invoice_folder:
        log(LogLevel.ERROR, "Honeyville shipments folder could not be found")
        return 1

    log(LogLevel.SUCCESS, f"Data imports folder: {invoice_folder}")
    log(LogLevel.SUCCESS, f"Shipments folder: {od_invoice_folder}")

    # Check if Outlook is running
    if not is_outlook_open():
        log(LogLevel.ERROR, "Outlook is not open. Please open Outlook and select the emails to process, then retry.")
        return 1

    log(LogLevel.SUCCESS, "Outlook is running")

    # Save attachments from selected emails
    log(LogLevel.DEBUG, "Starting attachment extraction from selected emails...")
    saved_count = save_attachments_from_selected_emails(invoice_folder, od_invoice_folder)

    if saved_count > 0:
        log(LogLevel.SUCCESS, f"Operation completed successfully! Saved {saved_count} attachment(s)")
        log(LogLevel.INFO, "All selected invoices saved to OneDrive. The script is now complete.")
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