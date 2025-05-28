"""Enhanced script runner service with log level support"""

import threading
import time
import queue
from typing import Callable, Optional, List, Tuple
from config.settings import SIMULATION_OPERATIONS, SCRIPT_SIMULATION_DELAY


class LogLevel:
    """Log levels for script output"""
    DEBUG = "debug"
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"


class ScriptRunner:
    """Handles script execution in a separate thread with log level support"""

    def __init__(self):
        self.is_running = False
        self.current_thread: Optional[threading.Thread] = None
        self.output_queue = queue.Queue()
        self._stop_requested = False
        self.developer_mode = False  # Track developer mode

    def start(self, script_path: Optional[str] = None, args: Optional[List[str]] = None, developer_mode: bool = False):
        """Start running a script

        Args:
            script_path: Path to the script to run (optional for simulation)
            args: Command line arguments for the script
            developer_mode: Whether to output debug-level messages
        """
        if self.is_running:
            raise RuntimeError("Script is already running")

        self.is_running = True
        self._stop_requested = False
        self.developer_mode = developer_mode

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

    def set_developer_mode(self, enabled: bool):
        """Update developer mode setting"""
        self.developer_mode = enabled

    def _run_simulation(self):
        """Run the enhanced script simulation with different log levels"""
        # Enhanced simulation with debug messages
        operations = [
            # (message, log_level, has_debug_details)
            ("Starting script execution...", LogLevel.INFO, True),
            ("Initializing components...", LogLevel.INFO, True),
            ("Loading configuration...", LogLevel.INFO, True),
            ("Connecting to database...", LogLevel.INFO, True),
            ("Fetching data...", LogLevel.INFO, True),
            ("Processing records...", LogLevel.INFO, True),
            ("Generating report...", LogLevel.INFO, True),
            ("Finalizing operations...", LogLevel.INFO, True),
        ]

        # Debug details for each operation
        debug_details = {
            0: [  # Starting script
                ("Python version: 3.9.7", LogLevel.DEBUG),
                ("Script path: /scripts/data_processor.py", LogLevel.DEBUG),
                ("Working directory: /home/user/projects", LogLevel.DEBUG),
            ],
            1: [  # Initializing
                ("Loading module: pandas v1.3.4", LogLevel.DEBUG),
                ("Loading module: numpy v1.21.4", LogLevel.DEBUG),
                ("Memory allocated: 128MB", LogLevel.DEBUG),
            ],
            2: [  # Loading config
                ("Config file: config.json", LogLevel.DEBUG),
                ("Parsing JSON configuration...", LogLevel.DEBUG),
                ("Validated 15 configuration parameters", LogLevel.DEBUG),
            ],
            3: [  # Database connection
                ("Database host: localhost:5432", LogLevel.DEBUG),
                ("Connection pool size: 10", LogLevel.DEBUG),
                ("SSL mode: require", LogLevel.DEBUG),
                ("Connection established in 0.23 seconds", LogLevel.DEBUG),
            ],
            4: [  # Fetching data
                ("Query: SELECT * FROM sales_data WHERE date >= '2024-01-01'", LogLevel.DEBUG),
                ("Fetching 10,000 records...", LogLevel.DEBUG),
                ("Data transfer rate: 2.3 MB/s", LogLevel.DEBUG),
            ],
            5: [  # Processing records
                ("Applying data transformations...", LogLevel.DEBUG),
                ("Validating data integrity...", LogLevel.DEBUG),
                ("Calculating aggregations...", LogLevel.DEBUG),
            ],
            6: [  # Generating report
                ("Template: quarterly_report.html", LogLevel.DEBUG),
                ("Generating charts...", LogLevel.DEBUG),
                ("Compiling PDF output...", LogLevel.DEBUG),
            ],
            7: [  # Finalizing
                ("Closing database connections...", LogLevel.DEBUG),
                ("Clearing temporary files...", LogLevel.DEBUG),
                ("Total execution time: 4.7 seconds", LogLevel.DEBUG),
            ],
        }

        for i, (operation, level, has_debug) in enumerate(operations):
            if self._stop_requested:
                self._add_output(LogLevel.WARNING, "Script execution interrupted by user.")
                break

            # Always show the main operation message
            self._add_output(level, operation)

            # Add debug details if they exist for this operation
            if has_debug and i in debug_details:
                for debug_msg, debug_level in debug_details[i]:
                    self._add_output(debug_level, debug_msg)
                    time.sleep(0.1)  # Small delay for debug messages

            time.sleep(SCRIPT_SIMULATION_DELAY)

            # Special handling for processing records - show progress
            if i == 5:  # Processing records
                for j in range(5):
                    if self._stop_requested:
                        break

                    # High-level progress for normal users
                    self._add_output(LogLevel.INFO, f"  Processing batch {j + 1}/5...")

                    # Detailed progress for developers
                    self._add_output(LogLevel.DEBUG, f"    Records {j*2000+1}-{(j+1)*2000}: Validated")
                    self._add_output(LogLevel.DEBUG, f"    Memory usage: {64 + j*12}MB")
                    self._add_output(LogLevel.DEBUG, f"    Processing rate: {1.8 + j*0.1:.1f}k records/sec")

                    time.sleep(0.5)

                # Simulate a warning
                if not self._stop_requested:
                    self._add_output(LogLevel.WARNING, "  Warning: 3 records had missing values and were skipped")
                    self._add_output(LogLevel.DEBUG, "    Missing values in columns: [customer_id, purchase_date, amount]")

        if not self._stop_requested:
            self._add_output(LogLevel.SUCCESS, "Script completed successfully!")
            self._add_output(LogLevel.INFO, "Output saved to: /output/report_2024_01_15.pdf")
            self._add_output(LogLevel.DEBUG, "Total memory peak: 256MB")
            self._add_output(LogLevel.DEBUG, "CPU usage average: 45%")

        self.is_running = False

    def _add_output(self, msg_type: str, message: str):
        """Add a message to the output queue

        Args:
            msg_type: Type of message (debug, info, success, warning, error)
            message: The message content
        """
        self.output_queue.put((msg_type, message))

    @property
    def is_alive(self) -> bool:
        """Check if the script thread is still running"""
        return self.current_thread is not None and self.current_thread.is_alive()
