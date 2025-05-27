"""Output manager service for handling script output display"""

from typing import Callable, Optional
from config.settings import OUTPUT_CHECK_INTERVAL


class OutputManager:
    """Manages periodic checking and display of script output"""

    def __init__(self, app_instance, script_runner):
        """Initialize the output manager

        Args:
            app_instance: The main application instance (for scheduling)
            script_runner: The ScriptRunner instance to monitor
        """
        self.app = app_instance
        self.script_runner = script_runner
        self.output_callback: Optional[Callable] = None
        self._check_scheduled = False

    def set_output_callback(self, callback: Callable[[str, str], None]):
        """Set the callback function for displaying output

        Args:
            callback: Function that takes (message_type, message) as arguments
        """
        self.output_callback = callback

    def start_monitoring(self):
        """Start monitoring the script output"""
        if not self._check_scheduled:
            self._check_scheduled = True
            self._check_output()

    def stop_monitoring(self):
        """Stop monitoring the script output"""
        self._check_scheduled = False

    def _check_output(self):
        """Check for new output messages from the script"""
        if self.output_callback:
            # Get all pending messages
            messages = self.script_runner.get_all_output()

            # Display each message
            for msg_type, message in messages:
                self.output_callback(message, msg_type)

        # Schedule next check if still monitoring
        if self._check_scheduled:
            self.app.after(OUTPUT_CHECK_INTERVAL, self._check_output)