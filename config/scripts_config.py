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
    "Reporting",
    "System",
    "Web Automation",
    "File Operations",
    "Integration"
]

# Default script to select on startup
DEFAULT_SCRIPT = "Simulation"