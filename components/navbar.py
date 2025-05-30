"""Modern navigation bar component with integrated status indicator"""

import customtkinter as ctk
from config.themes import COLORS
from PIL import Image
from config.settings import (
    NAV_ITEMS, DEFAULT_PAGE, NAVBAR_CORNER_RADIUS,
    NAV_BUTTON_WIDTH, NAV_BUTTON_HEIGHT, BUTTON_CORNER_RADIUS,
    LOGO_SIZE, LOGO_CORNER_RADIUS
)
from components.status_bar import StatusIndicator


class ModernNavbar(ctk.CTkFrame):
    """A modern navbar component with integrated status indicator"""

    def __init__(self, master, command=None):
        super().__init__(master, fg_color=("gray85", "#212121"), corner_radius=NAVBAR_CORNER_RADIUS)

        self.command = command
        self.active_item = DEFAULT_PAGE
        self.nav_items = NAV_ITEMS

        # Store color schemes
        self.colors = COLORS

        # Configure the frame
        self.grid_columnconfigure(1, weight=1)

        # Create components
        self.create_logo()
        self.create_nav_items()

    def create_logo(self):
        """Create the logo section"""
        self.logo_frame = ctk.CTkFrame(
            self,
            fg_color="transparent", # Make logo frame transparent
            width=LOGO_SIZE,
            height=LOGO_SIZE,
            corner_radius=LOGO_CORNER_RADIUS
        )
        self.logo_frame.grid(row=0, column=0, padx=(10, 10), pady=5)
        self.logo_frame.grid_propagate(False)

        # Load and display the image
        try:
            # Define the path to your icon
            icon_path = "assets/icons/kodiak.png" # Make sure this path is correct relative to where your app runs
            pil_image = Image.open(icon_path)
            self.logo_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(LOGO_SIZE, LOGO_SIZE))

            self.logo_label = ctk.CTkLabel(
                self.logo_frame,
                image=self.logo_image,
                text="" # No text needed
            )
            self.logo_label.place(relx=0.5, rely=0.5, anchor="center")

        except FileNotFoundError:
            # Fallback to text if image not found
            print(f"Error: Icon image not found at {icon_path}. Using text fallback.")
            self.logo_label = ctk.CTkLabel(
                self.logo_frame,
                text="/", # Fallback text
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color=self.colors["logo_text"]
            )
            self.logo_label.place(relx=0.5, rely=0.5, anchor="center")
            # You might want to set a background color for the frame if the image fails to load
            self.logo_frame.configure(fg_color=self.colors["logo_bg"])

    def create_nav_items(self):
        """Create the navigation items with integrated status indicator"""
        nav_container = ctk.CTkFrame(self, fg_color="transparent")
        nav_container.grid(row=0, column=1, sticky="e", padx=(10, 20), pady=10)

        # Create status indicator within nav_container
        self.status_indicator = StatusIndicator(nav_container)
        self.status_indicator.grid(row=0, column=0, padx=(0, 30), pady=0)

        self.nav_buttons = {}

        for i, item in enumerate(self.nav_items):
            btn = ctk.CTkButton(
                nav_container,
                text=item,
                width=NAV_BUTTON_WIDTH,
                height=NAV_BUTTON_HEIGHT,
                corner_radius=BUTTON_CORNER_RADIUS,
                fg_color=self.colors["active_bg"] if item == self.active_item else "transparent",
                hover_color=self.colors["active_hover"] if item == self.active_item else self.colors["inactive_hover"],
                text_color=self.colors["active_text"] if item == self.active_item else self.colors["inactive_text"],
                font=ctk.CTkFont(size=14, weight="bold" if item == self.active_item else "normal"),
                command=lambda x=item: self.set_active_item(x)
            )
            btn.grid(row=0, column=i + 1, padx=2)  # +1 to account for status indicator
            self.nav_buttons[item] = btn

    def set_active_item(self, item, trigger_command=True):
        """Set the active navigation item

        Args:
            item: The navigation item to set as active
            trigger_command: Whether to call the command callback (default True)
        """
        self.active_item = item

        # Update all buttons
        for nav_item, btn in self.nav_buttons.items():
            if nav_item == item:
                btn.configure(
                    fg_color=self.colors["active_bg"],
                    hover_color=self.colors["active_hover"],
                    text_color=self.colors["active_text"],
                    font=ctk.CTkFont(size=14, weight="bold")
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    hover_color=self.colors["inactive_hover"],
                    text_color=self.colors["inactive_text"],
                    font=ctk.CTkFont(size=14, weight="normal")
                )

        # Call the command if provided and trigger_command is True
        if self.command and trigger_command:
            self.command(item)

    def update_theme(self):
        """Update the navbar colors when theme changes."""

        # Check if the logo is in image mode (i.e., self.logo_image was successfully created)
        if hasattr(self, 'logo_image') and self.logo_label.cget("image"):
            self.logo_frame.configure(fg_color="transparent")
        else:
            self.logo_frame.configure(fg_color=self.colors["logo_bg"])
            if hasattr(self, 'logo_label'):
                self.logo_label.configure(text_color=self.colors["logo_text"])

        # Update all navigation buttons
        for nav_item, btn in self.nav_buttons.items():
            if nav_item == self.active_item:
                btn.configure(
                    fg_color=self.colors["active_bg"],
                    hover_color=self.colors["active_hover"],
                    text_color=self.colors["active_text"]
                )
            else:
                btn.configure(
                    hover_color=self.colors["inactive_hover"],
                    text_color=self.colors["inactive_text"]
                )
