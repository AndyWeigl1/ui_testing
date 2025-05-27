"""Main application class"""

import customtkinter as ctk

from components.navbar import ModernNavbar
from components.status_bar import StatusIndicator
from pages import AboutPage, ProcessPage, ProjectsPage, SettingsPage
from services.script_runner import ScriptRunner
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

    def setup_state_subscriptions(self):
        """Set up state subscriptions for reactive UI updates"""
        # Subscribe to state changes
        self.state_manager.subscribe('status', self.on_status_changed)
        self.state_manager.subscribe('theme', self.on_theme_changed)

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

    def on_status_changed(self, status):
        """Handle status state changes"""
        self.status_indicator.set_status(status)

    def on_theme_changed(self, theme):
        """Handle theme state changes"""
        ctk.set_appearance_mode(theme)
        self.navbar.update_theme()
