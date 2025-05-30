"""Main application class"""

import customtkinter as ctk

from components.navbar import ModernNavbar
from components.status_bar import StatusIndicator
from pages import AboutPage, ProcessPage, ProjectsPage, SOPsPage, SettingsPage
from services.script_runner import ScriptRunner
from services.sound_integration import initialize_sound_integration
from services.notification_integration import initialize_notification_integration  # NEW
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

        # Initialize state manager and load saved settings
        self.state_manager = get_state_manager()
        self.state_manager.load_from_file()  # Load settings from file

        # Set defaults for any missing values
        defaults = {
            'current_page': DEFAULT_PAGE,
            'theme': DEFAULT_APPEARANCE,
            'font_size': DEFAULT_FONT_SIZE,
            'status': 'idle',
            'notifications_enabled': True,
            'notification_duration': 5,
            'silent_notifications': True,  # NEW: Default to silent system notifications
            'notification_script_start': True,
            'notification_script_success': True,
            'notification_script_error': True,
            'notification_script_warning': True,
            'sounds_enabled': True,
            'sound_volume': 0.7,
            'sound_script_start': True,
            'sound_script_success': True,
            'sound_script_error': True,
            'developer_mode': False
        }

        for key, default_value in defaults.items():
            if self.state_manager.get(key) is None:
                self.state_manager.set(key, default_value)

        # Initialize event bus
        self.event_bus = get_event_bus()
        self.setup_state_subscriptions()

        # Initialize services
        self.script_runner = ScriptRunner()

        # Initialize sound integration
        try:
            initialize_sound_integration()
            print("Sound integration initialized successfully")
        except Exception as e:
            print(f"Warning: Sound integration failed to initialize: {e}")
            print("Continuing without sound notifications...")

        # Initialize notification integration
        try:
            initialize_notification_integration()
            print("System notification integration initialized successfully")
        except Exception as e:
            print(f"Warning: System notification integration failed to initialize: {e}")
            print("Continuing without system notifications...")

        # Configure grid - Updated row configuration since header is removed
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)  # Page container is now at row 1

        # Create navbar
        self.create_navbar()

        # Create page container (now at row 1 instead of row 2)
        self.create_page_container()
        self.create_pages()

        # Show initial page
        self.switch_page(DEFAULT_PAGE)

        # Timer for status reset
        self._status_reset_timer = None

        # Set up proper window closing behavior
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_state_subscriptions(self):
        """Set up state subscriptions for reactive UI updates"""
        self.state_manager.subscribe('status', self.on_status_changed)
        self.state_manager.subscribe('theme', self.on_theme_changed)
        self.state_manager.subscribe('current_page', self.on_current_page_changed)

    def create_navbar(self):
        """Create the modern navbar"""
        self.navbar = ModernNavbar(self, command=self.on_nav_change)
        self.navbar.grid(row=0, column=0, padx=20, pady=(15, 5), sticky="ew")

    def on_nav_change(self, page_name: str):
        """Handle navigation changes"""
        self.switch_page(page_name)
        self.event_bus.publish(Events.NAVIGATION_CHANGED, {'page': page_name})

    def on_current_page_changed(self, page_name: str):
        """Handle current_page state changes to keep navbar in sync"""
        # Update navbar active item without triggering its command
        if hasattr(self, 'navbar'):
            self.navbar.set_active_item(page_name, trigger_command=False)

    def create_page_container(self):
        """Create the container for pages"""
        self.page_container = ctk.CTkFrame(self, fg_color="transparent")
        self.page_container.grid(row=1, column=0, padx=0, pady=0, sticky="nsew")  # Now at row 1
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
            'Console': ProcessPage(
                self.page_container,
                self.state_manager,
                self.event_bus,
                self.script_runner # Pass script_runner here
            ),
            'Scripts': ProjectsPage(
                self.page_container,
                self.state_manager,
                self.event_bus
            ),
            'SOPs': SOPsPage(
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
        self.current_page_widget = None

    def switch_page(self, page_name: str):
        """Switch to a different page"""
        if self.current_page_widget:
            self.current_page_widget.on_deactivate()
            self.current_page_widget.grid_forget()

        if page_name in self.pages:
            self.current_page_widget = self.pages[page_name]
            self.current_page_widget.grid(row=0, column=0, sticky="nsew")
            self.current_page_widget.on_activate()
            self.state_manager.set('current_page', page_name)
        else:
            print(f"Error: Page '{page_name}' not found.")
            # Optionally switch to a default page if the requested one isn't found
            if DEFAULT_PAGE in self.pages:
                self.switch_page(DEFAULT_PAGE)

    def on_status_changed(self, status: str):
        """Handle status state changes - Updated to work with navbar status indicator"""
        # Update the status indicator in the navbar if it exists
        if hasattr(self.navbar, 'status_indicator'):
            self.navbar.status_indicator.set_status(status)

        # If status is success or error, start a timer to reset to idle
        if status in ["success", "error"]:
            # Cancel any existing timer
            if self._status_reset_timer is not None:
                self.after_cancel(self._status_reset_timer)
            self._status_reset_timer = self.after(STATUS_RESET_DELAY, self.revert_status_to_idle)
        # If status becomes running or idle, cancel any pending reset
        elif status in ["running", "idle"]:
            if self._status_reset_timer is not None:
                self.after_cancel(self._status_reset_timer)
                self._status_reset_timer = None

    def revert_status_to_idle(self):
        """Set the status back to idle"""
        self.state_manager.set('status', 'idle')
        self._status_reset_timer = None

    def on_theme_changed(self, theme: str):
        """Handle theme state changes"""
        ctk.set_appearance_mode(theme)
        self.navbar.update_theme()
        # Propagate theme change to current page if it has an update_theme method
        if self.current_page_widget and hasattr(self.current_page_widget, 'update_theme'):
            self.current_page_widget.update_theme()

    def on_closing(self):
        """Handle application closing"""
        # Save current settings before closing
        self.state_manager.save_to_file()

        # Clean up services
        try:
            from services.sound_integration import cleanup_sound_integration
            from services.notification_integration import cleanup_notification_integration
            cleanup_sound_integration()
            cleanup_notification_integration()
        except Exception as e:
            print(f"Error during cleanup: {e}")

        self.destroy()
