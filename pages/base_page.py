"""Enhanced base page class with scroll speed improvements"""

import customtkinter as ctk
from typing import Optional, Dict, Any
from utils.state_manager import StateManager
from utils.event_bus import EventBus


class BasePage(ctk.CTkFrame):
    """Abstract base class for all application pages with improved scrolling"""

    def __init__(
        self,
        parent,
        state_manager: StateManager,
        event_bus: EventBus,
        **kwargs
    ):
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

    def create_fast_scrollable_frame(self, parent, **kwargs) -> ctk.CTkScrollableFrame:
        """Create a scrollable frame with improved scroll speed

        Args:
            parent: Parent widget for the scrollable frame
            **kwargs: Additional arguments for CTkScrollableFrame

        Returns:
            CTkScrollableFrame with improved scrolling
        """
        # Create the scrollable frame
        scrollable_frame = ctk.CTkScrollableFrame(parent, **kwargs)

        # Configure faster scrolling
        self.configure_scroll_speed(scrollable_frame)

        return scrollable_frame

    def configure_scroll_speed(self, scrollable_frame: ctk.CTkScrollableFrame, speed_factor: int = 100):
        """Configure mouse wheel scroll speed for a scrollable frame

        Args:
            scrollable_frame: The CTkScrollableFrame to configure
            speed_factor: Multiplier for scroll speed (higher = faster)
        """
        def _on_mousewheel(event):
            # Calculate scroll amount based on speed factor
            if event.delta:
                # Windows
                delta = -1 * (event.delta / 120) * speed_factor
            else:
                # Linux
                if event.num == 4:
                    delta = -speed_factor
                elif event.num == 5:
                    delta = speed_factor
                else:
                    delta = 0

            # Scroll the canvas
            scrollable_frame._parent_canvas.yview_scroll(int(delta), "units")

        # Bind mouse wheel events to the scrollable frame and its canvas
        def bind_scroll_events(widget):
            # Windows and MacOS
            widget.bind("<MouseWheel>", _on_mousewheel)
            # Linux
            widget.bind("<Button-4>", _on_mousewheel)
            widget.bind("<Button-5>", _on_mousewheel)

        # Apply to the scrollable frame itself
        bind_scroll_events(scrollable_frame)

        # Apply to the internal canvas if accessible
        if hasattr(scrollable_frame, '_parent_canvas'):
            bind_scroll_events(scrollable_frame._parent_canvas)

        # Apply to all child widgets recursively
        def bind_to_children(widget):
            bind_scroll_events(widget)
            for child in widget.winfo_children():
                try:
                    bind_to_children(child)
                except:
                    pass  # Skip if widget doesn't support binding

        # Bind after a short delay to ensure all children are created
        scrollable_frame.after(100, lambda: bind_to_children(scrollable_frame))

    # Rest of the BasePage methods remain the same...
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
        """Called when the page becomes active"""
        self.is_active = True
        self.event_bus.publish(f'page.{self.page_name.lower()}.activated', {
            'page': self.page_name
        })

    def on_deactivate(self):
        """Called when the page becomes inactive"""
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
        """Create a standard section frame with title"""
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
        """Create a standard info label"""
        return ctk.CTkLabel(
            parent,
            text=text,
            font=ctk.CTkFont(size=14),
            justify="left",
            **kwargs
        )

    def show_message(self, message: str, message_type: str = "info"):
        """Show a message to the user"""
        self.event_bus.publish('page.message', {
            'message': message,
            'type': message_type,
            'page': self.page_name
        })

    def cleanup(self):
        """Clean up resources when page is destroyed"""
        pass
