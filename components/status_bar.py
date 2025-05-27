"""Status indicator component for showing application state"""

import customtkinter as ctk
from config.themes import COLORS


class StatusIndicator(ctk.CTkFrame):
    """A status indicator widget showing the current application state"""

    def __init__(self, master, **kwargs):
        # Set default width and height if not provided
        kwargs.setdefault('width', 100)
        kwargs.setdefault('height', 30)

        super().__init__(master, **kwargs)

        # Prevent frame from shrinking
        self.grid_propagate(False)

        # Create status label
        self.status_label = ctk.CTkLabel(
            self,
            text="● Idle",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["status_idle"]
        )
        self.status_label.place(relx=0.5, rely=0.5, anchor="center")

        # Store current status
        self._status = "idle"

    def set_status(self, status):
        """Set the status indicator

        Args:
            status (str): One of 'idle', 'running', 'error', 'success'
        """
        status_configs = {
            "idle": {
                "text": "● Idle",
                "color": COLORS["status_idle"]
            },
            "running": {
                "text": "● Running",
                "color": COLORS["status_running"]
            },
            "error": {
                "text": "● Error",
                "color": COLORS["output_error"]
            },
            "success": {
                "text": "● Success",
                "color": COLORS["output_success"]
            }
        }

        if status in status_configs:
            config = status_configs[status]
            self.status_label.configure(
                text=config["text"],
                text_color=config["color"]
            )
            self._status = status

    def get_status(self):
        """Get the current status"""
        return self._status