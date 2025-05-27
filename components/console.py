"""Output console component for displaying script output"""

import customtkinter as ctk
import tkinter as tk
from datetime import datetime
from config.settings import (
    DEFAULT_FONT_FAMILY, DEFAULT_FONT_SIZE, MIN_FONT_SIZE,
    MAX_FONT_SIZE, FONT_SIZE_STEPS
)
from config.themes import COLORS


class OutputConsole(ctk.CTkFrame):
    """A console widget for displaying script output with formatting"""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Create header with controls
        self.create_header()

        # Create output display
        self.create_output_display()

        # Add welcome message
        self.add_output("Welcome to Script Runner! Click 'Run' to start your script.", "system")

    def create_header(self):
        """Create the header with font controls and export button"""
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

        # Font size controls
        font_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        font_frame.grid(row=0, column=1, padx=10)

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
        self.export_btn.grid(row=0, column=2, padx=5)

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

    def add_output(self, message, msg_type="info"):
        """Add a message to the output console with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")

        # Color coding based on message type
        color_map = {
            "info": COLORS["output_info"],
            "success": COLORS["output_success"],
            "error": COLORS["output_error"],
            "warning": COLORS["output_warning"],
            "system": COLORS["output_system"]
        }

        self.output_text.configure(state="normal")

        # Add timestamp
        self.output_text.insert("end", f"[{timestamp}] ", "timestamp")

        # Add message with color if specified
        if msg_type in color_map and color_map[msg_type]:
            self.output_text.insert("end", f"{message}\n", msg_type)
            self.output_text.tag_config(msg_type, foreground=color_map[msg_type])
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
            self.add_output(f"Output exported to: {filename}", "success")

    def get_content(self):
        """Get the current content of the console"""
        return self.output_text.get("1.0", "end-1c")