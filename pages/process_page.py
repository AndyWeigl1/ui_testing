"""Process page - main script execution interface"""

import customtkinter as ctk
from pages.base_page import BasePage
from components.console import OutputConsole
from components.controls import ControlPanel
from services.script_runner import ScriptRunner
from services.output_manager import OutputManager
from utils.event_bus import Events


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
        
        super().__init__(parent, state_manager, event_bus, **kwargs)
        
    def setup_ui(self):
        """Set up the Process page UI"""
        # Configure grid
        self.grid_columnconfigure(0, weight=1)

        # Explicitly set weights for all rows within ProcessPage:
        self.grid_rowconfigure(0, weight=0)  # For header_frame (script path, etc.)
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
        
        # Script path input (for future use)
        self.script_path_var = ctk.StringVar(value="simulation_script.py")
        path_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        path_frame.grid(row=1, column=0, pady=(10, 0), sticky="ew")
        path_frame.grid_columnconfigure(1, weight=1)
        
        path_label = ctk.CTkLabel(
            path_frame,
            text="Script:",
            font=ctk.CTkFont(size=14)
        )
        path_label.grid(row=0, column=0, padx=(0, 10))
        
        self.path_entry = ctk.CTkEntry(
            path_frame,
            textvariable=self.script_path_var,
            placeholder_text="Enter script path or use browse...",
            state="disabled"  # Disabled for now since we're using simulation
        )
        self.path_entry.grid(row=0, column=1, sticky="ew", padx=(0, 10))
        
        self.browse_btn = ctk.CTkButton(
            path_frame,
            text="Browse",
            width=100,
            command=self.browse_script,
            state="disabled"  # Disabled for now
        )
        self.browse_btn.grid(row=0, column=2)
        
        # Create output console
        self.console = OutputConsole(self, state_manager=self.state_manager)
        self.console.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        
        # Create control panel
        self.control_panel = ControlPanel(
            self,
            on_run=self.run_script,
            on_stop=self.stop_script,
            on_clear=self.clear_output
        )
        self.control_panel.grid(row=2, column=0, padx=20, pady=(10, 20), sticky="ew")
        
        # Set up output handling
        self.output_manager.set_output_callback(self.console.add_output)

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
        
    def on_activate(self):
        """Called when the Process page becomes active"""
        super().on_activate()
        
        # Start monitoring output if script is running
        if self.get_state('script_running', False):
            self.output_manager.start_monitoring()
        else:
            # Make sure UI is in correct state
            self.control_panel.set_running_state(False)
            
    def on_deactivate(self):
        """Called when the Process page becomes inactive"""
        super().on_deactivate()
        
        # Continue monitoring even when page is not active
        # so we don't miss output
        
    def browse_script(self):
        """Browse for a script file"""
        # This will be implemented later when we add file selection
        self.show_message("File browser not yet implemented", "info")

    def run_script(self):
        """Start running the script"""
        if not self.get_state('script_running', False):
            try:
                # Clear the output queue before starting
                self.script_runner.clear_output_queue()

                # Get script path (for now, None means simulation)
                script_path = None  # self.script_path_var.get() when implemented

                # Get developer mode setting
                developer_mode = self.get_state('developer_mode', False)

                # Update script runner's developer mode
                self.script_runner.set_developer_mode(developer_mode)

                # Start the script with developer mode flag
                self.script_runner.start(script_path, developer_mode=developer_mode)

                # Update state
                self.set_state('script_running', True)
                self.set_state('status', 'running')
                self.set_state('script_path', script_path or 'simulation')

                # Start output monitoring
                self.output_manager.start_monitoring()

                # Publish event
                self.publish_event(Events.SCRIPT_STARTED, {
                    'page': 'Process',
                    'script': script_path or 'simulation',
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
        """Check if the script has completed"""
        if not self.script_runner.is_running and not self.script_runner.is_alive:
            # Script completed
            self.set_state('script_running', False)
            self.set_state('status', 'success')
            self.output_manager.stop_monitoring()
            self.publish_event(Events.SCRIPT_COMPLETED, {'status': 'success'})
        else:
            # Check again in 100ms
            self.after(100, self.check_script_completion)
            
    def on_script_running_changed(self, is_running):
        """Handle script running state changes"""
        self.control_panel.set_running_state(is_running)
        
        if is_running:
            self.output_manager.start_monitoring()
        else:
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
