"""Process page - main script execution interface with simplified layout"""

import customtkinter as ctk
from pages.base_page import BasePage
from components.console import OutputConsole
from components.controls import ControlPanel
from services.script_runner import ScriptRunner
from services.output_manager import OutputManager
from utils.event_bus import Events
from utils.script_history import get_history_manager  # Add this import
import os

# Import script configuration
try:
    from config.scripts_config import AVAILABLE_SCRIPTS, DEFAULT_SCRIPT
except ImportError:
    # Fallback if config doesn't exist yet
    AVAILABLE_SCRIPTS = {}
    DEFAULT_SCRIPT = ""


class ProcessPage(BasePage):
    """Process page for script execution and output display"""

    def __init__(self, parent, state_manager, event_bus, script_runner: ScriptRunner, **kwargs):
        """Initialize the Process page

        Args:
            parent: Parent widget
            state_manager: Application state manager
            event_bus: Application event bus
            script_runner: Script runner service instance
            **kwargs: Additional arguments
        """
        # Store script runner reference before calling super().__init__
        self.script_runner = script_runner

        # Initialize output manager
        self.output_manager = OutputManager(parent.winfo_toplevel(), script_runner)

        # Load scripts from configuration
        self.scripts_config = AVAILABLE_SCRIPTS

        # Initialize history manager
        self.history_manager = get_history_manager()

        # Track if placeholder has been removed from dropdown
        self.placeholder_removed = False

        super().__init__(parent, state_manager, event_bus, **kwargs)

    def setup_ui(self):
        """Set up the Process page UI"""
        # Configure grid
        self.grid_columnconfigure(0, weight=1)

        # Explicitly set weights for all rows within ProcessPage:
        self.grid_rowconfigure(0, weight=0)  # For header_frame (script selection, etc.)
        self.grid_rowconfigure(1, weight=1)  # For self.console (this row should expand/shrink)
        self.grid_rowconfigure(2, weight=0)  # For self.control_panel

        # Page header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1)

        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text="Script Execution",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.grid(row=0, column=0, sticky="w")

        # Script selection frame
        script_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        script_frame.grid(row=1, column=0, pady=(10, 0), sticky="ew")
        script_frame.grid_columnconfigure(1, weight=1)  # Let dropdown expand

        # Script label
        script_label = ctk.CTkLabel(
            script_frame,
            text="Script:",
            font=ctk.CTkFont(size=14)
        )
        script_label.grid(row=0, column=0, padx=(0, 10), sticky="w")

        # Script dropdown (wider now) - Start with placeholder, remove it once a real script is selected
        if self.scripts_config:
            script_options = ["Select a script..."] + list(self.scripts_config.keys())
            initial_value = DEFAULT_SCRIPT if DEFAULT_SCRIPT and DEFAULT_SCRIPT in self.scripts_config else "Select a script..."
        else:
            script_options = ["No scripts available"]
            initial_value = "No scripts available"

        self.script_type_var = ctk.StringVar(value=initial_value)
        self.script_dropdown = ctk.CTkOptionMenu(
            script_frame,
            values=script_options,
            variable=self.script_type_var,
            command=self.on_script_changed,
            width=250  # Wider dropdown
        )
        self.script_dropdown.grid(row=0, column=1, padx=(0, 20), sticky="w")

        # Configure Script button
        self.configure_btn = ctk.CTkButton(
            script_frame,
            text="Configure Script",
            width=130,
            command=self.configure_script,
            fg_color=("gray70", "gray30")  # Secondary button style
        )
        self.configure_btn.grid(row=0, column=2, sticky="w")

        # Create output console
        self.console = OutputConsole(self, state_manager=self.state_manager)
        self.console.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

        # Create control panel
        self.control_panel = ControlPanel(
            self,
            on_run=self.run_script,
            on_stop=self.stop_script,
            on_clear=self.clear_output,
            on_continue=self.continue_script  # New callback
        )
        self.control_panel.grid(row=2, column=0, padx=20, pady=(10, 20), sticky="ew")

        # Set up output handling
        self.output_manager.set_output_callback(self.console.add_output)

    def continue_script(self):
        """Continue a paused script"""
        try:
            # Check if script is actually paused
            if not self.script_runner.is_script_paused():
                self.console.add_output("No script is currently paused", "warning")
                return

            self.console.add_output("Continuing script execution...", "system")

            # Resume the script
            self.script_runner.resume()

            # Update UI state
            self.set_state('script_running', True)
            self.set_state('status', 'running')
            self.control_panel.set_running_state(True)
            self.control_panel.set_paused_state(False)

            # Start output monitoring
            self.output_manager.start_monitoring()

            # Publish event
            self.publish_event('script.resumed', {
                'page': 'Process',
                'script': self.get_state('script_path')
            })

            # Schedule completion check
            self.check_script_completion()

        except Exception as e:
            self.console.add_output(f"Error resuming script: {e}", "error")
            self.set_state('script_running', False)
            self.set_state('status', 'error')

    def setup_state_subscriptions(self):
        """Set up state subscriptions for the Process page"""
        # Subscribe to script running state
        self.state_manager.subscribe('script_running', self.on_script_running_changed)
        # Subscribe to developer mode changes
        self.state_manager.subscribe('developer_mode', self.on_developer_mode_changed)

    def on_developer_mode_changed(self, enabled):
        """Handle developer mode state changes"""
        # Update script runner's developer mode setting
        if hasattr(self, 'script_runner'):
            self.script_runner.set_developer_mode(enabled)

        # If a script is currently running, notify the user
        if self.get_state('script_running', False):
            mode_text = "enabled" if enabled else "disabled"
            self.console.add_output(
                f"Developer mode {mode_text} (will take full effect on next run)",
                "system"
            )

    def setup_event_subscriptions(self):
        """Set up event subscriptions for the Process page"""
        # Subscribe to script events
        self.event_bus.subscribe(Events.SCRIPT_OUTPUT, self.handle_script_output)
        # Subscribe to navigation events to refresh history when returning to Scripts page
        self.event_bus.subscribe(Events.NAVIGATION_CHANGED, self.on_navigation_changed)

    def on_navigation_changed(self, data):
        """Handle navigation changes"""
        if data and data.get('page') == 'Scripts':
            # Refresh the Scripts page to show updated history
            scripts_page = self.parent.winfo_toplevel().pages.get('Scripts')
            if scripts_page and hasattr(scripts_page, 'refresh_projects'):
                scripts_page.refresh_projects()

    def on_activate(self):
        """Called when the Process page becomes active"""
        super().on_activate()

        # Check if there's a paused script
        if self.script_runner.is_script_paused():
            self.control_panel.set_paused_state(True)
            self.console.add_output("Script is paused. Click 'Continue' to resume.", "info")
        elif self.get_state('script_running', False):
            self.output_manager.start_monitoring()
        else:
            # Make sure UI is in correct state
            self.control_panel.set_running_state(False)
            self.control_panel.set_paused_state(False)

    def on_deactivate(self):
        """Called when the Process page becomes inactive"""
        super().on_deactivate()

        # Continue monitoring even when page is not active
        # so we don't miss output

    def on_script_changed(self, selection: str):
        """Handle script selection change"""
        # Don't show description for placeholder text
        if selection == "Select a script..." or selection == "No scripts available":
            return

        # If this is the first time selecting a real script, remove the placeholder
        if not self.placeholder_removed and selection in self.scripts_config:
            self.placeholder_removed = True
            # Update dropdown values to only include real scripts
            script_options = list(self.scripts_config.keys())
            self.script_dropdown.configure(values=script_options)

        # Show script description
        script_info = self.scripts_config.get(selection, {})
        description = script_info.get("description", "No description available")
        self.show_message(f"{selection}: {description}", "info")

    def configure_script(self):
        """Handle configure script button click"""
        # Get current script info
        script_name = self.script_type_var.get()

        # Check if a valid script is selected
        if script_name == "Select a script..." or script_name == "No scripts available" or script_name not in self.scripts_config:
            self.show_message("Please select a script first", "warning")
            return

        script_info = self.scripts_config.get(script_name, {})

        # Check if script has configurable paths
        if script_info.get("configurable_paths"):
            # Import the path config dialog and settings manager
            from components.path_config_dialog import PathConfigDialog
            from config.script_settings import get_settings_manager

            # Get current settings
            settings_manager = get_settings_manager()
            current_settings = settings_manager.load_settings(script_name)

            # Open configuration dialog
            dialog = PathConfigDialog(
                self,
                script_name,
                script_info["configurable_paths"],
                current_settings
            )

            # Wait for dialog to close
            self.wait_window(dialog)

            # Get result
            result = dialog.get_result()
            if result is not None:
                # Save settings
                if settings_manager.save_settings(script_name, result):
                    self.console.add_output(f"Path configuration saved for {script_name}", "success")
                else:
                    self.console.add_output(f"Failed to save configuration for {script_name}", "error")

        elif script_info.get("parameters"):
            # Show existing parameters (legacy support)
            params_str = ", ".join(f"{k}={v}" for k, v in script_info["parameters"].items())
            self.show_message(f"Configuration for {script_name}: {params_str}", "info")
        else:
            self.show_message(f"No configuration options for {script_name}", "info")

    def run_script(self):
        """Start running the script"""
        if not self.get_state('script_running', False):
            try:
                # Get selected script
                script_name = self.script_type_var.get()

                # Check if a valid script is selected
                if script_name == "Select a script..." or script_name == "No scripts available":
                    self.console.add_output("Please select a script to run", "warning")
                    return

                if script_name not in self.scripts_config:
                    self.console.add_output(f"Script '{script_name}' not found in configuration", "error")
                    return

                # Clear the output queue before starting
                self.script_runner.clear_output_queue()

                script_info = self.scripts_config.get(script_name, {})
                script_path = script_info.get("path")

                # Check if script path is valid
                if not script_path:
                    self.console.add_output(f"No script path configured for '{script_name}'", "error")
                    return

                # Check if script exists
                if not os.path.exists(script_path):
                    self.console.add_output(f"Script not found: {script_path}", "error")
                    self.console.add_output("Please ensure the script file exists in the scripts/ directory", "warning")
                    return

                self.console.add_output(f"Running script: {script_name}", "system")

                # Get developer mode setting
                developer_mode = self.get_state('developer_mode', False)

                # Update script runner's developer mode
                self.script_runner.set_developer_mode(developer_mode)

                # Record script start in history
                self.history_manager.start_script_run(script_name, script_path)

                # Start the script with developer mode flag
                self.script_runner.start(script_path, developer_mode=developer_mode)

                # Update state
                self.set_state('script_running', True)
                self.set_state('status', 'running')
                self.set_state('script_path', script_path)
                self.set_state('script_name', script_name)

                # Start output monitoring
                self.output_manager.start_monitoring()

                # Publish event
                self.publish_event(Events.SCRIPT_STARTED, {
                    'page': 'Process',
                    'script': script_path,
                    'script_name': script_name,
                    'developer_mode': developer_mode
                })

                # Schedule completion check
                self.check_script_completion()

            except RuntimeError as e:
                self.set_state('script_running', False)
                self.set_state('status', 'error')
                self.console.add_output(f"Error starting script: {e}", "error")
                self.publish_event(Events.SCRIPT_ERROR, {'error': str(e)})

    def stop_script(self):
        """Stop the running script"""
        if self.get_state('script_running', False):
            # Stop the script
            self.script_runner.stop()

            # Stop output monitoring
            self.output_manager.stop_monitoring()

            # Record script stop in history
            script_name = self.get_state('script_name')
            if script_name:
                self.history_manager.end_script_run(script_name, 'stopped', -1, 'Stopped by user')

            # Update state
            self.set_state('script_running', False)
            self.set_state('status', 'idle')

            # Publish event
            self.publish_event(Events.SCRIPT_STOPPED, {'reason': 'user_request'})

            # Add console message
            self.console.add_output("Script stopped by user.", "warning")

    def clear_output(self):
        """Clear the output console"""
        self.console.clear()
        self.console.add_output("Console cleared.", "system")
        self.publish_event(Events.OUTPUT_CLEARED, {'page': 'Process'})

    def check_script_completion(self):
        """Check if the script has completed (modified to handle pause state)"""
        if not self.script_runner.is_running and not self.script_runner.is_alive:
            # Check if script is paused
            if self.script_runner.is_script_paused():
                # Script is paused, not completed
                self.set_state('script_running', False)
                self.set_state('status', 'paused')
                self.output_manager.stop_monitoring()

                # Update UI to show Continue button
                self.control_panel.set_running_state(False)
                self.control_panel.set_paused_state(True)

                # Enable script selection but keep it on current script
                self.script_dropdown.configure(state="normal")
                self.configure_btn.configure(state="disabled")

                # Publish event
                self.publish_event('script.paused', {
                    'script': self.get_state('script_name'),
                    'reason': 'user_review'
                })

                return  # Don't continue checking

            # Script completed (not paused)
            self.set_state('script_running', False)
            self.output_manager.stop_monitoring()

            # Reset pause state in UI
            self.control_panel.set_paused_state(False)

            # Determine the final status based on script exit code
            script_succeeded = self.script_runner.did_script_succeed()
            exit_code = self.script_runner.get_last_exit_code()
            script_name = self.get_state('script_name')

            if script_succeeded is True:
                # Script completed successfully
                self.set_state('status', 'success')
                self.publish_event(Events.SCRIPT_COMPLETED, {'status': 'success', 'exit_code': exit_code})

                # Record success in history
                if script_name:
                    self.history_manager.end_script_run(script_name, 'success', exit_code)

            elif script_succeeded is False:
                # Script failed or was stopped by user
                if exit_code == -1:
                    # User stopped the script - already recorded in stop_script()
                    self.set_state('status', 'idle')  # Don't show error for user-initiated stops
                    self.publish_event(Events.SCRIPT_STOPPED, {'reason': 'user_request', 'exit_code': exit_code})
                else:
                    # Script failed with an error
                    self.set_state('status', 'error')
                    self.publish_event(Events.SCRIPT_ERROR, {'status': 'error', 'exit_code': exit_code})

                    # Record error in history
                    if script_name:
                        self.history_manager.end_script_run(script_name, 'error', exit_code, f'Exit code: {exit_code}')
            else:
                # Fallback case (shouldn't happen, but just in case)
                self.set_state('status', 'idle')
                self.publish_event(Events.SCRIPT_COMPLETED, {'status': 'unknown', 'exit_code': exit_code})

                # Record unknown status in history
                if script_name:
                    self.history_manager.end_script_run(script_name, 'unknown', exit_code)
        else:
            # Check again in 100ms
            self.after(100, self.check_script_completion)

    def on_script_running_changed(self, is_running):
        """Handle script running state changes"""
        self.control_panel.set_running_state(is_running)

        # Check if we should show pause state
        if not is_running and self.script_runner.is_script_paused():
            self.control_panel.set_paused_state(True)
            self.script_dropdown.configure(state="disabled")  # Keep disabled while paused
            self.configure_btn.configure(state="disabled")
        else:
            # Normal state handling
            if is_running:
                self.script_dropdown.configure(state="disabled")
                self.configure_btn.configure(state="disabled")
                self.output_manager.start_monitoring()
            else:
                self.script_dropdown.configure(state="normal")
                self.configure_btn.configure(state="normal")
                self.output_manager.stop_monitoring()

    def handle_script_output(self, data):
        """Handle script output events"""
        if data and self.is_active:
            message = data.get('message', '')
            msg_type = data.get('type', 'info')
            self.console.add_output(message, msg_type)

    def cleanup(self):
        """Clean up resources when page is destroyed"""
        # Make sure output monitoring is stopped
        self.output_manager.stop_monitoring()
        super().cleanup()
