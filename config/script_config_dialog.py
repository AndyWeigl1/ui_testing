"""Script configuration dialog for non-technical users"""

import customtkinter as ctk
from typing import Dict, Any, Optional, Callable
import json
from pathlib import Path


class ScriptConfigDialog(ctk.CTkToplevel):
    """Dialog for configuring script parameters before execution"""

    def __init__(self, parent, script_info: Dict[str, Any], on_run: Callable = None):
        """Initialize the configuration dialog

        Args:
            parent: Parent window
            script_info: Information about the script including metadata
            on_run: Callback function when user clicks Run
        """
        super().__init__(parent)

        self.script_info = script_info
        self.on_run_callback = on_run
        self.parameter_widgets = {}
        self.result = None

        # Window setup
        self.title(f"Configure: {script_info['metadata']['name']}")
        self.geometry("600x500")
        self.resizable(False, False)

        # Make dialog modal
        self.transient(parent)
        self.grab_set()

        # Center the dialog
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.winfo_screenheight() // 2) - (500 // 2)
        self.geometry(f"+{x}+{y}")

        # Create UI
        self.create_ui()

        # Focus on first parameter input
        if self.parameter_widgets:
            first_widget = next(iter(self.parameter_widgets.values()))
            first_widget.focus_set()

    def create_ui(self):
        """Create the dialog UI"""
        # Main container
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)

        # Header section
        header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        header_frame.grid_columnconfigure(0, weight=1)

        # Script name and description
        name_label = ctk.CTkLabel(
            header_frame,
            text=self.script_info['metadata']['name'],
            font=ctk.CTkFont(size=20, weight="bold")
        )
        name_label.grid(row=0, column=0, sticky="w")

        if self.script_info['metadata'].get('description'):
            desc_label = ctk.CTkLabel(
                header_frame,
                text=self.script_info['metadata']['description'],
                font=ctk.CTkFont(size=12),
                text_color=("gray40", "gray60"),
                wraplength=550,
                justify="left"
            )
            desc_label.grid(row=1, column=0, sticky="w", pady=(5, 0))

        # Category and tags
        info_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        info_frame.grid(row=2, column=0, sticky="w", pady=(10, 0))

        category = self.script_info['metadata'].get('category', 'General')
        category_label = ctk.CTkLabel(
            info_frame,
            text=category,
            font=ctk.CTkFont(size=11),
            fg_color=("#e0e0e0", "#374151"),
            corner_radius=12,
            padx=10,
            pady=2
        )
        category_label.grid(row=0, column=0, padx=(0, 5))

        # Tags
        tags = self.script_info['metadata'].get('tags', [])
        for i, tag in enumerate(tags[:3]):
            tag_label = ctk.CTkLabel(
                info_frame,
                text=f"#{tag}",
                font=ctk.CTkFont(size=10),
                text_color=("#1f6aa5", "#4d94ff")
            )
            tag_label.grid(row=0, column=i + 1, padx=5)

        # Parameters section
        params_container = ctk.CTkFrame(main_frame)
        params_container.grid(row=1, column=0, sticky="nsew")
        params_container.grid_columnconfigure(0, weight=1)
        params_container.grid_rowconfigure(0, weight=1)

        # Scrollable frame for parameters
        scrollable_frame = ctk.CTkScrollableFrame(params_container)
        scrollable_frame.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
        scrollable_frame.grid_columnconfigure(0, weight=1)

        # Create parameter inputs
        parameters = self.script_info['metadata'].get('parameters', {})

        if parameters:
            params_title = ctk.CTkLabel(
                scrollable_frame,
                text="Script Parameters",
                font=ctk.CTkFont(size=16, weight="bold")
            )
            params_title.grid(row=0, column=0, sticky="w", pady=(0, 15))

            row = 1
            for param_name, param_info in parameters.items():
                self.create_parameter_input(scrollable_frame, row, param_name, param_info)
                row += 1
        else:
            # No parameters needed
            no_params_label = ctk.CTkLabel(
                scrollable_frame,
                text="This script doesn't require any parameters.\nClick 'Run Script' to start.",
                font=ctk.CTkFont(size=14),
                text_color=("gray40", "gray60")
            )
            no_params_label.grid(row=0, column=0, pady=50)

        # Advanced options (collapsible)
        self.create_advanced_section(scrollable_frame, row + 1)

        # Button section
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.grid(row=2, column=0, sticky="ew", pady=(20, 0))
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

        # Run button
        run_btn = ctk.CTkButton(
            button_frame,
            text="Run Script",
            width=120,
            command=self.run_script
        )
        run_btn.grid(row=0, column=2, padx=5)

        # Bind Enter key to run
        self.bind("<Return>", lambda e: self.run_script())
        self.bind("<Escape>", lambda e: self.cancel())

    def create_parameter_input(self, parent, row: int, param_name: str, param_info: Dict[str, Any]):
        """Create input widget for a parameter"""
        # Parameter frame
        param_frame = ctk.CTkFrame(parent, fg_color="transparent")
        param_frame.grid(row=row, column=0, sticky="ew", pady=10)
        param_frame.grid_columnconfigure(1, weight=1)

        # Label
        label_text = param_name.replace('_', ' ').title()
        if param_info.get('required', False):
            label_text += " *"

        label = ctk.CTkLabel(
            param_frame,
            text=label_text,
            font=ctk.CTkFont(size=14),
            width=150,
            anchor="w"
        )
        label.grid(row=0, column=0, sticky="w", padx=(0, 20))

        # Input widget based on type
        param_type = param_info.get('type', 'string')

        if param_type == 'file':
            # File selector
            file_frame = ctk.CTkFrame(param_frame, fg_color="transparent")
            file_frame.grid(row=0, column=1, sticky="ew")
            file_frame.grid_columnconfigure(0, weight=1)

            entry = ctk.CTkEntry(file_frame, placeholder_text="Select a file...")
            entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))

            browse_btn = ctk.CTkButton(
                file_frame,
                text="Browse",
                width=80,
                command=lambda e=entry: self.browse_file(e)
            )
            browse_btn.grid(row=0, column=1)

            self.parameter_widgets[param_name] = entry

        elif param_type == 'directory':
            # Directory selector
            dir_frame = ctk.CTkFrame(param_frame, fg_color="transparent")
            dir_frame.grid(row=0, column=1, sticky="ew")
            dir_frame.grid_columnconfigure(0, weight=1)

            entry = ctk.CTkEntry(dir_frame, placeholder_text="Select a directory...")
            entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))

            browse_btn = ctk.CTkButton(
                dir_frame,
                text="Browse",
                width=80,
                command=lambda e=entry: self.browse_directory(e)
            )
            browse_btn.grid(row=0, column=1)

            self.parameter_widgets[param_name] = entry

        elif param_type == 'choice':
            # Dropdown menu
            choices = param_info.get('choices', [])
            var = ctk.StringVar(value=choices[0] if choices else "")

            menu = ctk.CTkOptionMenu(
                param_frame,
                values=choices,
                variable=var
            )
            menu.grid(row=0, column=1, sticky="ew")

            self.parameter_widgets[param_name] = var

        elif param_type == 'boolean':
            # Checkbox
            var = ctk.BooleanVar(value=param_info.get('default', False))

            checkbox = ctk.CTkCheckBox(
                param_frame,
                text="",
                variable=var
            )
            checkbox.grid(row=0, column=1, sticky="w")

            self.parameter_widgets[param_name] = var

        else:
            # Text entry (default)
            entry = ctk.CTkEntry(
                param_frame,
                placeholder_text=param_info.get('placeholder', f"Enter {param_name}...")
            )
            entry.grid(row=0, column=1, sticky="ew")

            # Set default value if provided
            if 'default' in param_info:
                entry.insert(0, str(param_info['default']))

            self.parameter_widgets[param_name] = entry

        # Description
        if param_info.get('description'):
            desc_label = ctk.CTkLabel(
                param_frame,
                text=param_info['description'],
                font=ctk.CTkFont(size=11),
                text_color=("gray30", "gray70"),
                anchor="w"
            )
            desc_label.grid(row=1, column=1, sticky="w", pady=(2, 0))

    def create_advanced_section(self, parent, row: int):
        """Create collapsible advanced options section"""
        # Advanced section frame
        adv_frame = ctk.CTkFrame(parent, fg_color="transparent")
        adv_frame.grid(row=row, column=0, sticky="ew", pady=(20, 0))
        adv_frame.grid_columnconfigure(0, weight=1)

        # Toggle button
        self.advanced_expanded = False
        self.toggle_btn = ctk.CTkButton(
            adv_frame,
            text="▶ Advanced Options",
            command=self.toggle_advanced,
            fg_color="transparent",
            text_color=("#1f6aa5", "#4d94ff"),
            hover_color=("gray90", "gray20"),
            anchor="w",
            width=200
        )
        self.toggle_btn.grid(row=0, column=0, sticky="w")

        # Advanced content (initially hidden)
        self.advanced_content = ctk.CTkFrame(adv_frame)
        self.advanced_content.grid_columnconfigure(1, weight=1)

        # Timeout setting
        timeout_label = ctk.CTkLabel(
            self.advanced_content,
            text="Timeout (seconds):",
            font=ctk.CTkFont(size=12)
        )
        timeout_label.grid(row=0, column=0, sticky="w", padx=(20, 10), pady=5)

        self.timeout_var = ctk.StringVar(value="300")
        timeout_entry = ctk.CTkEntry(
            self.advanced_content,
            textvariable=self.timeout_var,
            width=100
        )
        timeout_entry.grid(row=0, column=1, sticky="w", pady=5)

        # Working directory
        workdir_label = ctk.CTkLabel(
            self.advanced_content,
            text="Working Directory:",
            font=ctk.CTkFont(size=12)
        )
        workdir_label.grid(row=1, column=0, sticky="w", padx=(20, 10), pady=5)

        self.workdir_var = ctk.StringVar(value="")
        workdir_entry = ctk.CTkEntry(
            self.advanced_content,
            textvariable=self.workdir_var,
            placeholder_text="Default: script directory"
        )
        workdir_entry.grid(row=1, column=1, sticky="ew", pady=5)

    def toggle_advanced(self):
        """Toggle advanced options visibility"""
        self.advanced_expanded = not self.advanced_expanded

        if self.advanced_expanded:
            self.toggle_btn.configure(text="▼ Advanced Options")
            self.advanced_content.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        else:
            self.toggle_btn.configure(text="▶ Advanced Options")
            self.advanced_content.grid_forget()

    def browse_file(self, entry_widget):
        """Browse for a file"""
        from tkinter import filedialog

        filename = filedialog.askopenfilename(
            title="Select File",
            filetypes=[("All files", "*.*")]
        )

        if filename:
            entry_widget.delete(0, "end")
            entry_widget.insert(0, filename)

    def browse_directory(self, entry_widget):
        """Browse for a directory"""
        from tkinter import filedialog

        directory = filedialog.askdirectory(title="Select Directory")

        if directory:
            entry_widget.delete(0, "end")
            entry_widget.insert(0, directory)

    def get_parameter_values(self) -> Dict[str, Any]:
        """Get values from all parameter widgets"""
        values = {}

        for param_name, widget in self.parameter_widgets.items():
            if isinstance(widget, ctk.CTkEntry):
                values[param_name] = widget.get()
            elif isinstance(widget, (ctk.StringVar, ctk.BooleanVar)):
                values[param_name] = widget.get()

        return values

    def validate_parameters(self) -> bool:
        """Validate parameter values"""
        parameters = self.script_info['metadata'].get('parameters', {})
        values = self.get_parameter_values()

        for param_name, param_info in parameters.items():
            if param_info.get('required', False):
                value = values.get(param_name, '')
                if not value:
                    self.show_error(f"'{param_name.replace('_', ' ').title()}' is required")
                    return False

        return True

    def show_error(self, message: str):
        """Show error message to user"""
        error_dialog = ctk.CTkInputDialog(
            text=message,
            title="Validation Error"
        )
        error_dialog.get_input()

    def run_script(self):
        """Validate and run the script"""
        if not self.validate_parameters():
            return

        # Prepare result
        self.result = {
            'parameters': self.get_parameter_values(),
            'timeout': int(self.timeout_var.get()) if hasattr(self, 'timeout_var') else 300,
            'working_directory': self.workdir_var.get() if hasattr(self, 'workdir_var') else None
        }

        # Call callback if provided
        if self.on_run_callback:
            self.on_run_callback(self.result)

        self.destroy()

    def cancel(self):
        """Cancel the dialog"""
        self.result = None
        self.destroy()

    def get_result(self) -> Optional[Dict[str, Any]]:
        """Get the dialog result"""
        return self.result