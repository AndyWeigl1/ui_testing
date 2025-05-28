"""Theme configurations for the application"""

COLORS = {
    "active_bg": ("#1f6aa5", "#1f6aa5"),  # (light, dark) - Blue for both themes
    "active_hover": ("#144870", "#144870"),
    "inactive_hover": ("gray75", "#374151"),
    "active_text": "white",
    "inactive_text": ("gray20", "#d1d5db"),
    "logo_bg": ("#1f6aa5", "white"),
    "logo_text": ("white", "#212121"),

    # Button colors
    "run_button": "#4CAF50",
    "run_button_hover": "#45a049",
    "stop_button": "#bb2332",
    "stop_button_hover": "#78161f",
    "clear_button": "#757575",
    "clear_button_hover": "#616161",

    # Status colors
    "status_idle": "#4CAF50",
    "status_running": "#FF9800",

    # Output console colors
    "output_info": ("gray20", "gray80"),
    "output_success": "#4CAF50",
    "output_error": "#f44336",
    "output_warning": "#FF9800",
    "output_system": "#2196F3",
    "output_timestamp": "gray"
}

# Theme settings
DEFAULT_APPEARANCE = "dark"
DEFAULT_COLOR_THEME = "blue"
