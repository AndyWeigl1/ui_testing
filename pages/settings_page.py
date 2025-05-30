"""Settings page - application configuration (CLEANED VERSION)"""

import customtkinter as ctk
from pages.base_page import BasePage
from config.settings import MIN_FONT_SIZE, MAX_FONT_SIZE, FONT_SIZE_STEPS
from services.sound_manager import get_sound_manager
from services.notification_manager import get_notification_manager


class SettingsPage(BasePage):
    """Settings page for application configuration"""

    def setup_ui(self):
        """Set up the Settings page UI"""
        # Main container with scrolling
        self.scrollable_frame = self.create_fast_scrollable_frame(self)
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

        # Sound section
        sound_section = self.create_settings_section(
            "Sound Notifications",
            self.scrollable_frame,
            row=3
        )
        self.create_sound_settings(sound_section.content_frame)

        # System Notifications section
        notification_section = self.create_settings_section(
            "System Notifications",
            self.scrollable_frame,
            row=4
        )
        self.create_notification_settings(notification_section.content_frame)

        # Script Execution section
        execution_section = self.create_settings_section(
            "Script Execution",
            self.scrollable_frame,
            row=5
        )
        self.create_execution_settings(execution_section.content_frame)

        # Save/Reset buttons (updated row number since Advanced section was removed)
        button_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        button_frame.grid(row=6, column=0, pady=(30, 0), sticky="ew")
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
        """Create appearance settings (cleaned - removed accent color)"""
        row = 0

        # Theme
        theme_label = ctk.CTkLabel(parent, text="Theme:  ")
        theme_label.grid(row=row, column=0, sticky="w", pady=5)

        self.theme_var = ctk.StringVar(value=self.get_state('theme', 'dark'))
        theme_menu = ctk.CTkOptionMenu(
            parent,
            values=["dark", "light"],
            variable=self.theme_var,
            command=self.on_theme_changed
        )
        theme_menu.grid(row=row, column=1, sticky="w", pady=5)

    def create_console_settings(self, parent):
        """Create console settings (cleaned - removed font family and line wrap)"""
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

    def create_sound_settings(self, parent):
        """Create sound notification settings"""
        row = 0

        # Get sound manager
        self.sound_manager = get_sound_manager()

        # Enable sounds
        self.sounds_enabled_var = ctk.BooleanVar(value=self.get_state('sounds_enabled', True))
        sounds_check = ctk.CTkCheckBox(
            parent,
            text="Enable sound notifications",
            variable=self.sounds_enabled_var,
            command=self.on_sounds_enabled_changed
        )
        sounds_check.grid(row=row, column=0, columnspan=2, sticky="w", pady=5)
        row += 1

        # Volume control
        volume_label = ctk.CTkLabel(parent, text="Volume:")
        volume_label.grid(row=row, column=0, sticky="w", pady=5)

        volume_frame = ctk.CTkFrame(parent, fg_color="transparent")
        volume_frame.grid(row=row, column=1, sticky="ew", pady=5)

        self.volume_var = ctk.DoubleVar(value=self.get_state('sound_volume', 0.7))
        self.volume_label = ctk.CTkLabel(
            volume_frame,
            text=f"{int(self.volume_var.get() * 100)}%"
        )
        self.volume_label.grid(row=0, column=0, padx=(0, 10))

        volume_slider = ctk.CTkSlider(
            volume_frame,
            from_=0.0,
            to=1.0,
            variable=self.volume_var,
            command=self.on_volume_changed
        )
        volume_slider.grid(row=0, column=1, sticky="ew")
        volume_frame.grid_columnconfigure(1, weight=1)
        row += 1

        # Sound test buttons
        test_label = ctk.CTkLabel(parent, text="Test Sounds:")
        test_label.grid(row=row, column=0, sticky="w", pady=5)

        test_frame = ctk.CTkFrame(parent, fg_color="transparent")
        test_frame.grid(row=row, column=1, sticky="ew", pady=5)

        # Get available sounds
        available_sounds = self.sound_manager.get_available_sounds()

        # Create test buttons for each sound type
        col = 0
        for sound_type, description in available_sounds.items():
            if sound_type in ['success', 'error', 'start']:  # Only show main sounds
                test_btn = ctk.CTkButton(
                    test_frame,
                    text=f"♪ {sound_type.title()}",
                    width=80,
                    height=28,
                    command=lambda st=sound_type: self.test_sound(st),
                    fg_color=("gray70", "gray30")
                )
                test_btn.grid(row=0, column=col, padx=(0, 5))
                col += 1

        row += 1

        # Sound notification types
        notifications_label = ctk.CTkLabel(parent, text="Play sounds for:")
        notifications_label.grid(row=row, column=0, sticky="w", pady=(15, 5))
        row += 1

        # Individual sound type toggles
        self.sound_type_vars = {}

        sound_types = [
            ('script_success', 'Script completes successfully'),
            ('script_error', 'Script fails or encounters an error'),
            ('script_start', 'Script execution begins')
        ]

        for sound_key, description in sound_types:
            self.sound_type_vars[sound_key] = ctk.BooleanVar(
                value=self.get_state(f'sound_{sound_key}', True)
            )

            sound_check = ctk.CTkCheckBox(
                parent,
                text=description,
                variable=self.sound_type_vars[sound_key]
            )
            sound_check.grid(row=row, column=0, columnspan=2, sticky="w", padx=(20, 0), pady=2)
            row += 1

    def create_notification_settings(self, parent):
        """Create system notification settings"""
        row = 0

        # Get notification manager
        self.notification_manager = get_notification_manager()

        # Enable system notifications
        self.notifications_enabled_var = ctk.BooleanVar(value=self.get_state('notifications_enabled', True))
        notifications_check = ctk.CTkCheckBox(
            parent,
            text="Enable system notifications",
            variable=self.notifications_enabled_var,
            command=self.on_notifications_enabled_changed
        )
        notifications_check.grid(row=row, column=0, columnspan=2, sticky="w", pady=5)
        row += 1

        # NEW: Silent notifications toggle
        self.silent_notifications_var = ctk.BooleanVar(value=self.get_state('silent_notifications', True))
        silent_notifications_check = ctk.CTkCheckBox(
            parent,
            text="Silent system notifications (no OS sounds)",
            variable=self.silent_notifications_var,
            command=self.on_silent_notifications_changed
        )
        silent_notifications_check.grid(row=row, column=0, columnspan=2, sticky="w", pady=5)
        row += 1

        # Add help text for silent notifications
        silent_help_label = ctk.CTkLabel(
            parent,
            text="    Prevents system notification sounds from playing alongside GUI sounds",
            font=ctk.CTkFont(size=11),
            text_color=("gray30", "gray70")
        )
        silent_help_label.grid(row=row, column=0, columnspan=2, sticky="w", padx=(25, 0))
        row += 1

        # Duration control
        duration_label = ctk.CTkLabel(parent, text="Duration:")
        duration_label.grid(row=row, column=0, sticky="w", pady=5)

        duration_frame = ctk.CTkFrame(parent, fg_color="transparent")
        duration_frame.grid(row=row, column=1, sticky="ew", pady=5)

        self.duration_var = ctk.IntVar(value=self.get_state('notification_duration', 5))
        self.duration_label = ctk.CTkLabel(
            duration_frame,
            text=f"{self.duration_var.get()}s"
        )
        self.duration_label.grid(row=0, column=0, padx=(0, 10))

        duration_slider = ctk.CTkSlider(
            duration_frame,
            from_=1,
            to=15,
            number_of_steps=14,
            variable=self.duration_var,
            command=self.on_duration_changed
        )
        duration_slider.grid(row=0, column=1, sticky="ew")
        duration_frame.grid_columnconfigure(1, weight=1)
        row += 1

        # Test notification buttons
        test_notif_label = ctk.CTkLabel(parent, text="Test Notifications:")
        test_notif_label.grid(row=row, column=0, sticky="w", pady=5)

        test_notif_frame = ctk.CTkFrame(parent, fg_color="transparent")
        test_notif_frame.grid(row=row, column=1, sticky="ew", pady=5)

        # Get available notification types
        available_notifications = self.notification_manager.get_available_types()

        # Create test buttons for each notification type
        col = 0
        for notif_type, description in available_notifications.items():
            if notif_type in ['success', 'error', 'info']:  # Only show main notification types
                test_btn = ctk.CTkButton(
                    test_notif_frame,
                    text=f"🔔 {notif_type.title()}",
                    width=80,
                    height=28,
                    command=lambda nt=notif_type: self.test_notification(nt),
                    fg_color=("gray70", "gray30")
                )
                test_btn.grid(row=0, column=col, padx=(0, 5))
                col += 1

        row += 1

        # System notification types
        notif_types_label = ctk.CTkLabel(parent, text="Show notifications for:")
        notif_types_label.grid(row=row, column=0, sticky="w", pady=(15, 5))
        row += 1

        # Individual notification type toggles
        self.notification_type_vars = {}

        notification_types = [
            ('script_success', 'Script completes successfully'),
            ('script_error', 'Script fails or encounters an error'),
            ('script_start', 'Script execution begins'),
            ('script_warning', 'Script warnings or user stops')
        ]

        for notif_key, description in notification_types:
            self.notification_type_vars[notif_key] = ctk.BooleanVar(
                value=self.get_state(f'notification_{notif_key}', True)
            )

            notif_check = ctk.CTkCheckBox(
                parent,
                text=description,
                variable=self.notification_type_vars[notif_key]
            )
            notif_check.grid(row=row, column=0, columnspan=2, sticky="w", padx=(20, 0), pady=2)
            row += 1

        # Platform info
        platform_info_label = ctk.CTkLabel(
            parent,
            text=f"Using notification backend: {self.notification_manager.notification_backend}",
            font=ctk.CTkFont(size=11),
            text_color=("gray30", "gray70")
        )
        platform_info_label.grid(row=row, column=0, columnspan=2, sticky="w", pady=(10, 0))

    def on_silent_notifications_changed(self):
        """Handle silent notifications toggle"""
        silent = self.silent_notifications_var.get()
        self.set_state('silent_notifications', silent)
        self.notification_manager.set_silent(silent)

        if silent:
            self.show_message("System notification sounds disabled", "success")
        else:
            self.show_message("System notification sounds enabled", "info")

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

        # Developer mode
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

    def on_sounds_enabled_changed(self):
        """Handle sounds enabled toggle"""
        enabled = self.sounds_enabled_var.get()
        self.set_state('sounds_enabled', enabled)
        self.sound_manager.set_enabled(enabled)

        if enabled:
            self.show_message("Sound notifications enabled", "success")
        else:
            self.show_message("Sound notifications disabled", "info")

    def on_volume_changed(self, volume: float):
        """Handle volume change"""
        self.volume_label.configure(text=f"{int(volume * 100)}%")
        self.set_state('sound_volume', volume)
        self.sound_manager.set_volume(volume)

    def test_sound(self, sound_type: str):
        """Test a specific sound"""
        self.sound_manager.test_sound(sound_type)
        self.show_message(f"Playing {sound_type} sound...", "info")

    def on_notifications_enabled_changed(self):
        """Handle system notifications enabled toggle"""
        enabled = self.notifications_enabled_var.get()
        self.set_state('notifications_enabled', enabled)
        self.notification_manager.set_enabled(enabled)

        if enabled:
            self.show_message("System notifications enabled", "success")
            # Show a test notification
            self.notification_manager.show_notification(
                "Notifications Enabled",
                "System notifications are now active!",
                "info"
            )
        else:
            self.show_message("System notifications disabled", "info")

    def on_duration_changed(self, duration: float):
        """Handle notification duration change"""
        duration = int(duration)
        self.duration_label.configure(text=f"{duration}s")
        self.set_state('notification_duration', duration)
        self.notification_manager.set_duration(duration)

    def test_notification(self, notification_type: str):
        """Test a specific notification"""
        self.notification_manager.test_notification(notification_type)
        self.show_message(f"Showing {notification_type} notification...", "info")

    def save_settings(self):
        """Save current settings with correct key naming"""
        # Gather all settings
        settings = {
            'theme': self.theme_var.get(),
            'font_size': self.font_size_var.get(),
            'auto_scroll': self.auto_scroll_var.get(),
            'clear_on_run': self.clear_on_run_var.get(),
            'developer_mode': self.developer_mode_var.get(),
            # Sound settings
            'sounds_enabled': self.sounds_enabled_var.get(),
            'sound_volume': self.volume_var.get(),
            # Notification settings
            'notifications_enabled': self.notifications_enabled_var.get(),
            'notification_duration': self.duration_var.get(),
            'silent_notifications': self.silent_notifications_var.get(),  # NEW
        }

        # Add individual sound type settings with correct keys
        for sound_key, var in self.sound_type_vars.items():
            # Add the 'sound_' prefix to match what the integration expects
            settings[f'sound_{sound_key}'] = var.get()

        # Add individual notification type settings with correct keys
        for notif_key, var in self.notification_type_vars.items():
            # Add the 'notification_' prefix to match what the integration expects
            settings[f'notification_{notif_key}'] = var.get()

        # Update state
        self.state_manager.update(settings)

        # Apply sound settings to sound manager
        self.sound_manager.set_enabled(settings['sounds_enabled'])
        self.sound_manager.set_volume(settings['sound_volume'])

        # Apply notification settings to notification manager
        self.notification_manager.set_enabled(settings['notifications_enabled'])
        self.notification_manager.set_duration(settings['notification_duration'])

        # Save to file for persistence
        if self.state_manager.save_to_file():
            self.show_message("Settings saved successfully!", "success")
        else:
            self.show_message("Settings updated but failed to save to disk", "warning")

        self.publish_event('settings.saved', {'settings': settings})

    def reset_settings(self):
        """Reset settings to defaults"""
        # Reset to defaults
        self.theme_var.set('dark')
        self.font_size_var.set(12)
        self.auto_scroll_var.set(True)
        self.clear_on_run_var.set(False)
        self.developer_mode_var.set(False)

        # Reset sound settings
        self.sounds_enabled_var.set(True)
        self.volume_var.set(0.7)

        # Reset notification settings
        self.notifications_enabled_var.set(True)
        self.duration_var.set(5)

        for var in self.sound_type_vars.values():
            var.set(True)

        for var in self.notification_type_vars.values():
            var.set(True)

        # Update UI
        self.font_size_label.configure(text="12px")
        self.volume_label.configure(text="70%")
        self.duration_label.configure(text="5s")

        # Save the reset settings
        self.save_settings()
        self.show_message("Settings reset to defaults", "info")

    def on_activate(self):
        """Called when settings page becomes active"""
        super().on_activate()

        # Update UI to reflect current state
        self.theme_var.set(self.get_state('theme', 'dark'))
        self.font_size_var.set(self.get_state('font_size', 12))
        self.font_size_label.configure(text=f"{self.font_size_var.get()}px")
        self.developer_mode_var.set(self.get_state('developer_mode', False))

        # Update sound settings
        self.sounds_enabled_var.set(self.get_state('sounds_enabled', True))
        self.volume_var.set(self.get_state('sound_volume', 0.7))
        self.volume_label.configure(text=f"{int(self.volume_var.get() * 100)}%")

        # Update notification settings
        self.notifications_enabled_var.set(self.get_state('notifications_enabled', True))
        self.duration_var.set(self.get_state('notification_duration', 5))
        self.duration_label.configure(text=f"{self.duration_var.get()}s")

        # Update sound type settings with correct keys
        for sound_key, var in self.sound_type_vars.items():
            var.set(self.get_state(f'sound_{sound_key}', True))

        # Update notification type settings with correct keys
        for notif_key, var in self.notification_type_vars.items():
            var.set(self.get_state(f'notification_{notif_key}', True))
