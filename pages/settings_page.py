"""Settings page - application configuration"""

import customtkinter as ctk
from pages.base_page import BasePage
from config.settings import MIN_FONT_SIZE, MAX_FONT_SIZE, FONT_SIZE_STEPS


class SettingsPage(BasePage):
    """Settings page for application configuration"""
    
    def setup_ui(self):
        """Set up the Settings page UI"""
        # Main container with scrolling
        self.scrollable_frame = ctk.CTkScrollableFrame(self)
        self.scrollable_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        
        # Page title
        title_label = ctk.CTkLabel(
            self.scrollable_frame,
            text="Settings",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.grid(row=0, column=0, pady=(0, 30), sticky="w")
        
        # Appearance section
        appearance_section = self.create_settings_section(
            "Appearance",
            self.scrollable_frame,
            row=1
        )
        self.create_appearance_settings(appearance_section.content_frame)
        
        # Console section
        console_section = self.create_settings_section(
            "Console",
            self.scrollable_frame,
            row=2
        )
        self.create_console_settings(console_section.content_frame)
        
        # Script Execution section
        execution_section = self.create_settings_section(
            "Script Execution",
            self.scrollable_frame,
            row=3
        )
        self.create_execution_settings(execution_section.content_frame)
        
        # Advanced section
        advanced_section = self.create_settings_section(
            "Advanced",
            self.scrollable_frame,
            row=4
        )
        self.create_advanced_settings(advanced_section.content_frame)
        
        # Save/Reset buttons
        button_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        button_frame.grid(row=5, column=0, pady=(30, 0), sticky="ew")
        button_frame.grid_columnconfigure(0, weight=1)
        
        save_btn = ctk.CTkButton(
            button_frame,
            text="Save Settings",
            command=self.save_settings
        )
        save_btn.grid(row=0, column=1, padx=5)
        
        reset_btn = ctk.CTkButton(
            button_frame,
            text="Reset to Defaults",
            fg_color=("gray70", "gray30"),
            command=self.reset_settings
        )
        reset_btn.grid(row=0, column=2, padx=5)

    def on_developer_mode_changed(self):
        """Handle developer mode toggle in settings"""
        developer_mode = self.developer_mode_var.get()
        self.set_state('developer_mode', developer_mode)
        self.publish_event('developer_mode.changed', {'enabled': developer_mode})

    def create_settings_section(self, title: str, parent, row: int) -> ctk.CTkFrame:
        """Create a settings section with consistent styling"""
        section = ctk.CTkFrame(parent)
        section.grid(row=row, column=0, pady=(0, 20), sticky="ew")
        section.grid_columnconfigure(0, weight=1)
        
        # Section title
        title_label = ctk.CTkLabel(
            section,
            text=title,
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=20, pady=(15, 10), sticky="w")
        
        # Content frame
        content_frame = ctk.CTkFrame(section, fg_color="transparent")
        content_frame.grid(row=1, column=0, padx=40, pady=(0, 15), sticky="ew")
        content_frame.grid_columnconfigure(1, weight=1)
        
        section.content_frame = content_frame
        return section
        
    def create_appearance_settings(self, parent):
        """Create appearance settings"""
        row = 0
        
        # Theme
        theme_label = ctk.CTkLabel(parent, text="Theme:")
        theme_label.grid(row=row, column=0, sticky="w", pady=5)
        
        self.theme_var = ctk.StringVar(value=self.get_state('theme', 'dark'))
        theme_menu = ctk.CTkOptionMenu(
            parent,
            values=["dark", "light"],
            variable=self.theme_var,
            command=self.on_theme_changed
        )
        theme_menu.grid(row=row, column=1, sticky="w", pady=5)
        row += 1
        
        # Accent color (placeholder)
        accent_label = ctk.CTkLabel(parent, text="Accent Color:")
        accent_label.grid(row=row, column=0, sticky="w", pady=5)
        
        self.accent_var = ctk.StringVar(value="blue")
        accent_menu = ctk.CTkOptionMenu(
            parent,
            values=["blue", "green", "red", "purple"],
            variable=self.accent_var,
            state="disabled"  # Not implemented yet
        )
        accent_menu.grid(row=row, column=1, sticky="w", pady=5)
        row += 1
        
    def create_console_settings(self, parent):
        """Create console settings"""
        row = 0
        
        # Font size
        font_label = ctk.CTkLabel(parent, text="Font Size:")
        font_label.grid(row=row, column=0, sticky="w", pady=5)
        
        font_frame = ctk.CTkFrame(parent, fg_color="transparent")
        font_frame.grid(row=row, column=1, sticky="ew", pady=5)
        
        self.font_size_var = ctk.IntVar(value=self.get_state('font_size', 12))
        self.font_size_label = ctk.CTkLabel(
            font_frame,
            text=f"{self.font_size_var.get()}px"
        )
        self.font_size_label.grid(row=0, column=0, padx=(0, 10))
        
        font_slider = ctk.CTkSlider(
            font_frame,
            from_=MIN_FONT_SIZE,
            to=MAX_FONT_SIZE,
            number_of_steps=FONT_SIZE_STEPS,
            variable=self.font_size_var,
            command=self.on_font_size_changed
        )
        font_slider.grid(row=0, column=1, sticky="ew")
        font_frame.grid_columnconfigure(1, weight=1)
        row += 1
        
        # Font family (placeholder)
        font_family_label = ctk.CTkLabel(parent, text="Font Family:")
        font_family_label.grid(row=row, column=0, sticky="w", pady=5)
        
        self.font_family_var = ctk.StringVar(value="Consolas")
        font_family_menu = ctk.CTkOptionMenu(
            parent,
            values=["Consolas", "Courier New", "Monaco", "Ubuntu Mono"],
            variable=self.font_family_var,
            state="disabled"  # Not implemented yet
        )
        font_family_menu.grid(row=row, column=1, sticky="w", pady=5)
        row += 1
        
        # Line wrap
        self.line_wrap_var = ctk.BooleanVar(value=True)
        line_wrap_check = ctk.CTkCheckBox(
            parent,
            text="Wrap long lines",
            variable=self.line_wrap_var,
            state="disabled"  # Not implemented yet
        )
        line_wrap_check.grid(row=row, column=0, columnspan=2, sticky="w", pady=5)
        row += 1

    def create_execution_settings(self, parent):
        """Create script execution settings"""
        row = 0

        # Auto-scroll
        self.auto_scroll_var = ctk.BooleanVar(value=True)
        auto_scroll_check = ctk.CTkCheckBox(
            parent,
            text="Auto-scroll to bottom on new output",
            variable=self.auto_scroll_var
        )
        auto_scroll_check.grid(row=row, column=0, columnspan=2, sticky="w", pady=5)
        row += 1

        # Clear on run
        self.clear_on_run_var = ctk.BooleanVar(value=False)
        clear_on_run_check = ctk.CTkCheckBox(
            parent,
            text="Clear console before running script",
            variable=self.clear_on_run_var
        )
        clear_on_run_check.grid(row=row, column=0, columnspan=2, sticky="w", pady=5)
        row += 1

        # Developer mode - NEW ADDITION
        self.developer_mode_var = ctk.BooleanVar(value=self.get_state('developer_mode', False))
        developer_mode_check = ctk.CTkCheckBox(
            parent,
            text="Developer mode (show debug output)",
            variable=self.developer_mode_var,
            command=self.on_developer_mode_changed
        )
        developer_mode_check.grid(row=row, column=0, columnspan=2, sticky="w", pady=5)

        # Add help text for developer mode
        dev_help_label = ctk.CTkLabel(
            parent,
            text="    Enables detailed debug output for troubleshooting",
            font=ctk.CTkFont(size=11),
            text_color=("gray30", "gray70")
        )
        dev_help_label.grid(row=row + 1, column=0, columnspan=2, sticky="w", padx=(25, 0))
        row += 2

        # Output buffer size (placeholder)
        buffer_label = ctk.CTkLabel(parent, text="Output Buffer Size:")
        buffer_label.grid(row=row, column=0, sticky="w", pady=5)

        self.buffer_size_var = ctk.StringVar(value="1000 lines")
        buffer_entry = ctk.CTkEntry(
            parent,
            textvariable=self.buffer_size_var,
            state="disabled"  # Not implemented yet
        )
        buffer_entry.grid(row=row, column=1, sticky="w", pady=5)
        row += 1
        
    def create_advanced_settings(self, parent):
        """Create advanced settings"""
        row = 0
        
        # Debug mode
        self.debug_mode_var = ctk.BooleanVar(value=False)
        debug_check = ctk.CTkCheckBox(
            parent,
            text="Enable debug mode",
            variable=self.debug_mode_var
        )
        debug_check.grid(row=row, column=0, columnspan=2, sticky="w", pady=5)
        row += 1
        
        # Log level (placeholder)
        log_label = ctk.CTkLabel(parent, text="Log Level:")
        log_label.grid(row=row, column=0, sticky="w", pady=5)
        
        self.log_level_var = ctk.StringVar(value="INFO")
        log_menu = ctk.CTkOptionMenu(
            parent,
            values=["DEBUG", "INFO", "WARNING", "ERROR"],
            variable=self.log_level_var,
            state="disabled"  # Not implemented yet
        )
        log_menu.grid(row=row, column=1, sticky="w", pady=5)
        row += 1
        
        # Export settings button
        export_btn = ctk.CTkButton(
            parent,
            text="Export Settings",
            command=self.export_settings,
            fg_color=("gray70", "gray30")
        )
        export_btn.grid(row=row, column=0, pady=(10, 0))
        
        # Import settings button
        import_btn = ctk.CTkButton(
            parent,
            text="Import Settings",
            command=self.import_settings,
            fg_color=("gray70", "gray30")
        )
        import_btn.grid(row=row, column=1, sticky="w", padx=(10, 0), pady=(10, 0))
        
    def on_theme_changed(self, theme: str):
        """Handle theme change"""
        self.set_state('theme', theme)
        self.publish_event('theme.changed', {'theme': theme})
        
    def on_font_size_changed(self, size: float):
        """Handle font size change"""
        size = int(size)
        self.font_size_label.configure(text=f"{size}px")
        self.set_state('font_size', size)
        self.publish_event('font_size.changed', {'size': size})

    def save_settings(self):
        """Save current settings"""
        # In a real app, this would persist settings to file
        settings = {
            'theme': self.theme_var.get(),
            'font_size': self.font_size_var.get(),
            'auto_scroll': self.auto_scroll_var.get(),
            'clear_on_run': self.clear_on_run_var.get(),
            'developer_mode': self.developer_mode_var.get(),  # Add this line
            'debug_mode': self.debug_mode_var.get(),
        }

        # Update state
        self.state_manager.update(settings)

        self.show_message("Settings saved successfully!", "success")
        self.publish_event('settings.saved', {'settings': settings})
        
    def reset_settings(self):
        """Reset settings to defaults"""
        # Reset to defaults
        self.theme_var.set('dark')
        self.font_size_var.set(12)
        self.auto_scroll_var.set(True)
        self.clear_on_run_var.set(False)
        self.debug_mode_var.set(False)
        
        # Update UI
        self.font_size_label.configure(text="12px")
        
        # Save the reset settings
        self.save_settings()
        self.show_message("Settings reset to defaults", "info")
        
    def export_settings(self):
        """Export settings to file"""
        self.show_message("Settings export not yet implemented", "info")
        
    def import_settings(self):
        """Import settings from file"""
        self.show_message("Settings import not yet implemented", "info")

    def on_activate(self):
        """Called when settings page becomes active"""
        super().on_activate()

        # Update UI to reflect current state
        self.theme_var.set(self.get_state('theme', 'dark'))
        self.font_size_var.set(self.get_state('font_size', 12))
        self.font_size_label.configure(text=f"{self.font_size_var.get()}px")
        self.developer_mode_var.set(self.get_state('developer_mode', False))  # Add this line
