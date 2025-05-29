"""
Simple path configuration dialog for script settings
"""

import customtkinter as ctk
from typing import Dict, Any, Optional
from tkinter import filedialog
import os


class PathConfigDialog(ctk.CTkToplevel):
    """Simple dialog for configuring script paths"""

    def __init__(self, parent, script_name: str, configurable_paths: Dict[str, Any], current_settings: Dict[str, str]):
        """Initialize the path configuration dialog

        Args:
            parent: Parent window
            script_name: Name of the script being configured
            configurable_paths: Dictionary of configurable paths from script config
            current_settings: Current saved settings for the script
        """
        super().__init__(parent)

        self.script_name = script_name
        self.configurable_paths = configurable_paths
        self.current_settings = current_settings
        self.path_widgets = {}
        self.result = None

        # Window setup
        self.title(f"Configure Paths: {script_name}")
        self.geometry("700x400")
        self.resizable(False, False)

        # Make dialog modal
        self.transient(parent)
        self.grab_set()

        # Center the dialog
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (700 // 2)
        y = (self.winfo_screenheight() // 2) - (400 // 2)
        self.geometry(f"+{x}+{y}")

        # Create UI
        self.create_ui()

    def create_ui(self):
        """Create the dialog UI"""
        # Main container
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)

        # Header
        header_label = ctk.CTkLabel(
            main_frame,
            text=f"Configure Paths for {self.script_name}",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        header_label.grid(row=0, column=0, sticky="w", pady=(0, 10))

        # Instruction
        instruction_label = ctk.CTkLabel(
            main_frame,
            text="Configure the file paths used by this script. Leave blank to use default paths.",
            font=ctk.CTkFont(size=12),
            text_color=("gray40", "gray60")
        )
        instruction_label.grid(row=1, column=0, sticky="w", pady=(0, 20))

        # Scrollable frame for paths
        scroll_frame = ctk.CTkScrollableFrame(main_frame)
        scroll_frame.grid(row=2, column=0, sticky="nsew", pady=(0, 20))
        scroll_frame.grid_columnconfigure(0, weight=1)

        # Create path inputs
        row = 0
        for path_key, path_info in self.configurable_paths.items():
            self.create_path_input(scroll_frame, row, path_key, path_info)
            row += 1

        # Button frame
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.grid(row=3, column=0, sticky="ew")
        button_frame.grid_columnconfigure(0, weight=1)

        # Cancel button
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            width=100,
            fg_color=("gray70", "gray30"),
            command=self.cancel
        )
        cancel_btn.grid(row=0, column=1, padx=5)

        # Save button
        save_btn = ctk.CTkButton(
            button_frame,
            text="Save",
            width=100,
            command=self.save_settings
        )
        save_btn.grid(row=0, column=2, padx=5)

    def create_path_input(self, parent, row: int, path_key: str, path_info: Dict[str, Any]):
        """Create input widget for a path configuration"""
        # Container frame
        container = ctk.CTkFrame(parent)
        container.grid(row=row, column=0, sticky="ew", pady=10)
        container.grid_columnconfigure(0, weight=1)

        # Label
        label_text = path_key.replace('_', ' ').title()
        label = ctk.CTkLabel(
            container,
            text=label_text,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        label.grid(row=0, column=0, sticky="w", pady=(0, 5))

        # Description
        if path_info.get('description'):
            desc_label = ctk.CTkLabel(
                container,
                text=path_info['description'],
                font=ctk.CTkFont(size=11),
                text_color=("gray30", "gray70")
            )
            desc_label.grid(row=1, column=0, sticky="w", pady=(0, 5))

        # Path input frame
        input_frame = ctk.CTkFrame(container, fg_color="transparent")
        input_frame.grid(row=2, column=0, sticky="ew")
        input_frame.grid_columnconfigure(0, weight=1)

        # Entry
        entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="Click Browse to select folder or leave blank for default"
        )
        entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))

        # Set current value if exists
        current_value = self.current_settings.get(path_key, "")
        if current_value:
            entry.insert(0, current_value)

        # Browse button
        browse_btn = ctk.CTkButton(
            input_frame,
            text="Browse",
            width=80,
            command=lambda e=entry: self.browse_folder(e)
        )
        browse_btn.grid(row=0, column=1)

        # Clear button
        clear_btn = ctk.CTkButton(
            input_frame,
            text="Clear",
            width=60,
            fg_color=("gray70", "gray30"),
            command=lambda e=entry: self.clear_entry(e)
        )
        clear_btn.grid(row=0, column=2, padx=(5, 0))

        # Store widget reference
        self.path_widgets[path_key] = entry

    def browse_folder(self, entry_widget):
        """Browse for a folder"""
        # Get initial directory from current entry value
        current = entry_widget.get()
        initial_dir = os.path.dirname(current) if current and os.path.exists(current) else None

        folder = filedialog.askdirectory(
            title="Select Folder",
            initialdir=initial_dir
        )

        if folder:
            entry_widget.delete(0, "end")
            entry_widget.insert(0, folder)

    def clear_entry(self, entry_widget):
        """Clear an entry widget"""
        entry_widget.delete(0, "end")

    def get_path_values(self) -> Dict[str, str]:
        """Get values from all path widgets"""
        values = {}
        for path_key, widget in self.path_widgets.items():
            value = widget.get().strip()
            if value:  # Only save non-empty values
                values[path_key] = value
        return values

    def save_settings(self):
        """Save the configured paths"""
        self.result = self.get_path_values()
        self.destroy()

    def cancel(self):
        """Cancel without saving"""
        self.result = None
        self.destroy()

    def get_result(self) -> Optional[Dict[str, str]]:
        """Get the dialog result"""
        return self.result