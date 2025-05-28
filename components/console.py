"""Enhanced output console component with developer mode support"""

import customtkinter as ctk
import tkinter as tk
from datetime import datetime
from config.settings import (
    DEFAULT_FONT_FAMILY, DEFAULT_FONT_SIZE, MIN_FONT_SIZE,
    MAX_FONT_SIZE, FONT_SIZE_STEPS
)
from config.themes import COLORS
from typing import Literal, Optional


# Define log levels
class LogLevel:
    DEBUG = "debug"      # Detailed info for developers
    INFO = "info"        # General information
    SUCCESS = "success"  # Success messages
    WARNING = "warning"  # Warning messages
    ERROR = "error"      # Error messages
    SYSTEM = "system"    # System messages


class OutputConsole(ctk.CTkFrame):
    """A console widget for displaying script output with filtering based on developer mode"""

    def __init__(self, master, state_manager=None, **kwargs):
        super().__init__(master, **kwargs)

        # Store state manager reference
        self.state_manager = state_manager

        # Track developer mode state
        self.developer_mode = False
        if self.state_manager:
            self.developer_mode = self.state_manager.get('developer_mode', False)
            self.state_manager.subscribe('developer_mode', self.on_developer_mode_changed)

        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Create header with controls
        self.create_header()

        # Create output display
        self.create_output_display()

        # Add welcome message
        self.add_output("Welcome to Script Runner! Click 'Run' to start your script.", LogLevel.SYSTEM)

    def create_header(self):
        """Create the header with font controls, developer mode toggle, and export button"""
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1)

        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text="Output Console",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.grid(row=0, column=0, sticky="w")

        # Developer mode toggle
        self.dev_mode_var = ctk.BooleanVar(value=self.developer_mode)
        dev_mode_switch = ctk.CTkSwitch(
            header_frame,
            text="Developer Mode",
            variable=self.dev_mode_var,
            command=self.toggle_developer_mode,
            button_color="#1f6aa5",
            progress_color="#144870",
            width=48,
            height=24
        )
        dev_mode_switch.grid(row=0, column=1, padx=10)

        # Font size controls
        font_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        font_frame.grid(row=0, column=2, padx=10)

        ctk.CTkLabel(font_frame, text="Font Size:").grid(row=0, column=0, padx=5)

        self.font_size_var = tk.IntVar(value=DEFAULT_FONT_SIZE)
        font_size_slider = ctk.CTkSlider(
            font_frame,
            from_=MIN_FONT_SIZE,
            to=MAX_FONT_SIZE,
            number_of_steps=FONT_SIZE_STEPS,
            variable=self.font_size_var,
            command=self.update_font_size,
            width=100
        )
        font_size_slider.grid(row=0, column=1, padx=5)

        # Export button
        self.export_btn = ctk.CTkButton(
            header_frame,
            text="Export",
            width=80,
            height=28,
            command=self.export_output
        )
        self.export_btn.grid(row=0, column=3, padx=5)

    def create_output_display(self):
        """Create the text widget for output display"""
        self.output_text = ctk.CTkTextbox(
            self,
            font=ctk.CTkFont(family=DEFAULT_FONT_FAMILY, size=DEFAULT_FONT_SIZE),
            wrap="word",
            state="disabled"
        )
        self.output_text.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")

    def update_font_size(self, value):
        """Update the font size of the output text"""
        font_size = int(value)
        self.output_text.configure(font=ctk.CTkFont(family=DEFAULT_FONT_FAMILY, size=font_size))

    def toggle_developer_mode(self):
        """Toggle developer mode on/off"""
        self.developer_mode = self.dev_mode_var.get()
        if self.state_manager:
            self.state_manager.set('developer_mode', self.developer_mode)

        # Add a system message indicating the mode change
        mode_text = "enabled" if self.developer_mode else "disabled"
        self.add_output(f"Developer mode {mode_text}", LogLevel.SYSTEM)

        # If turning off developer mode, add a hint about hidden messages
        if not self.developer_mode:
            self.add_output("Debug messages are now hidden. Enable developer mode to see detailed output.", LogLevel.INFO)

    def on_developer_mode_changed(self, value):
        """Handle developer mode state changes from state manager"""
        self.developer_mode = value
        self.dev_mode_var.set(value)

    def should_display_message(self, msg_type: str) -> bool:
        """Determine if a message should be displayed based on its type and current mode"""
        # Always show these message types
        always_show = [LogLevel.INFO, LogLevel.SUCCESS, LogLevel.WARNING, LogLevel.ERROR, LogLevel.SYSTEM]

        # Only show debug messages in developer mode
        if msg_type == LogLevel.DEBUG:
            return self.developer_mode

        # Show all other standard messages
        return msg_type in always_show

    def add_output(self, message: str, msg_type: str = LogLevel.INFO, force_display: bool = False):
        """Add a message to the output console with timestamp and filtering

        Args:
            message: The message to display
            msg_type: The type/level of the message (debug, info, success, warning, error, system)
            force_display: If True, displays the message regardless of developer mode setting
        """
        # Check if message should be displayed
        if not force_display and not self.should_display_message(msg_type):
            return

        timestamp = datetime.now().strftime("%H:%M:%S")

        # Enhanced color coding based on message type
        color_map = {
            LogLevel.DEBUG: ("#666666", "#999999"),     # Gray for debug
            LogLevel.INFO: COLORS.get("output_info", ""),
            LogLevel.SUCCESS: COLORS["output_success"],
            LogLevel.WARNING: COLORS["output_warning"],
            LogLevel.ERROR: COLORS["output_error"],
            LogLevel.SYSTEM: COLORS["output_system"]
        }

        # Prefixes for different message types in developer mode
        prefix_map = {
            LogLevel.DEBUG: "[DEBUG] ",
            LogLevel.WARNING: "[WARN] ",
            LogLevel.ERROR: "[ERROR] ",
        }

        self.output_text.configure(state="normal")

        # Add timestamp
        self.output_text.insert("end", f"[{timestamp}] ", "timestamp")

        # Add prefix if in developer mode
        if self.developer_mode and msg_type in prefix_map:
            self.output_text.insert("end", prefix_map[msg_type], msg_type + "_prefix")
            # Configure prefix color
            prefix_color = color_map.get(msg_type, "")
            if prefix_color:
                self.output_text.tag_config(msg_type + "_prefix", foreground=prefix_color)

        # Add message with color if specified
        color = color_map.get(msg_type)
        if color:
            # Handle tuple colors (light, dark theme)
            if isinstance(color, tuple):
                # Get current theme from state manager if available
                theme = "dark"
                if self.state_manager:
                    theme = self.state_manager.get('theme', 'dark')
                color = color[1] if theme == "dark" else color[0]

            self.output_text.insert("end", f"{message}\n", msg_type)
            self.output_text.tag_config(msg_type, foreground=color)
        else:
            self.output_text.insert("end", f"{message}\n")

        # Configure timestamp appearance
        self.output_text.tag_config("timestamp", foreground=COLORS["output_timestamp"])

        # Auto-scroll to bottom
        self.output_text.see("end")
        self.output_text.configure(state="disabled")

    def clear(self):
        """Clear all output from the console"""
        self.output_text.configure(state="normal")
        self.output_text.delete("1.0", "end")
        self.output_text.configure(state="disabled")

    def export_output(self):
        """Export output to a file"""
        from tkinter import filedialog

        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )

        if filename:
            content = self.output_text.get("1.0", "end-1c")
            with open(filename, "w") as f:
                f.write(content)
            self.add_output(f"Output exported to: {filename}", LogLevel.SUCCESS)

    def get_content(self):
        """Get the current content of the console"""
        return self.output_text.get("1.0", "end-1c")
