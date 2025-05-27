"""Application settings and constants"""

# Window configuration
WINDOW_TITLE = "Script Runner - Modern UI"
WINDOW_SIZE = (700, 600)
MIN_SIZE = (700, 600)

# Navigation
NAV_ITEMS = ["About", "Projects", "Process", "Settings"]
DEFAULT_PAGE = "About"

# Font settings
DEFAULT_FONT_FAMILY = "Consolas"
DEFAULT_FONT_SIZE = 12
MIN_FONT_SIZE = 10
MAX_FONT_SIZE = 18
FONT_SIZE_STEPS = 8

# UI dimensions
NAVBAR_CORNER_RADIUS = 25
BUTTON_CORNER_RADIUS = 20
LOGO_SIZE = 32
LOGO_CORNER_RADIUS = 6
NAV_BUTTON_WIDTH = 100
NAV_BUTTON_HEIGHT = 35
CONTROL_BUTTON_WIDTH = 120
CONTROL_BUTTON_HEIGHT = 40

# Timing
OUTPUT_CHECK_INTERVAL = 100  # milliseconds
SCRIPT_SIMULATION_DELAY = 1  # seconds

# Script simulation data
SIMULATION_OPERATIONS = [
    "Initializing components...",
    "Loading configuration...",
    "Connecting to database...",
    "Fetching data...",
    "Processing records...",
    "Generating report...",
    "Finalizing operations..."
]