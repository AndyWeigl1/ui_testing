#!/usr/bin/env python3
"""
Divvy ME Transaction Upload Script
Processes transaction files and creates upload files for NetSuite
"""

import sys
import os
import pandas as pd
import numpy as np
import re
import glob
import operator
import random
import json
import pickle
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
    sys.stdout.flush()


class ScriptState:
    """Class to hold script state for pause/resume functionality"""

    def __init__(self):
        self.upload_df = None
        self.csv_upload_base_folder = None
        self.upload_template_file = None
        self.phase = None

    def save(self, filepath):
        """Save state to file"""
        with open(filepath, 'wb') as f:
            pickle.dump(self, f)

    @classmethod
    def load(cls, filepath):
        """Load state from file"""
        with open(filepath, 'rb') as f:
            return pickle.load(f)


def find_valid_path(base_dir, alternate_paths):
    for path in alternate_paths:
        full_path = os.path.join(base_dir, *path)
        if os.path.exists(full_path):
            return full_path, True
    return base_dir, False


def get_folder_path(alternate_paths, folder_components):
    home_dir = os.path.expanduser('~')
    onedrive_dir = 'Kodiak Cakes'
    base_dir = os.path.join(home_dir, onedrive_dir)

    valid_path, found = find_valid_path(base_dir, alternate_paths)
    if not found:
        log(LogLevel.ERROR, f"Could not find the valid base path starting from: '{base_dir}'")
        return None

    for component in folder_components:
        next_path = os.path.join(valid_path, component)
        if not os.path.exists(next_path):
            log(LogLevel.ERROR, f"Path resolution stopped at: '{valid_path}'. Could not find: '{component}'")
            return None
        valid_path = next_path

    return valid_path


def get_transaction_mapping_file():
    alternate_paths = [
        ['Kodiak Cakes Team Site - Private'],
        ['Kodiak Cakes Team Site - Accounting', 'Private']
    ]
    folder_components = ['Banking', 'Bill Divvy', 'Imports', 'Excel Files', 'Transaction Mapping.csv']
    return get_folder_path(alternate_paths, folder_components)


def get_transaction_file_folder():
    alternate_paths = [
        ['Kodiak Cakes Team Site - Private'],
        ['Kodiak Cakes Team Site - Accounting', 'Private']
    ]
    folder_components = ['Banking', 'Bill Divvy', 'Imports', 'Transaction File']
    return get_folder_path(alternate_paths, folder_components)


def get_upload_template_file():
    alternate_paths = [
        ['Kodiak Cakes Team Site - Private'],
        ['Kodiak Cakes Team Site - Accounting', 'Private']
    ]
    folder_components = ['Banking', 'Bill Divvy', 'Imports', 'Divvy ME Upload Template.xlsx']
    return get_folder_path(alternate_paths, folder_components)


def get_csv_upload_base_folder():
    alternate_paths = [
        ['Kodiak Cakes Team Site - Private'],
        ['Kodiak Cakes Team Site - Accounting', 'Private']
    ]
    folder_components = ['Banking', 'Bill Divvy']
    return get_folder_path(alternate_paths, folder_components)


def create_mapping_dict(transaction_mapping_df):
    mapping_dict = {}
    for index, row in transaction_mapping_df.iterrows():
        try:
            key = (row['Merchant Name'], row['Card Name'])
            value = {
                'Merchant Category': row['Merchant Category'],
                'GL Name': parse_conditional(row['GL Name']),
                'GL Internal ID': parse_conditional(row['GL Internal ID']),
                'Transaction Cost Center': row['Transaction Cost Center'],
                'Cost Center Internal ID': row['Cost Center Internal ID'],
                'Customer Internal ID': row['Customer Internal ID'],
                'Customer': row['Customer'],
                'Line Memo': row['Line Memo'],
                'Include Memo': row['Include Memo'] == 'Yes'
            }
            mapping_dict[key] = value
        except Exception as e:
            log(LogLevel.ERROR, f"Error processing row {index} in transaction_mapping_df: {str(e)}")
            log(LogLevel.DEBUG, f"Row data: {row}")
    return mapping_dict


def parse_conditional(value):
    if not isinstance(value, str) or not 'IF' in value:
        return value

    conditions = [cond.strip() for cond in value.split(';')]
    parsed_conditions = []

    for condition in conditions:
        if condition.startswith('IF'):
            try:
                parts = condition.replace('IF', '').split('THEN')
                if len(parts) == 2:
                    condition_part = parts[0].strip()
                    result_part = parts[1].strip()
                    parsed_conditions.append((condition_part, result_part))
            except Exception as e:
                log(LogLevel.ERROR, f"Error parsing condition: {condition}")
                log(LogLevel.DEBUG, f"Error details: {str(e)}")
                continue

    return parsed_conditions if parsed_conditions else value


def safe_eval(condition, amount):
    try:
        condition = condition.strip()
        operators = {
            '>=': operator.ge,
            '<=': operator.le,
            '>': operator.gt,
            '<': operator.lt,
            '==': operator.eq,
            '!=': operator.ne
        }

        used_op = None
        for op in operators:
            if op in condition:
                used_op = op
                break

        if not used_op:
            raise ValueError(f"No valid operator found in condition: {condition}")

        left, right = [part.strip() for part in condition.split(used_op)]

        if left == 'Amount':
            return operators[used_op](float(amount), float(right))
        elif right == 'Amount':
            return operators[used_op](float(left), float(amount))

        raise ValueError(f"Invalid condition format: {condition}")

    except Exception as e:
        log(LogLevel.ERROR, f"Error evaluating condition: {condition}")
        log(LogLevel.DEBUG, f"Error details: {str(e)}")
        log(LogLevel.DEBUG, f"Amount value: {amount}, Type: {type(amount)}")
        return False


def evaluate_conditional(conditions, amount):
    if not isinstance(conditions, list):
        return conditions

    try:
        for condition, result in conditions:
            if safe_eval(condition, amount):
                return result

        return conditions[-1][1] if conditions else None

    except Exception as e:
        log(LogLevel.ERROR, f"Error in evaluate_conditional: {str(e)}")
        log(LogLevel.DEBUG, f"Conditions: {conditions}")
        log(LogLevel.DEBUG, f"Amount: {amount}")
        return None


def standardize_merchant_name(merchant_name):
    """Standardize merchant names for consistent mapping"""
    if isinstance(merchant_name, str) and (merchant_name.startswith('Facebk') or merchant_name == 'Facebook'):
        return 'Facebook'
    return merchant_name


def create_upload_df(transaction_df, mapping_dict):
    upload_rows = []

    for idx, trans_row in transaction_df.iterrows():
        try:
            standard_merchant_name = standardize_merchant_name(trans_row['Clean Merchant Name'])
            key = (standard_merchant_name, trans_row['Card Name'])
            mapped_values = mapping_dict.get(key)

            new_row = {
                'Date (UTC)': trans_row['Date (UTC)'],
                'Amount': trans_row['Amount'],
                'Clean Merchant Name': trans_row['Clean Merchant Name'],
                'Card Name': trans_row['Card Name']
            }

            if mapped_values:
                for field, value in mapped_values.items():
                    if field in ['GL Name', 'GL Internal ID']:
                        evaluated_value = evaluate_conditional(value, trans_row['Amount'])
                        if evaluated_value is not None:
                            new_row[field] = evaluated_value
                        else:
                            log(LogLevel.WARNING, f"No valid value found for {field} with amount {trans_row['Amount']}")
                    elif field == 'Line Memo':
                        line_memo = value
                        if mapped_values.get('Include Memo') and trans_row.get('Memo'):
                            line_memo = f"{line_memo} - {trans_row['Memo']}"
                        new_row[field] = line_memo
                    elif field != 'Include Memo':
                        new_row[field] = value
            else:
                new_row['Needs Review'] = 'X'
                new_row['Review Reason'] = f"No rules found for {trans_row['Clean Merchant Name']} in the mapping file."

                mapped_fields = ['Merchant Category', 'GL Name', 'GL Internal ID',
                                 'Transaction Cost Center', 'Cost Center Internal ID',
                                 'Customer Internal ID', 'Customer', 'Line Memo']
                for field in mapped_fields:
                    new_row[field] = None

            upload_rows.append(new_row)

        except Exception as e:
            log(LogLevel.ERROR, f"Error processing row {idx}: {str(e)}")
            log(LogLevel.DEBUG, f"Row data: {trans_row}")
            continue

    upload_df = pd.DataFrame(upload_rows)

    if 'Needs Review' in upload_df.columns:
        regular_cols = [col for col in upload_df.columns if col not in ['Needs Review', 'Review Reason']]
        final_cols = regular_cols + ['Needs Review', 'Review Reason']
        upload_df = upload_df[final_cols]

    return upload_df


def process_summit_storage(upload_df):
    summit_count = len(upload_df[upload_df['Merchant Name'] == 'Summit Self Storage'])

    if summit_count != 3:
        if 'Needs Review' not in upload_df.columns:
            upload_df['Needs Review'] = ''
        if 'Review Reason' not in upload_df.columns:
            upload_df['Review Reason'] = ''

        summit_mask = upload_df['Merchant Name'] == 'Summit Self Storage'
        upload_df.loc[summit_mask, 'Needs Review'] = 'X'
        upload_df.loc[
            summit_mask, 'Review Reason'] = f'There are {summit_count} charges for Summit Self Storage. There should be exactly 3.'
    else:
        summit_indices = upload_df[upload_df['Merchant Name'] == 'Summit Self Storage'].index.tolist()
        random.shuffle(summit_indices)

        department_mappings = [
            ('Marketing : Field Marketing', 18),
            ('Marketing : Partnerships', 19),
            ('Marketing : Shopper Marketing', 24)
        ]

        for idx, (dept, dept_id) in zip(summit_indices, department_mappings):
            upload_df.loc[idx, 'Department'] = dept
            upload_df.loc[idx, 'Department Internal ID'] = dept_id

    return upload_df


def main(resume_state=None):
    """
    Main function to execute the Divvy ME transaction processing

    Args:
        resume_state: ScriptState object if resuming from pause, None if starting fresh

    Returns:
        tuple: (exit_code, state) where state is ScriptState if paused, None if completed
    """
    try:
        # Check if we're resuming from a saved state
        if resume_state:
            log(LogLevel.INFO, "Resuming from saved state...")

            # Load state
            upload_df = pd.read_excel(resume_state.upload_template_file)
            csv_upload_base_folder = resume_state.csv_upload_base_folder

            # Jump to phase 2
            return complete_processing(upload_df, csv_upload_base_folder)

        # Phase 1: Initial processing
        log(LogLevel.INFO, "Starting Divvy ME transaction processing...")

        # Get file paths
        transaction_mapping_file = get_transaction_mapping_file()
        transaction_file_folder = get_transaction_file_folder()
        upload_template_file = get_upload_template_file()
        csv_upload_base_folder = get_csv_upload_base_folder()

        # Check for required files
        if not all([transaction_mapping_file, transaction_file_folder, upload_template_file, csv_upload_base_folder]):
            log(LogLevel.ERROR, "One or more required paths could not be found")
            return 1, None

        # Get CSV files
        csv_files = glob.glob(os.path.join(transaction_file_folder, '*.csv'))

        if len(csv_files) == 0:
            log(LogLevel.ERROR,
                "No CSV file found in the transaction folder. Please add a CSV file and run the script again.")
            return 1, None
        elif len(csv_files) > 1:
            log(LogLevel.ERROR,
                "More than one CSV file found in the folder. Please ensure only one CSV file is present.")
            return 1, None

        transaction_file = csv_files[0]
        log(LogLevel.INFO, f"Processing transaction file: {os.path.basename(transaction_file)}")

        # Process the transaction file
        required_columns = ['Date (UTC)', 'Clean Merchant Name', 'Amount', 'Card Name', 'Department', 'GL']
        optional_columns = ['Memo']

        available_columns = pd.read_csv(transaction_file, nrows=0).columns.tolist()
        use_columns = required_columns + [col for col in optional_columns if col in available_columns]

        transaction_df = pd.read_csv(
            transaction_file,
            usecols=use_columns,
            thousands=',',
            converters={'Amount': lambda x: float(x.strip('$()').replace(',', '')) * -1}
        )

        transaction_df['Amount'] = pd.to_numeric(transaction_df['Amount'], errors='coerce')
        transaction_df['Date (UTC)'] = pd.to_datetime(transaction_df['Date (UTC)']).dt.strftime('%m/%d/%Y')

        if 'Memo' not in transaction_df.columns:
            transaction_df['Memo'] = ''

        # Remove Accounts Payable transactions
        ap_rows = transaction_df[transaction_df['Card Name'] == 'Accounts Payable'].copy()
        if not ap_rows.empty:
            log(LogLevel.INFO, f"Removing {len(ap_rows)} Accounts Payable transactions")
            log(LogLevel.DEBUG, f"Total value of removed AP transactions: ${abs(ap_rows['Amount'].sum()):,.2f}")
            transaction_df = transaction_df[transaction_df['Card Name'] != 'Accounts Payable'].copy()

        # Remove negative amount transactions
        negative_rows = transaction_df[transaction_df['Amount'] < 0].copy()
        if not negative_rows.empty:
            log(LogLevel.INFO, f"Removing {len(negative_rows)} transactions with negative amounts")
            log(LogLevel.DEBUG, f"Total value of removed negative transactions: ${negative_rows['Amount'].sum():,.2f}")
            transaction_df = transaction_df[transaction_df['Amount'] >= 0].copy()

        # Read mapping file and process
        log(LogLevel.INFO, "Loading transaction mapping...")
        transaction_mapping_df = pd.read_csv(transaction_mapping_file)
        mapping_dict = create_mapping_dict(transaction_mapping_df)

        # Create upload DataFrame
        log(LogLevel.INFO, "Creating upload data...")
        upload_df = create_upload_df(transaction_df, mapping_dict)

        # Rename columns
        upload_df.rename(columns={
            'Date (UTC)': 'Date',
            'Clean Merchant Name': 'Merchant Name',
            'Transaction Cost Center': 'Department',
            'Cost Center Internal ID': 'Department Internal ID'
        }, inplace=True)

        # Add Vendor Internal ID
        upload_df['Vendor Internal ID'] = 6268
        upload_df.reset_index(drop=True, inplace=True)

        # Create NS Transaction IDs
        dates_dt = pd.to_datetime(upload_df['Date'])
        date_prefix = dates_dt.dt.strftime('%y%m')
        row_suffix = (upload_df.index + 1).map(lambda x: f'{x:05d}')
        upload_df['NS Transaction'] = date_prefix + row_suffix

        # Reorder columns
        cols = ['Vendor Internal ID', 'NS Transaction'] + [col for col in upload_df.columns if
                                                           col not in ['Vendor Internal ID', 'NS Transaction']]
        upload_df = upload_df[cols]

        # Drop Merchant Category if it exists
        if 'Merchant Category' in upload_df.columns:
            upload_df = upload_df.drop(columns=['Merchant Category'])

        # Process Summit Storage special case
        upload_df = process_summit_storage(upload_df)

        # Save to Excel for review
        log(LogLevel.INFO, "Saving data to Excel template for review...")
        upload_df.to_excel(upload_template_file, sheet_name='MVP Logistics', index=False)

        # Open the file for review
        log(LogLevel.INFO, "Opening Excel file for review...")
        os.startfile(upload_template_file)

        # Create state for resume
        state = ScriptState()
        state.upload_df = upload_df
        state.csv_upload_base_folder = csv_upload_base_folder
        state.upload_template_file = upload_template_file
        state.phase = 'review'

        log(LogLevel.INFO,
            "Excel file opened for review. Please review the file, save and close it, then click 'Continue' to proceed.")

        # Return special code to indicate pause
        return 99, state  # -99 indicates "paused for review"

    except Exception as e:
        log(LogLevel.ERROR, f"Unexpected error: {str(e)}")
        return 1, None


def complete_processing(upload_df, csv_upload_base_folder):
    """Complete the processing after Excel review"""
    try:
        log(LogLevel.INFO, "Continuing with processing after review...")

        # Create the primary upload DataFrame
        primary_upload_df = upload_df[[
            'Vendor Internal ID', 'NS Transaction', 'Date', 'Amount',
            'GL Name', 'GL Internal ID', 'Department', 'Department Internal ID',
            'Customer Internal ID', 'Customer', 'Line Memo'
        ]].copy()

        # Create save path based on current date
        current_date = datetime.now()
        year = current_date.strftime("%Y")
        month = current_date.strftime("%Y-%m")
        save_path = os.path.join(csv_upload_base_folder, year, month)

        # Create directories if they don't exist
        os.makedirs(save_path, exist_ok=True)

        # Save the CSV file
        primary_csv_path = os.path.join(save_path, f"{month} Divvy Upload.csv")
        primary_upload_df.to_csv(primary_csv_path, index=False)

        log(LogLevel.SUCCESS, f"File saved successfully: {primary_csv_path}")
        log(LogLevel.INFO, "=" * 80)
        log(LogLevel.SUCCESS, "The file is ready to be uploaded to NetSuite. The script is now complete!")
        log(LogLevel.INFO, "=" * 80)

        return 0, None  # Success, no state to save

    except Exception as e:
        log(LogLevel.ERROR, f"Error during final processing: {str(e)}")
        return 1, None


if __name__ == "__main__":
    # Check if this is a resume operation
    if len(sys.argv) > 1 and sys.argv[1] == "--resume":
        # Load saved state
        state_file = os.path.join(os.path.dirname(__file__), ".divvy_state.pkl")
        if os.path.exists(state_file):
            try:
                saved_state = ScriptState.load(state_file)
                exit_code, _ = main(resume_state=saved_state)
                # Clean up state file after successful completion
                if exit_code == 0:
                    os.remove(state_file)
                sys.exit(exit_code)
            except Exception as e:
                log(LogLevel.ERROR, f"Failed to load saved state: {str(e)}")
                sys.exit(1)
        else:
            log(LogLevel.ERROR, "No saved state found")
            sys.exit(1)
    else:
        # Normal execution
        exit_code, state = main()

        # If paused, save state
        if exit_code == -99 and state:
            state_file = os.path.join(os.path.dirname(__file__), ".divvy_state.pkl")
            state.save(state_file)

        sys.exit(exit_code)
