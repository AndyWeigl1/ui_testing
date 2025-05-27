"""Base page class for all application pages"""

import customtkinter as ctk
from typing import Optional, Dict, Any
from utils.state_manager import StateManager
from utils.event_bus import EventBus


class BasePage(ctk.CTkFrame):
    """Abstract base class for all application pages
    
    Provides common functionality and structure for pages including:
    - State management integration
    - Event bus access
    - Lifecycle methods
    - Common UI helpers
    """
    
    def __init__(
        self,
        parent,
        state_manager: StateManager,
        event_bus: EventBus,
        **kwargs
    ):
        """Initialize the base page
        
        Args:
            parent: Parent widget
            state_manager: Application state manager instance
            event_bus: Application event bus instance
            **kwargs: Additional arguments passed to CTkFrame
        """
        super().__init__(parent, **kwargs)
        
        # Store references
        self.state_manager = state_manager
        self.event_bus = event_bus
        self.parent = parent
        
        # Page metadata
        self.page_name = self.__class__.__name__.replace('Page', '')
        self.is_active = False
        
        # Configure the frame
        self.configure(fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Initialize the page
        self._initialize()
        
    def _initialize(self):
        """Initialize the page (called once during construction)"""
        # Set up state subscriptions
        self.setup_state_subscriptions()
        
        # Set up event subscriptions
        self.setup_event_subscriptions()
        
        # Create the UI
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the page UI - Override in subclasses"""
        raise NotImplementedError(f"{self.__class__.__name__} must implement setup_ui()")
        
    def setup_state_subscriptions(self):
        """Set up state subscriptions - Override in subclasses if needed"""
        pass
        
    def setup_event_subscriptions(self):
        """Set up event subscriptions - Override in subclasses if needed"""
        pass
        
    def on_activate(self):
        """Called when the page becomes active
        
        Override in subclasses to handle page activation
        (e.g., refresh data, start timers, etc.)
        """
        self.is_active = True
        self.event_bus.publish(f'page.{self.page_name.lower()}.activated', {
            'page': self.page_name
        })
        
    def on_deactivate(self):
        """Called when the page becomes inactive
        
        Override in subclasses to handle page deactivation
        (e.g., save state, stop timers, etc.)
        """
        self.is_active = False
        self.event_bus.publish(f'page.{self.page_name.lower()}.deactivated', {
            'page': self.page_name
        })
        
    def refresh(self):
        """Refresh the page content - Override in subclasses if needed"""
        pass
        
    def get_state(self, key: str, default: Any = None) -> Any:
        """Convenience method to get state value"""
        return self.state_manager.get(key, default)
        
    def set_state(self, key: str, value: Any):
        """Convenience method to set state value"""
        self.state_manager.set(key, value)
        
    def publish_event(self, event_name: str, data: Optional[Dict[str, Any]] = None):
        """Convenience method to publish events"""
        self.event_bus.publish(event_name, data)
        
    def create_section(self, title: str, parent=None) -> ctk.CTkFrame:
        """Create a standard section frame with title
        
        Args:
            title: Section title
            parent: Parent widget (defaults to self)
            
        Returns:
            CTkFrame: The section frame
        """
        if parent is None:
            parent = self
            
        section = ctk.CTkFrame(parent)
        section.grid_columnconfigure(0, weight=1)
        
        # Section title
        title_label = ctk.CTkLabel(
            section,
            text=title,
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        
        # Content frame
        content_frame = ctk.CTkFrame(section, fg_color="transparent")
        content_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        content_frame.grid_columnconfigure(0, weight=1)
        section.grid_rowconfigure(1, weight=1)
        
        # Store reference to content frame
        section.content_frame = content_frame
        
        return section
        
    def create_info_label(self, parent, text: str, **kwargs) -> ctk.CTkLabel:
        """Create a standard info label
        
        Args:
            parent: Parent widget
            text: Label text
            **kwargs: Additional arguments for CTkLabel
            
        Returns:
            CTkLabel: The created label
        """
        return ctk.CTkLabel(
            parent,
            text=text,
            font=ctk.CTkFont(size=14),
            justify="left",
            **kwargs
        )
        
    def show_message(self, message: str, message_type: str = "info"):
        """Show a message to the user
        
        Args:
            message: The message to show
            message_type: Type of message (info, success, warning, error)
        """
        # This could be implemented as a toast notification or status bar update
        # For now, we'll publish an event that the main app can handle
        self.event_bus.publish('page.message', {
            'message': message,
            'type': message_type,
            'page': self.page_name
        })
        
    def cleanup(self):
        """Clean up resources when page is destroyed
        
        Override in subclasses if cleanup is needed
        """
        pass
