"""
Script settings manager for storing and retrieving script-specific configurations
"""

import json
import os
from typing import Dict, Any, Optional


class ScriptSettingsManager:
    """Manages persistent settings for individual scripts"""

    def __init__(self, settings_dir: str = "config/script_settings"):
        """Initialize the settings manager

        Args:
            settings_dir: Directory to store script settings files
        """
        self.settings_dir = settings_dir
        self.ensure_settings_directory()

    def ensure_settings_directory(self):
        """Ensure the settings directory exists"""
        if not os.path.exists(self.settings_dir):
            os.makedirs(self.settings_dir)

    def get_settings_file_path(self, script_name: str) -> str:
        """Get the settings file path for a script

        Args:
            script_name: Name of the script

        Returns:
            Path to the settings file
        """
        # Sanitize script name for filename
        safe_name = script_name.lower().replace(" ", "_").replace("/", "_")
        return os.path.join(self.settings_dir, f"{safe_name}_settings.json")

    def load_settings(self, script_name: str) -> Dict[str, Any]:
        """Load settings for a specific script

        Args:
            script_name: Name of the script

        Returns:
            Dictionary of settings
        """
        settings_file = self.get_settings_file_path(script_name)

        if os.path.exists(settings_file):
            try:
                with open(settings_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading settings for {script_name}: {e}")
                return {}

        return {}

    def save_settings(self, script_name: str, settings: Dict[str, Any]) -> bool:
        """Save settings for a specific script

        Args:
            script_name: Name of the script
            settings: Dictionary of settings to save

        Returns:
            True if successful, False otherwise
        """
        settings_file = self.get_settings_file_path(script_name)

        try:
            with open(settings_file, 'w') as f:
                json.dump(settings, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving settings for {script_name}: {e}")
            return False

    def get_setting(self, script_name: str, key: str, default: Any = None) -> Any:
        """Get a specific setting value

        Args:
            script_name: Name of the script
            key: Setting key
            default: Default value if setting not found

        Returns:
            Setting value or default
        """
        settings = self.load_settings(script_name)
        return settings.get(key, default)

    def set_setting(self, script_name: str, key: str, value: Any) -> bool:
        """Set a specific setting value

        Args:
            script_name: Name of the script
            key: Setting key
            value: Setting value

        Returns:
            True if successful, False otherwise
        """
        settings = self.load_settings(script_name)
        settings[key] = value
        return self.save_settings(script_name, settings)

    def has_settings(self, script_name: str) -> bool:
        """Check if a script has saved settings

        Args:
            script_name: Name of the script

        Returns:
            True if settings exist, False otherwise
        """
        return os.path.exists(self.get_settings_file_path(script_name))


# Global instance
_settings_manager = None


def get_settings_manager() -> ScriptSettingsManager:
    """Get the global settings manager instance"""
    global _settings_manager
    if _settings_manager is None:
        _settings_manager = ScriptSettingsManager()
    return _settings_manager