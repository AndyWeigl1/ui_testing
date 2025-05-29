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
# - parameters: Future use for script configuration
# - configurable_paths: Dictionary of paths that can be configured

AVAILABLE_SCRIPTS = {
    "Simulation": {
        "path": None,  # None triggers simulation mode
        "description": "Built-in simulation for testing",
        "category": "Testing",
        "parameters": {}
    },

    "Test Data Processor": {
        "path": "scripts/test_data_processor.py",
        "description": "Processes data and demonstrates log levels",
        "category": "Data Processing",
        "parameters": {
            "batch_size": 100,
            "output_format": "json"
        }
    },

    "Schneider Attachments Saver": {
        "path": "scripts/schneider_save_attachments.py",
        "description": "Saves email attachments from selected Outlook emails to Schneider import bills folder",
        "category": "Email Processing",
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
        "description": "Saves email attachments from selected Outlook emails to Element Food Solutions folders",
        "category": "Email Processing",
        "parameters": {},
        "configurable_paths": {
            "od_invoice_folder": {
                "description": "Main Element Food Solutions folder for organized invoice storage",
                "default_components": ["Waffle-Dry", "Element Food Solutions"],
                "type": "directory"
            },
            "data_imports_folder": {
                "description": "Data imports folder for Element Food Solutions invoices",
                "default_components": ["Waffle-Dry", "Element Food Solutions", "Data Imports"],
                "type": "directory"
            }
        }
    },

    "Honeyville Attachments Saver": {
        "path": "scripts/honeyville_save_attachments.py",
        "description": "Saves email attachments from selected Outlook emails to Honeyville folders",
        "category": "Email Processing",
        "parameters": {},
        "configurable_paths": {
            "shipments_folder": {
                "description": "Honeyville shipments folder for organized invoice storage",
                "default_components": ["Waffle-Dry", "Honeyville", "Shipments to RJW"],
                "type": "directory"
            },
            "data_imports_folder": {
                "description": "Data imports folder for Honeyville invoices",
                "default_components": ["Waffle-Dry", "Honeyville", "Data Imports"],
                "type": "directory"
            }
        }
    },

    "File Organizer": {
        "path": "scripts/file_organizer.py",
        "description": "Organizes files into categories",
        "category": "File Operations",
        "parameters": {
            "source_dir": "./",
            "create_backup": True
        }
    },

    # Add new scripts here:
    # "CSV Report Generator": {
    #     "path": "scripts/csv_report_gen.py",
    #     "description": "Generates reports from CSV files",
    #     "category": "Reporting",
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

# Default script to select on startup
DEFAULT_SCRIPT = "Simulation"
