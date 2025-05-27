"""Modern navigation bar component"""

import customtkinter as ctk
from config.themes import COLORS
from config.settings import (
    NAV_ITEMS, DEFAULT_PAGE, NAVBAR_CORNER_RADIUS,
    NAV_BUTTON_WIDTH, NAV_BUTTON_HEIGHT, BUTTON_CORNER_RADIUS,
    LOGO_SIZE, LOGO_CORNER_RADIUS
)


class ModernNavbar(ctk.CTkFrame):
    """A modern navbar component similar to the React design"""

    def __init__(self, master, command=None):
        super().__init__(master, fg_color=("gray85", "#212121"), corner_radius=NAVBAR_CORNER_RADIUS)

        self.command = command
        self.active_item = DEFAULT_PAGE
        self.nav_items = NAV_ITEMS

        # Store color schemes
        self.colors = COLORS

        # Configure the frame
        self.grid_columnconfigure(1, weight=1)

        # Create logo
        self.create_logo()

        # Create navigation items
        self.create_nav_items()

    def create_logo(self):
        """Create the logo section"""
        self.logo_frame = ctk.CTkFrame(
            self,
            fg_color=self.colors["logo_bg"],
            width=LOGO_SIZE,
            height=LOGO_SIZE,
            corner_radius=LOGO_CORNER_RADIUS
        )
        self.logo_frame.grid(row=0, column=0, padx=(20, 10), pady=10)
        self.logo_frame.grid_propagate(False)

        # Logo slash with rotation effect (simulated)
        self.logo_label = ctk.CTkLabel(
            self.logo_frame,
            text="/",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.colors["logo_text"]
        )
        self.logo_label.place(relx=0.5, rely=0.5, anchor="center")

    def create_nav_items(self):
        """Create the navigation items"""
        nav_container = ctk.CTkFrame(self, fg_color="transparent")
        nav_container.grid(row=0, column=1, sticky="e", padx=(10, 20), pady=10)

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
            btn.grid(row=0, column=i, padx=2)
            self.nav_buttons[item] = btn

    def set_active_item(self, item):
        """Set the active navigation item"""
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

        # Call the command if provided
        if self.command:
            self.command(item)

    def update_theme(self):
        """Update the navbar colors when theme changes"""
        # The CTkFrame automatically updates its fg_color
        # We need to update logo and buttons manually
        self.logo_frame.configure(fg_color=self.colors["logo_bg"])
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