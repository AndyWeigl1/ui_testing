"""Main application class"""

import customtkinter as ctk
import tkinter as tk
import threading
import queue
import time

from components.navbar import ModernNavbar
from components.status_bar import StatusIndicator
from pages import AboutPage, ProcessPage, ProjectsPage, SettingsPage
from services.script_runner import ScriptRunner
from services.output_manager import OutputManager
from utils.event_bus import get_event_bus, Events
from utils.state_manager import get_state_manager
from config.settings import *
from config.themes import COLORS, DEFAULT_APPEARANCE, DEFAULT_COLOR_THEME

# Configure CustomTkinter appearance
ctk.set_appearance_mode(DEFAULT_APPEARANCE)
ctk.set_default_color_theme(DEFAULT_COLOR_THEME)


class ModernUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window configuration
        self.title(WINDOW_TITLE)
        self.geometry(f"{WINDOW_SIZE[0]}x{WINDOW_SIZE[1]}")
        self.minsize(*MIN_SIZE)

        # Initialize state manager
        self.state_manager = get_state_manager()
        self.state_manager.set('current_page', DEFAULT_PAGE)
        self.state_manager.set('theme', DEFAULT_APPEARANCE)
        self.state_manager.set('font_size', DEFAULT_FONT_SIZE)
        
        # Initialize event bus
        self.event_bus = get_event_bus()
        self.setup_event_subscriptions()
        self.setup_state_subscriptions()

        # Initialize services
        self.script_runner = ScriptRunner()
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Create navbar
        self.create_navbar()

        # Create UI elements
        self.create_header()
        self.create_page_container()
        self.create_pages()
        
        # Show initial page
        self.switch_page(DEFAULT_PAGE)

    def setup_event_subscriptions(self):
        """Set up event subscriptions for the application"""
        # Subscribe to navigation events
        self.event_bus.subscribe(Events.NAVIGATION_CHANGED, self.handle_navigation_change)
        
        # Subscribe to script events
        # self.event_bus.subscribe(Events.SCRIPT_STARTED, self.handle_script_started)
        # self.event_bus.subscribe(Events.SCRIPT_STOPPED, self.handle_script_stopped)
        self.event_bus.subscribe(Events.SCRIPT_COMPLETED, self.handle_script_completed)
        self.event_bus.subscribe(Events.SCRIPT_ERROR, self.handle_script_error)
        
        # Subscribe to theme events
        self.event_bus.subscribe(Events.THEME_CHANGED, self.handle_theme_changed)
        
        # Subscribe to status events
        self.event_bus.subscribe(Events.STATUS_CHANGED, self.handle_status_changed)
    
    def setup_state_subscriptions(self):
        """Set up state subscriptions for reactive UI updates"""
        # Subscribe to state changes
        # self.state_manager.subscribe('script_running', self.on_script_running_changed)
        self.state_manager.subscribe('status', self.on_status_changed)
        self.state_manager.subscribe('theme', self.on_theme_changed)
        self.state_manager.subscribe('current_page', self.on_page_changed)

    def create_navbar(self):
        """Create the modern navbar"""
        self.navbar = ModernNavbar(self, command=self.on_nav_change)
        self.navbar.grid(row=0, column=0, padx=20, pady=(15, 5), sticky="ew")

    def on_nav_change(self, page):
        """Handle navigation changes"""
        # Update state and switch page
        self.switch_page(page)
        
        # Publish navigation change event
        self.event_bus.publish(Events.NAVIGATION_CHANGED, {'page': page})

    def create_header(self):
        """Create the header with title and theme toggle"""
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=1, column=0, padx=20, pady=(10, 10), sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1)

        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text="Script Control Panel",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.grid(row=0, column=0, sticky="w")

        # Theme toggle switch
        self.theme_switch = ctk.CTkSwitch(
            header_frame,
            text="Dark Mode",
            command=self.toggle_theme,
            button_color="#1f6aa5",
            progress_color="#144870"
        )
        self.theme_switch.grid(row=0, column=1, padx=10)
        self.theme_switch.select()

        # Status indicator
        self.status_indicator = StatusIndicator(header_frame)
        self.status_indicator.grid(row=0, column=2, padx=10)

    def create_page_container(self):
        """Create the container for pages"""
        self.page_container = ctk.CTkFrame(self, fg_color="transparent")
        self.page_container.grid(row=2, column=0, padx=0, pady=0, sticky="nsew")
        self.page_container.grid_columnconfigure(0, weight=1)
        self.page_container.grid_rowconfigure(0, weight=1)
        
    def create_pages(self):
        """Create all application pages"""
        self.pages = {
            'About': AboutPage(
                self.page_container,
                self.state_manager,
                self.event_bus
            ),
            'Process': ProcessPage(
                self.page_container,
                self.state_manager,
                self.event_bus,
                self.script_runner
            ),
            'Projects': ProjectsPage(
                self.page_container,
                self.state_manager,
                self.event_bus
            ),
            'Settings': SettingsPage(
                self.page_container,
                self.state_manager,
                self.event_bus
            )
        }
        
        # Initially hide all pages
        for page in self.pages.values():
            page.grid_forget()
            
        # Store reference to current page
        self.current_page_widget = None
        
    def switch_page(self, page_name: str):
        """Switch to a different page"""
        # Deactivate current page
        if self.current_page_widget:
            self.current_page_widget.on_deactivate()
            self.current_page_widget.grid_forget()
            
        # Activate new page
        if page_name in self.pages:
            self.current_page_widget = self.pages[page_name]
            self.current_page_widget.grid(row=0, column=0, sticky="nsew")
            self.current_page_widget.on_activate()
            
            # Update state
            self.state_manager.set('current_page', page_name)

    def toggle_theme(self):
        """Toggle between light and dark themes"""
        theme = "dark" if self.theme_switch.get() else "light"
        
        # Update state
        self.state_manager.set('theme', theme)
        
        # Publish theme change event
        self.event_bus.publish(Events.THEME_CHANGED, {'theme': theme})

    def run_script(self):
        """Start running the script"""
        if not self.state_manager.get('script_running', False):
            try:
                # Clear the output queue before starting
                self.script_runner.clear_output_queue()

                # Start the script
                self.script_runner.start()
                
                # Update state
                self.state_manager.set('script_running', True)
                self.state_manager.set('status', 'running')
                
                # Publish script started event
                current_page = self.state_manager.get('current_page')
                self.event_bus.publish(Events.SCRIPT_STARTED, {'page': current_page})

                # Schedule UI reset when script completes
                self.check_script_completion()

            except RuntimeError as e:
                self.state_manager.set('script_running', False)
                self.state_manager.set('status', 'error')
                self.event_bus.publish(Events.SCRIPT_ERROR, {'error': str(e)})

    def stop_script(self):
        """Stop the running script"""
        if self.state_manager.get('script_running', False):
            # Stop the script
            self.script_runner.stop()
            
            # Update state
            self.state_manager.set('script_running', False)
            self.state_manager.set('status', 'idle')

            # Publish script stopped event
            self.event_bus.publish(Events.SCRIPT_STOPPED, {'reason': 'user_request'})

    def check_script_completion(self):
        """Check if the script has completed and update UI accordingly"""
        if not self.script_runner.is_running and not self.script_runner.is_alive:
            # Script has completed successfully
            self.state_manager.set('script_running', False)
            self.state_manager.set('status', 'success')
            self.event_bus.publish(Events.SCRIPT_COMPLETED, {'status': 'success'})
        else:
            # Check again in 100ms
            self.after(100, self.check_script_completion)

    def clear_output(self):
        """Clear the output console"""
        self.console.clear()
        self.console.add_output("Console cleared.", "system")

    def simulate_script(self):
        """Simulate a running script"""
        operations = SIMULATION_OPERATIONS

        for i, operation in enumerate(operations):
            if not self.is_running:
                break

            self.output_queue.put(("info", operation))
            time.sleep(SCRIPT_SIMULATION_DELAY)

            # Simulate some detailed output
            if i == 4:  # Processing records
                for j in range(5):
                    if not self.is_running:
                        break
                    self.output_queue.put(("info", f"  - Processed record {j + 1}/5"))
                    time.sleep(0.5)

        if self.is_running:
            # self.output_queue.put(("success", "Script completed successfully!"))
            self.is_running = False
            self.after(0, self.reset_ui_state)

    def reset_ui_state(self):
        """Reset UI state after script completion"""
        # Now handled by state subscriptions
        self.state_manager.set('script_running', False)
        self.state_manager.set('status', 'idle')

    def check_output_queue(self):
        """Check for new output messages from the script thread"""
        try:
            while True:
                msg_type, message = self.output_queue.get_nowait()
                self.console.add_output(message, msg_type)
        except queue.Empty:
            pass

        # Schedule next check
        self.after(OUTPUT_CHECK_INTERVAL, self.check_output_queue)

    # Event Handlers
    def handle_navigation_change(self, data):
        """Handle navigation change events"""
        if data and 'page' in data:
            pass
    
    def handle_script_started(self, data):
        """Handle script started events"""
        # UI updates are now handled by state subscriptions
        current_page = self.state_manager.get('current_page')
        self.console.add_output(f"Script started from '{current_page}' page...", "success")
    
    def handle_script_stopped(self, data):
        """Handle script stopped events"""
        # UI updates are now handled by state subscriptions
        pass
    
    def handle_script_completed(self, data):
        """Handle script completed events"""
        # UI updates are now handled by state subscriptions
        # Uncomment if you want completion message:
        # self.console.add_output("Script completed successfully!", "success")
        pass
    
    def handle_script_error(self, data):
        """Handle script error events"""
        # UI updates are now handled by state subscriptions
        if data and 'error' in data:
            self.console.add_output(f"Script error: {data['error']}", "error")
    
    def handle_theme_changed(self, data):
        """Handle theme change events"""
        if data and 'theme' in data:
            ctk.set_appearance_mode(data['theme'])
            self.navbar.update_theme()
    
    def handle_status_changed(self, data):
        """Handle status change events"""
        if data and 'status' in data:
            self.status_indicator.set_status(data['status'])
    
    # State subscription callbacks
    def on_script_running_changed(self, is_running):
        """Handle script running state changes"""
        self.control_panel.set_running_state(is_running)
        
    def on_status_changed(self, status):
        """Handle status state changes"""
        self.status_indicator.set_status(status)
        
    def on_theme_changed(self, theme):
        """Handle theme state changes"""
        ctk.set_appearance_mode(theme)
        self.navbar.update_theme()
        
    def on_page_changed(self, page):
        """Handle page state changes"""
        # This will be more useful when we implement the page system
        pass