"""About page - displays information about the application"""

import customtkinter as ctk
from pages.base_page import BasePage
from config.settings import WINDOW_TITLE


class AboutPage(BasePage):
    """About page showing application information"""
    
    def setup_ui(self):
        """Set up the About page UI"""
        # Create main container
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.grid(row=0, column=0, padx=40, pady=40, sticky="nsew")
        main_container.grid_columnconfigure(0, weight=1)
        
        # Application title
        title_label = ctk.CTkLabel(
            main_container,
            text="Script Runner",
            font=ctk.CTkFont(size=32, weight="bold")
        )
        title_label.grid(row=0, column=0, pady=(0, 10))
        
        # Version info
        version_label = ctk.CTkLabel(
            main_container,
            text="Version 1.0.0",
            font=ctk.CTkFont(size=16),
            text_color=("gray40", "gray60")
        )
        version_label.grid(row=1, column=0, pady=(0, 30))
        
        # Description section
        desc_section = self.create_section("About This Application", main_container)
        desc_section.grid(row=2, column=0, pady=(0, 20), sticky="ew")
        
        description_text = """Script Runner is a modern, user-friendly application for executing and managing Python scripts.
        
Features:
• Clean, modern UI with dark/light theme support
• Real-time script output display with color coding
• Script execution control (Run, Stop, Clear)
• Output export functionality
• Customizable font sizes
• Multi-page navigation system"""
        
        desc_label = self.create_info_label(
            desc_section.content_frame,
            description_text,
            wraplength=500
        )
        desc_label.grid(row=0, column=0, padx=20, sticky="w")
        
        # Architecture section
        arch_section = self.create_section("Architecture Highlights", main_container)
        arch_section.grid(row=3, column=0, pady=(0, 20), sticky="ew")
        
        architecture_text = """This application demonstrates modern software architecture principles:
        
• Component-based UI design with reusable widgets
• Event-driven communication using Event Bus pattern
• Centralized state management with observer pattern
• Service layer for business logic separation
• Modular page system for scalable navigation
• Clean separation of concerns"""
        
        arch_label = self.create_info_label(
            arch_section.content_frame,
            architecture_text,
            wraplength=500
        )
        arch_label.grid(row=0, column=0, padx=20, sticky="w")
        
        # Footer with links (placeholder for now)
        footer_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        footer_frame.grid(row=4, column=0, pady=(30, 0))
        
        # GitHub button (placeholder)
        github_btn = ctk.CTkButton(
            footer_frame,
            text="View on GitHub",
            width=150,
            command=lambda: self.show_message("GitHub link would open here", "info")
        )
        github_btn.grid(row=0, column=0, padx=5)
        
        # Documentation button (placeholder)
        docs_btn = ctk.CTkButton(
            footer_frame,
            text="Documentation",
            width=150,
            command=lambda: self.show_message("Documentation would open here", "info")
        )
        docs_btn.grid(row=0, column=1, padx=5)
        
    def on_activate(self):
        """Called when the About page becomes active"""
        super().on_activate()
        # Could refresh version info or check for updates here
        
    def on_deactivate(self):
        """Called when the About page becomes inactive"""
        super().on_deactivate()
        # Nothing specific to clean up for this page
