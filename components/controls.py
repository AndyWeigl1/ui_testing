"""Control panel component with Run, Stop, and Clear buttons"""

import customtkinter as ctk
from config.settings import CONTROL_BUTTON_WIDTH, CONTROL_BUTTON_HEIGHT
from config.themes import COLORS


class ControlPanel(ctk.CTkFrame):
    """Control panel with script execution controls and progress indicator"""

    def __init__(self, master, on_run=None, on_stop=None, on_clear=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        # Store callbacks
        self.on_run_callback = on_run
        self.on_stop_callback = on_stop
        self.on_clear_callback = on_clear

        # Configure grid
        self.grid_columnconfigure(0, weight=1)

        # Create controls
        self.create_buttons()
        self.create_progress_bar()

    def create_buttons(self):
        """Create the control buttons"""
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.grid(row=0, column=0)

        # Run button
        self.run_button = ctk.CTkButton(
            button_frame,
            text="▶ Run",
            width=CONTROL_BUTTON_WIDTH,
            height=CONTROL_BUTTON_HEIGHT,
            font=ctk.CTkFont(size=16, weight="bold"),
            command=self.handle_run,
            fg_color=COLORS["run_button"],
            hover_color=COLORS["run_button_hover"]
        )
        self.run_button.grid(row=0, column=0, padx=10)

        # Stop button
        self.stop_button = ctk.CTkButton(
            button_frame,
            text="■ Stop",
            width=CONTROL_BUTTON_WIDTH,
            height=CONTROL_BUTTON_HEIGHT,
            font=ctk.CTkFont(size=16, weight="bold"),
            command=self.handle_stop,
            fg_color=COLORS["stop_button"],
            hover_color=COLORS["stop_button_hover"],
            state="disabled"
        )
        self.stop_button.grid(row=0, column=1, padx=10)

        # Clear button
        self.clear_button = ctk.CTkButton(
            button_frame,
            text="🗑 Clear",
            width=CONTROL_BUTTON_WIDTH,
            height=CONTROL_BUTTON_HEIGHT,
            font=ctk.CTkFont(size=16, weight="bold"),
            command=self.handle_clear,
            fg_color=COLORS["clear_button"],
            hover_color=COLORS["clear_button_hover"]
        )
        self.clear_button.grid(row=0, column=2, padx=10)

    def create_progress_bar(self):
        """Create the progress bar (initially hidden)"""
        self.progress_bar = ctk.CTkProgressBar(
            self,
            width=400,
            height=20,
            mode="indeterminate"
        )
        self.progress_bar.grid(row=1, column=0, pady=(20, 0))
        self.progress_bar.grid_forget()

    def handle_run(self):
        """Handle run button click"""
        if self.on_run_callback:
            self.on_run_callback()

    def handle_stop(self):
        """Handle stop button click"""
        if self.on_stop_callback:
            self.on_stop_callback()

    def handle_clear(self):
        """Handle clear button click"""
        if self.on_clear_callback:
            self.on_clear_callback()

    def set_running_state(self, is_running):
        """Update button states based on running state"""
        if is_running:
            self.run_button.configure(state="disabled")
            self.stop_button.configure(state="normal")
            self.show_progress()
        else:
            self.run_button.configure(state="normal")
            self.stop_button.configure(state="disabled")
            self.hide_progress()

    def show_progress(self):
        """Show and start the progress bar"""
        self.progress_bar.grid(row=1, column=0, pady=(20, 0))
        self.progress_bar.start()

    def hide_progress(self):
        """Hide and stop the progress bar"""
        self.progress_bar.stop()
        self.progress_bar.grid_forget()