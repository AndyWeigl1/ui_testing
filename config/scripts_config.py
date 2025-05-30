"""
Script configuration for the Script Runner application
Add new scripts here to make them available in the dropdown
"""

# Script definitions
# Each script needs:
# - Display name (key): What appears in the dropdown
# - path: Path to the script file (None for simulation)
# - description: Brief description of what the script does
# - category: Type of script (for future filtering)
# - tags: List of searchable tags for the script
# - parameters: Future use for script configuration
# - configurable_paths: Dictionary of paths that can be configured

AVAILABLE_SCRIPTS = {
    # "Simulation": {
    #     "path": None,  # None triggers simulation mode
    #     "description": "Built-in simulation for testing",
    #     "category": "Testing",
    #     "tags": ["test", "simulation", "demo", "built-in"],
    #     "parameters": {}
    # },
    #
    # "Test Data Processor": {
    #     "path": "scripts/test_data_processor.py",
    #     "description": "Processes data and demonstrates log levels",
    #     "category": "Data Processing",
    #     "tags": ["data", "processing", "csv", "logs", "test"],
    #     "parameters": {
    #         "batch_size": 100,
    #         "output_format": "json"
    #     }
    # },

    "Schneider Attachments Saver": {
        "path": "scripts/schneider_save_attachments.py",
        "description": "Saves email attachments from selected Outlook emails to Schneider import bills folder",
        "category": "Email Processing",
        "tags": ["email", "outlook", "attachments", "schneider", "automation"],
        "parameters": {},
        "configurable_paths": {
            "import_bills_folder": {
                "description": "Folder where email attachments will be saved",
                "default_components": ["Vendors", "Schneider National Inc", "Imports", "Bills"],
                "type": "directory"
            },
            "schneider_report_folder": {
                "description": "Folder containing Schneider reports",
                "default_components": ["Vendors", "Schneider National Inc", "Imports", "Schneider Report"],
                "type": "directory"
            },
            "csv_uploads_folder": {
                "description": "Base folder for CSV uploads",
                "default_components": ["Vendors", "Schneider National Inc", "Imports", "CSV Uploads"],
                "type": "directory"
            }
        }
    },

    "EFS Attachments Saver": {
        "path": "scripts/efs_save_attachments.py",
        "description": "Saves email attachments from Outlook to Element Food Solutions folders",
        "category": "Email Processing",
        "tags": ["email", "outlook", "attachments", "efs", "element", "food", "pdf"],
        "parameters": {},
        "configurable_paths": {
            "od_invoice_folder": {
                "description": "Element Food Solutions main folder",
                "default_components": ["Waffle-Dry", "Element Food Solutions"],
                "type": "directory"
            },
            "data_imports_folder": {
                "description": "Element Food Solutions data imports folder",
                "default_components": ["Waffle-Dry", "Element Food Solutions", "Data Imports"],
                "type": "directory"
            }
        }
    },

    "Honeyville Attachments Saver": {
        "path": "scripts/honeyville_save_attachments.py",
        "description": "Saves email attachments from Outlook to Honeyville folders",
        "category": "Email Processing",
        "tags": ["email", "outlook", "attachments", "honeyville", "pdf", "invoices"],
        "parameters": {},
        "configurable_paths": {
            "shipments_folder": {
                "description": "Honeyville shipments folder",
                "default_components": ["Waffle-Dry", "Honeyville", "Shipments to RJW"],
                "type": "directory"
            },
            "data_imports_folder": {
                "description": "Honeyville data imports folder",
                "default_components": ["Waffle-Dry", "Honeyville", "Data Imports"],
                "type": "directory"
            }
        }
    },

    "Divvy ME Transaction Upload": {
        "path": "scripts/divvy_me_transaction_upload.py",
        "description": "Processes Divvy transaction files and creates upload files for NetSuite with review step",
        "category": "Financial Processing",
        "tags": ["divvy", "transactions", "netsuite", "upload", "financial", "excel"],
        "parameters": {},
        "configurable_paths": {
            "transaction_mapping_file": {
                "description": "CSV file containing merchant to GL mapping rules",
                "default_components": ["Banking", "Bill Divvy", "Imports", "Excel Files", "Transaction Mapping.csv"],
                "type": "file"
            },
            "transaction_file_folder": {
                "description": "Folder containing transaction CSV files to process",
                "default_components": ["Banking", "Bill Divvy", "Imports", "Transaction File"],
                "type": "directory"
            },
            "upload_template_file": {
                "description": "Excel template file for reviewing transactions",
                "default_components": ["Banking", "Bill Divvy", "Imports", "Divvy ME Upload Template.xlsx"],
                "type": "file"
            },
            "csv_upload_base_folder": {
                "description": "Base folder where processed CSV files will be saved",
                "default_components": ["Banking", "Bill Divvy"],
                "type": "directory"
            }
        }
    }

    # "File Organizer": {
    #     "path": "scripts/file_organizer.py",
    #     "description": "Organizes files into categories",
    #     "category": "File Operations",
    #     "tags": ["files", "organization", "sorting", "cleanup", "automation"],
    #     "parameters": {
    #         "source_dir": "./",
    #         "create_backup": True
    #     }
    # },

    # Add new scripts here:
    # "CSV Report Generator": {
    #     "path": "scripts/csv_report_gen.py",
    #     "description": "Generates reports from CSV files",
    #     "category": "Reporting",
    #     "tags": ["csv", "reports", "data", "analysis", "export"],
    #     "parameters": {
    #         "input_file": "data.csv",
    #         "output_format": "pdf"
    #     },
    #     "configurable_paths": {
    #         "reports_output_folder": {
    #             "description": "Folder where generated reports will be saved",
    #             "default_components": ["Reports", "Generated"],
    #             "type": "directory"
    #         }
    #     }
    # },

    # "Database Backup": {
    #     "path": "scripts/db_backup.py",
    #     "description": "Backs up database to specified location",
    #     "category": "System",
    #     "tags": ["database", "backup", "system", "maintenance", "sql"],
    #     "parameters": {
    #         "db_name": "production",
    #         "backup_path": "/backups/"
    #     }
    # },
}

# Script categories for future filtering
SCRIPT_CATEGORIES = [
    "Testing",
    "Data Processing",
    "Email Processing",
    "Reporting",
    "System",
    "Web Automation",
    "File Operations",
    "Integration"
]

# Tag colors for visual distinction
TAG_COLORS = {
    "test": "#4CAF50",      # Green
    "email": "#2196F3",     # Blue
    "data": "#FF9800",      # Orange
    "automation": "#9C27B0", # Purple
    "files": "#795548",     # Brown
    "system": "#F44336",    # Red
    "pdf": "#607D8B",       # Blue Grey
    "outlook": "#0078D4",   # Outlook Blue
    # Default color for unspecified tags
    "default": "#757575"    # Grey
}

# Default script to select on startup
DEFAULT_SCRIPT = "Simulation"
