"""Script runner service for executing scripts and managing their lifecycle"""

import threading
import time
import queue
from typing import Callable, Optional, List, Tuple
from config.settings import SIMULATION_OPERATIONS, SCRIPT_SIMULATION_DELAY


class ScriptRunner:
    """Handles script execution in a separate thread with output management"""

    def __init__(self):
        self.is_running = False
        self.current_thread: Optional[threading.Thread] = None
        self.output_queue = queue.Queue()
        self._stop_requested = False

    def start(self, script_path: Optional[str] = None, args: Optional[List[str]] = None):
        """Start running a script

        Args:
            script_path: Path to the script to run (optional for simulation)
            args: Command line arguments for the script
        """
        if self.is_running:
            raise RuntimeError("Script is already running")

        self.is_running = True
        self._stop_requested = False

        # For now, we'll use simulation. Later this can run actual scripts
        self.current_thread = threading.Thread(
            target=self._run_simulation,
            daemon=True
        )
        self.current_thread.start()

    def stop(self):
        """Stop the running script"""
        if self.is_running:
            self._stop_requested = True
            self.is_running = False

            # Wait for thread to finish (with timeout)
            if self.current_thread and self.current_thread.is_alive():
                self.current_thread.join(timeout=2.0)

    def get_output(self) -> Optional[Tuple[str, str]]:
        """Get the next output message from the queue

        Returns:
            Tuple of (message_type, message) or None if queue is empty
        """
        try:
            return self.output_queue.get_nowait()
        except queue.Empty:
            return None

    def get_all_output(self) -> List[Tuple[str, str]]:
        """Get all pending output messages

        Returns:
            List of (message_type, message) tuples
        """
        messages = []
        while True:
            msg = self.get_output()
            if msg is None:
                break
            messages.append(msg)
        return messages

    def clear_output_queue(self):
        """Clear any pending output messages"""
        while not self.output_queue.empty():
            try:
                self.output_queue.get_nowait()
            except queue.Empty:
                break

    def _run_simulation(self):
        """Run the script simulation"""
        operations = SIMULATION_OPERATIONS

        for i, operation in enumerate(operations):
            if self._stop_requested:
                self._add_output("info", "Script execution interrupted.")
                break

            self._add_output("info", operation)
            time.sleep(SCRIPT_SIMULATION_DELAY)

            # Simulate some detailed output
            if i == 4:  # Processing records
                for j in range(5):
                    if self._stop_requested:
                        break
                    self._add_output("info", f"  - Processed record {j + 1}/5")
                    time.sleep(0.5)

        if not self._stop_requested:
            self._add_output("success", "Script completed successfully!")

        self.is_running = False

    def _run_actual_script(self, script_path: str, args: Optional[List[str]] = None):
        """Run an actual script (to be implemented)

        This method will handle running real scripts using subprocess
        """
        # TODO: Implement actual script execution
        # This will use subprocess.Popen to run scripts and capture output
        pass

    def _add_output(self, msg_type: str, message: str):
        """Add a message to the output queue

        Args:
            msg_type: Type of message (info, success, error, warning)
            message: The message content
        """
        self.output_queue.put((msg_type, message))

    @property
    def is_alive(self) -> bool:
        """Check if the script thread is still running"""
        return self.current_thread is not None and self.current_thread.is_alive()