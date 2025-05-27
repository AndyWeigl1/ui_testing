"""
Utility functions for managing SOPs
Save this as utils/sop_manager.py
"""

import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime


class SOPManager:
    """Manager class for handling SOP operations"""

    def __init__(self, sops_file_path: str = "data/sops.json"):
        """Initialize the SOP Manager

        Args:
            sops_file_path: Path to the JSON file storing SOPs
        """
        self.sops_file_path = sops_file_path
        self.ensure_data_directory()
        self.sops = self.load_sops()

    def ensure_data_directory(self):
        """Ensure the data directory exists"""
        directory = os.path.dirname(self.sops_file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)

    def load_sops(self) -> List[Dict[str, Any]]:
        """Load SOPs from the JSON file"""
        if os.path.exists(self.sops_file_path):
            try:
                with open(self.sops_file_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading SOPs: {e}")
                return []
        return []

    def save_sops(self):
        """Save SOPs to the JSON file"""
        try:
            with open(self.sops_file_path, 'w') as f:
                json.dump(self.sops, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving SOPs: {e}")
            return False

    def add_sop(self, sop_data: Dict[str, Any]) -> bool:
        """Add a new SOP

        Args:
            sop_data: Dictionary containing SOP information

        Returns:
            True if successful, False otherwise
        """
        # Validate required fields
        required_fields = ['id', 'title', 'description', 'category', 'link']
        for field in required_fields:
            if field not in sop_data:
                print(f"Missing required field: {field}")
                return False

        # Check for duplicate ID
        if any(sop['id'] == sop_data['id'] for sop in self.sops):
            print(f"SOP with ID '{sop_data['id']}' already exists")
            return False

        # Add metadata
        sop_data['created_at'] = datetime.now().isoformat()
        sop_data['updated_at'] = datetime.now().isoformat()

        # Add default values for optional fields
        sop_data.setdefault('difficulty', 'Beginner')
        sop_data.setdefault('duration', '15 min')
        sop_data.setdefault('icon', '📄')
        sop_data.setdefault('tags', [])

        self.sops.append(sop_data)
        return self.save_sops()

    def update_sop(self, sop_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing SOP

        Args:
            sop_id: ID of the SOP to update
            updates: Dictionary of fields to update

        Returns:
            True if successful, False otherwise
        """
        for i, sop in enumerate(self.sops):
            if sop['id'] == sop_id:
                # Update fields
                self.sops[i].update(updates)
                self.sops[i]['updated_at'] = datetime.now().isoformat()
                return self.save_sops()

        print(f"SOP with ID '{sop_id}' not found")
        return False

    def remove_sop(self, sop_id: str) -> bool:
        """Remove an SOP

        Args:
            sop_id: ID of the SOP to remove

        Returns:
            True if successful, False otherwise
        """
        original_count = len(self.sops)
        self.sops = [sop for sop in self.sops if sop['id'] != sop_id]

        if len(self.sops) < original_count:
            return self.save_sops()

        print(f"SOP with ID '{sop_id}' not found")
        return False

    def get_sop(self, sop_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific SOP by ID"""
        for sop in self.sops:
            if sop['id'] == sop_id:
                return sop
        return None

    def get_all_sops(self) -> List[Dict[str, Any]]:
        """Get all SOPs"""
        return self.sops

    def get_sops_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get SOPs filtered by category"""
        return [sop for sop in self.sops if sop['category'] == category]

    def get_categories(self) -> List[str]:
        """Get all unique categories"""
        return list(set(sop['category'] for sop in self.sops))

    def import_from_csv(self, csv_path: str) -> int:
        """Import SOPs from a CSV file

        Returns:
            Number of SOPs imported
        """
        import csv

        imported_count = 0
        try:
            with open(csv_path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Convert CSV row to SOP format
                    sop_data = {
                        'id': row.get('id', '').lower().replace(' ', '_'),
                        'title': row.get('title', ''),
                        'description': row.get('description', ''),
                        'category': row.get('category', 'General'),
                        'difficulty': row.get('difficulty', 'Beginner'),
                        'duration': row.get('duration', '15 min'),
                        'link': row.get('link', ''),
                        'icon': row.get('icon', '📄'),
                        'tags': row.get('tags', '').split(',') if row.get('tags') else []
                    }

                    if self.add_sop(sop_data):
                        imported_count += 1

        except Exception as e:
            print(f"Error importing from CSV: {e}")

        return imported_count


# Example usage functions
def quick_add_sop(title: str, description: str, link: str, category: str = "General"):
    """Quick function to add an SOP with minimal information"""
    manager = SOPManager()

    sop_data = {
        'id': title.lower().replace(' ', '_'),
        'title': title,
        'description': description,
        'category': category,
        'link': link
    }

    if manager.add_sop(sop_data):
        print(f"Successfully added SOP: {title}")
    else:
        print(f"Failed to add SOP: {title}")


def bulk_add_sops(sops_list: List[Dict[str, Any]]):
    """Add multiple SOPs at once"""
    manager = SOPManager()

    success_count = 0
    for sop in sops_list:
        if manager.add_sop(sop):
            success_count += 1

    print(f"Successfully added {success_count}/{len(sops_list)} SOPs")


# Example: Adding a new SOP programmatically
if __name__ == "__main__":
    # Example 1: Add a single SOP
    quick_add_sop(
        title="Email Automation Guide",
        description="Learn how to automate email sending and processing",
        link="https://example.com/sop/email-automation",
        category="Integration"
    )

    # Example 2: Add multiple SOPs
    new_sops = [
        {
            'id': 'log_analysis',
            'title': 'Log Analysis Tutorial',
            'description': 'Analyze and extract insights from log files',
            'category': 'Data Processing',
            'difficulty': 'Intermediate',
            'duration': '20 min',
            'link': 'https://example.com/sop/log-analysis',
            'icon': '📋',
            'tags': ['Logs', 'Analysis', 'Debugging']
        },
        {
            'id': 'testing_automation',
            'title': 'Automated Testing Setup',
            'description': 'Set up automated testing for your scripts',
            'category': 'Development',
            'difficulty': 'Advanced',
            'duration': '40 min',
            'link': 'https://example.com/sop/testing-automation',
            'icon': '🧪',
            'tags': ['Testing', 'QA', 'Automation']
        }
    ]

    bulk_add_sops(new_sops)