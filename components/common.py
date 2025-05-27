"""Common UI components and utilities."""

import customtkinter as ctk
from typing import Optional, Callable, Any


def create_button(
    parent,
    text: str,
    command: Optional[Callable] = None,
    width: int = 120,
    height: int = 35,
    fg_color: Optional[str] = None,
    hover_color: Optional[str] = None,
    **kwargs
) -> ctk.CTkButton:
    """Create a standardized button."""
    return ctk.CTkButton(
        parent,
        text=text,
        command=command,
        width=width,
        height=height,
        fg_color=fg_color,
        hover_color=hover_color,
        **kwargs
    )


def create_label(
    parent,
    text: str,
    font_size: int = 14,
    font_weight: str = "normal",
    text_color: Optional[str] = None,
    **kwargs
) -> ctk.CTkLabel:
    """Create a standardized label."""
    return ctk.CTkLabel(
        parent,
        text=text,
        font=ctk.CTkFont(size=font_size, weight=font_weight),
        text_color=text_color,
        **kwargs
    )


def create_frame(
    parent,
    fg_color: Optional[str] = None,
    corner_radius: int = 10,
    **kwargs
) -> ctk.CTkFrame:
    """Create a standardized frame."""
    return ctk.CTkFrame(
        parent,
        fg_color=fg_color,
        corner_radius=corner_radius,
        **kwargs
    )


def create_textbox(
    parent,
    width: Optional[int] = None,
    height: Optional[int] = None,
    font_family: str = "Consolas",
    font_size: int = 12,
    **kwargs
) -> ctk.CTkTextbox:
    """Create a standardized textbox."""
    # Ensure width is an integer. If no width is provided,
    # use a default value (e.g., 200, or 1 if relying entirely on sticky expansion).
    # Let's use 1 as an example if sticky="nsew" is meant to fully control size.
    actual_width = width if width is not None else 1  # Or another default like 200

    return ctk.CTkTextbox(
        parent,
        font=ctk.CTkFont(family=font_family, size=font_size),
        width=actual_width,  # Pass the ensured numerical width
        height=height,
        **kwargs
    )


def create_progress_bar(
    parent,
    width: int = 400,
    height: int = 20,
    mode: str = "indeterminate",
    **kwargs
) -> ctk.CTkProgressBar:
    """Create a standardized progress bar."""
    return ctk.CTkProgressBar(
        parent,
        width=width,
        height=height,
        mode=mode,
        **kwargs
    )


class MessageBox:
    """Simple message box utility."""
    
    @staticmethod
    def show_info(parent, title: str, message: str):
        """Show an info message."""
        dialog = ctk.CTkInputDialog(text=message, title=title)
        return dialog.get_input()
    
    @staticmethod
    def show_error(parent, title: str, message: str):
        """Show an error message."""
        dialog = ctk.CTkInputDialog(text=f"Error: {message}", title=title)
        return dialog.get_input()
    
    @staticmethod
    def ask_yes_no(parent, title: str, message: str) -> bool:
        """Ask a yes/no question."""
        # This is a simplified implementation
        # You might want to create a custom dialog for better UX
        result = ctk.CTkInputDialog(text=f"{message} (yes/no)", title=title).get_input()
        return result and result.lower() in ['yes', 'y', '1', 'true']


def apply_theme_to_widget(widget, theme_colors: dict):
    """Apply theme colors to a widget."""
    if hasattr(widget, 'configure'):
        applicable_colors = {}
        widget_type = type(widget).__name__
        
        # Map theme colors to widget properties based on widget type
        color_mapping = {
            'CTkFrame': ['fg_color'],
            'CTkButton': ['fg_color', 'hover_color', 'text_color'],
            'CTkLabel': ['text_color', 'fg_color'],
            'CTkTextbox': ['fg_color', 'text_color'],
            'CTkEntry': ['fg_color', 'text_color'],
        }
        
        if widget_type in color_mapping:
            for prop in color_mapping[widget_type]:
                if prop in theme_colors:
                    applicable_colors[prop] = theme_colors[prop]
        
        if applicable_colors:
            widget.configure(**applicable_colors)
