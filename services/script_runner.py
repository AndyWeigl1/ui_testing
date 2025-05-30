"""Enhanced script runner service with real Python script execution"""

import threading
import time
import queue
import subprocess
import sys
import os
from typing import Callable, Optional, List, Tuple
from config.settings import SIMULATION_OPERATIONS, SCRIPT_SIMULATION_DELAY


class LogLevel:
    """Log levels for script output"""
    DEBUG = "debug"
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    SYSTEM = "system"


class ScriptRunner:
    """Handles script execution in a separate thread with log level support"""

    def __init__(self):
        self.is_running = False
        self.current_thread: Optional[threading.Thread] = None
        self.current_process: Optional[subprocess.Popen] = None
        self.output_queue = queue.Queue()
        self._stop_requested = False
        self.developer_mode = False  # Track developer mode
        self.last_exit_code = None  # Track the exit code of the last script
        self.script_succeeded = None  # Track whether the last script succeeded
        self.is_paused = False
        self.pause_state = None
        self.paused_script_path = None
        self.paused_script_args = None

    def start(self, script_path: Optional[str] = None, args: Optional[List[str]] = None, developer_mode: bool = False,
              resume: bool = False):
        """Start running a script with optional resume support

        Args:
            script_path: Path to the script to run (None for simulation)
            args: Command line arguments for the script
            developer_mode: Whether to output debug-level messages
            resume: Whether this is resuming a paused script
        """
        if self.is_running:
            raise RuntimeError("Script is already running")

        self.is_running = True
        self._stop_requested = False
        self.developer_mode = developer_mode
        self.is_paused = False

        # If not resuming, reset state
        if not resume:
            self.last_exit_code = None
            self.script_succeeded = None
            self.pause_state = None

        # Store script info for potential resume
        self.paused_script_path = script_path
        self.paused_script_args = args or []

        if script_path and os.path.exists(script_path):
            # Run actual script
            self.current_thread = threading.Thread(
                target=self._run_script,
                args=(script_path, args or [], resume),
                daemon=True
            )
        else:
            # Run simulation if no valid script path
            self.current_thread = threading.Thread(
                target=self._run_simulation,
                daemon=True
            )

        self.current_thread.start()

    def stop(self):
        """Stop the running script"""
        if self.is_running:
            self._stop_requested = True

            # If running a real process, terminate it
            if self.current_process and self.current_process.poll() is None:
                try:
                    self.current_process.terminate()
                    # Give it a moment to terminate gracefully
                    time.sleep(0.5)
                    # Force kill if still running
                    if self.current_process.poll() is None:
                        self.current_process.kill()
                except Exception as e:
                    self._add_output(LogLevel.ERROR, f"Error stopping process: {e}")

            # Mark as stopped by user (special case)
            self.last_exit_code = -1  # User termination
            self.script_succeeded = False
            self.is_running = False

            # Wait for thread to finish (with timeout)
            if self.current_thread and self.current_thread.is_alive():
                self.current_thread.join(timeout=2.0)

    def resume(self):
        """Resume a paused script"""
        if not self.is_paused or not self.paused_script_path:
            raise RuntimeError("No script is paused")

        # Start with resume flag
        self.start(
            script_path=self.paused_script_path,
            args=self.paused_script_args,
            developer_mode=self.developer_mode,
            resume=True
        )

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

    def get_last_exit_code(self) -> Optional[int]:
        """Get the exit code of the last completed script

        Returns:
            Exit code (0 = success, >0 = error, -1 = user stopped, None = still running)
        """
        return self.last_exit_code

    def did_script_succeed(self) -> Optional[bool]:
        """Check if the last script succeeded

        Returns:
            True if succeeded, False if failed, None if still running or no script run yet
        """
        return self.script_succeeded

    def _parse_log_level(self, line: str) -> Tuple[str, str]:
        """Parse log level from output line

        Returns:
            Tuple of (log_level, cleaned_message)
        """
        line = line.strip()

        # Check for log level markers
        level_markers = {
            "[DEBUG]": LogLevel.DEBUG,
            "[INFO]": LogLevel.INFO,
            "[SUCCESS]": LogLevel.SUCCESS,
            "[WARNING]": LogLevel.WARNING,
            "[ERROR]": LogLevel.ERROR,
        }

        for marker, level in level_markers.items():
            if marker in line:
                # Extract the message after the timestamp and level
                parts = line.split(marker, 1)
                if len(parts) > 1:
                    message = parts[1].strip()
                    return level, message

        # Default to info level if no marker found
        return LogLevel.INFO, line

    def _run_script(self, script_path: str, args: List[str], resume: bool = False):
        """Run an actual Python script with pause/resume support"""
        try:
            # Announce script execution
            if resume:
                self._add_output(LogLevel.SYSTEM, f"Resuming script: {script_path}")
            else:
                self._add_output(LogLevel.SYSTEM, f"Executing script: {script_path}")

            # Build command
            cmd = [sys.executable, script_path] + args

            # Add resume flag if resuming
            if resume:
                cmd.append("--resume")

            # Start the process
            self.current_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )

            # Read output in real-time
            while True:
                if self._stop_requested:
                    break

                # Check if process is still running
                if self.current_process.poll() is not None:
                    break

                # Read stdout
                line = self.current_process.stdout.readline()
                if line:
                    level, message = self._parse_log_level(line)
                    self._add_output(level, message)

                time.sleep(0.01)

            # Get any remaining output
            stdout, stderr = self.current_process.communicate(timeout=1)

            # Process remaining stdout
            if stdout:
                for line in stdout.strip().split('\n'):
                    if line:
                        level, message = self._parse_log_level(line)
                        self._add_output(level, message)

            # Process stderr
            if stderr:
                for line in stderr.strip().split('\n'):
                    if line:
                        self._add_output(LogLevel.ERROR, line)

            # Set exit code and success status
            self.last_exit_code = self.current_process.returncode

            # Check for special pause exit code
            if self.current_process.returncode == -99:
                self.is_paused = True
                self.script_succeeded = None  # Not finished yet
                self._add_output(LogLevel.SYSTEM, "Script paused for user review")

                # Try to load pause state if it exists
                state_file = os.path.join(os.path.dirname(script_path), ".divvy_state.pkl")
                if os.path.exists(state_file):
                    self.pause_state = state_file
            else:
                self.is_paused = False
                self.script_succeeded = (self.current_process.returncode == 0)

                if self.current_process.returncode == 0:
                    self._add_output(LogLevel.SYSTEM, "Script completed successfully")
                else:
                    self._add_output(LogLevel.ERROR, f"Script exited with code {self.current_process.returncode}")

        except Exception as e:
            self._add_output(LogLevel.ERROR, f"Error running script: {str(e)}")
            self.last_exit_code = 1
            self.script_succeeded = False
            self.is_paused = False
        finally:
            self.is_running = False
            self.current_process = None
    def _run_simulation(self):
        """Run the enhanced script simulation with different log levels"""
        # Original simulation code - kept as fallback
        operations = [
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
            0: [
                ("Python version: 3.9.7", LogLevel.DEBUG),
                ("Script path: /scripts/simulation.py", LogLevel.DEBUG),
                ("Working directory: /home/user/projects", LogLevel.DEBUG),
            ],
            1: [
                ("Loading module: pandas v1.3.4", LogLevel.DEBUG),
                ("Loading module: numpy v1.21.4", LogLevel.DEBUG),
                ("Memory allocated: 128MB", LogLevel.DEBUG),
            ],
            2: [
                ("Config file: config.json", LogLevel.DEBUG),
                ("Parsing JSON configuration...", LogLevel.DEBUG),
                ("Validated 15 configuration parameters", LogLevel.DEBUG),
            ],
            3: [
                ("Database host: localhost:5432", LogLevel.DEBUG),
                ("Connection pool size: 10", LogLevel.DEBUG),
                ("SSL mode: require", LogLevel.DEBUG),
                ("Connection established in 0.23 seconds", LogLevel.DEBUG),
            ],
            4: [
                ("Query: SELECT * FROM sales_data WHERE date >= '2024-01-01'", LogLevel.DEBUG),
                ("Fetching 10,000 records...", LogLevel.DEBUG),
                ("Data transfer rate: 2.3 MB/s", LogLevel.DEBUG),
            ],
            5: [
                ("Applying data transformations...", LogLevel.DEBUG),
                ("Validating data integrity...", LogLevel.DEBUG),
                ("Calculating aggregations...", LogLevel.DEBUG),
            ],
            6: [
                ("Template: quarterly_report.html", LogLevel.DEBUG),
                ("Generating charts...", LogLevel.DEBUG),
                ("Compiling PDF output...", LogLevel.DEBUG),
            ],
            7: [
                ("Closing database connections...", LogLevel.DEBUG),
                ("Clearing temporary files...", LogLevel.DEBUG),
                ("Total execution time: 4.7 seconds", LogLevel.DEBUG),
            ],
        }

        try:
            for i, (operation, level, has_debug) in enumerate(operations):
                if self._stop_requested:
                    self._add_output(LogLevel.WARNING, "Script execution interrupted by user.")
                    self.last_exit_code = -1  # User stopped
                    self.script_succeeded = False
                    break

                self._add_output(level, operation)

                if has_debug and i in debug_details:
                    for debug_msg, debug_level in debug_details[i]:
                        self._add_output(debug_level, debug_msg)
                        time.sleep(0.1)

                time.sleep(SCRIPT_SIMULATION_DELAY)

                if i == 5:  # Processing records
                    for j in range(5):
                        if self._stop_requested:
                            break

                        self._add_output(LogLevel.INFO, f"  Processing batch {j + 1}/5...")
                        self._add_output(LogLevel.DEBUG, f"    Records {j*2000+1}-{(j+1)*2000}: Validated")
                        self._add_output(LogLevel.DEBUG, f"    Memory usage: {64 + j*12}MB")
                        self._add_output(LogLevel.DEBUG, f"    Processing rate: {1.8 + j*0.1:.1f}k records/sec")

                        time.sleep(0.5)

                    if not self._stop_requested:
                        self._add_output(LogLevel.WARNING, "  Warning: 3 records had missing values and were skipped")
                        self._add_output(LogLevel.DEBUG, "    Missing values in columns: [customer_id, purchase_date, amount]")

            if not self._stop_requested:
                self._add_output(LogLevel.SUCCESS, "Script completed successfully!")
                self._add_output(LogLevel.INFO, "Output saved to: /output/report_2024_01_15.pdf")
                self._add_output(LogLevel.DEBUG, "Total memory peak: 256MB")
                self._add_output(LogLevel.DEBUG, "CPU usage average: 45%")

                # Simulation always succeeds unless stopped
                self.last_exit_code = 0
                self.script_succeeded = True

        except Exception as e:
            self._add_output(LogLevel.ERROR, f"Simulation error: {str(e)}")
            self.last_exit_code = 1
            self.script_succeeded = False
        finally:
            self.is_running = False

    def _add_output(self, msg_type: str, message: str):
        """Add a message to the output queue

        Args:
            msg_type: Type of message (debug, info, success, warning, error)
            message: The message content
        """
        self.output_queue.put((msg_type, message))

    def is_script_paused(self) -> bool:
        """Check if the script is currently paused"""
        return self.is_paused

    def get_pause_state(self) -> Optional[str]:
        """Get the pause state file path if script is paused"""
        return self.pause_state if self.is_paused else None

    @property
    def is_alive(self) -> bool:
        """Check if the script thread is still running"""
        return self.current_thread is not None and self.current_thread.is_alive()
