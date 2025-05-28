"""SOPs page - Standard Operating Procedures for scripts"""

import customtkinter as ctk
from pages.base_page import BasePage
from typing import List, Dict, Any
import webbrowser
from config.sops_config import SOPS_DATA, SOP_CATEGORIES, DIFFICULTY_LEVELS


class SOPsPage(BasePage):
    """SOPs page for displaying Standard Operating Procedures for different scripts"""

    def __init__(self, parent, state_manager, event_bus, **kwargs):
        # Define SOPs data structure - Easy to extend by adding new entries
        self.sops_data = SOPS_DATA
        # self.sops_data = [
        #     {
        #         'id': 'data_processing',
        #         'title': 'lol',
        #         'description': 'Learn how to process CSV files, clean data, and generate reports',
        #         'category': 'Data Processing',
        #         'difficulty': 'Beginner',
        #         'duration': '15 min',
        #         'link': 'https://example.com/sop/data-processing',  # Replace with actual links
        #         'icon': '📊',
        #         'tags': ['CSV', 'Data', 'Reports']
        #     },
        #     {
        #         'id': 'web_scraping',
        #         'title': 'Web Scraping Guide',
        #         'description': 'Step-by-step guide for setting up and running web scraping scripts',
        #         'category': 'Web Automation',
        #         'difficulty': 'Intermediate',
        #         'duration': '30 min',
        #         'link': 'https://example.com/sop/web-scraping',
        #         'icon': '🌐',
        #         'tags': ['Web', 'Scraping', 'Automation']
        #     },
        #     {
        #         'id': 'backup_automation',
        #         'title': 'Backup Automation Setup',
        #         'description': 'Configure automated backups for your important files and databases',
        #         'category': 'System Administration',
        #         'difficulty': 'Intermediate',
        #         'duration': '20 min',
        #         'link': 'https://example.com/sop/backup-automation',
        #         'icon': '💾',
        #         'tags': ['Backup', 'Automation', 'System']
        #     },
        #     {
        #         'id': 'image_processing',
        #         'title': 'Image Processing Workflow',
        #         'description': 'Batch process images with resizing, optimization, and format conversion',
        #         'category': 'Media Processing',
        #         'difficulty': 'Beginner',
        #         'duration': '10 min',
        #         'link': 'https://example.com/sop/image-processing',
        #         'icon': '🖼️',
        #         'tags': ['Images', 'Media', 'Batch']
        #     },
        #     {
        #         'id': 'api_integration',
        #         'title': 'API Integration Guide',
        #         'description': 'Connect to external APIs and process responses effectively',
        #         'category': 'Integration',
        #         'difficulty': 'Advanced',
        #         'duration': '45 min',
        #         'link': 'https://example.com/sop/api-integration',
        #         'icon': '🔌',
        #         'tags': ['API', 'Integration', 'REST']
        #     },
        #     {
        #         'id': 'database_operations',
        #         'title': 'Database Operations',
        #         'description': 'Perform CRUD operations and manage database connections',
        #         'category': 'Database',
        #         'difficulty': 'Intermediate',
        #         'duration': '25 min',
        #         'link': 'https://example.com/sop/database-operations',
        #         'icon': '🗄️',
        #         'tags': ['Database', 'SQL', 'CRUD']
        #     }
        # ]

        # Initialize categories for filtering
        self.categories = list(set(sop['category'] for sop in self.sops_data))
        self.selected_category = "All"

        # Initialize search
        self.search_var = ctk.StringVar()
        self.search_var.trace('w', lambda *args: self.filter_sops())

        super().__init__(parent, state_manager, event_bus, **kwargs)

    def setup_ui(self):
        """Set up the SOPs page UI"""
        # Main container
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_rowconfigure(2, weight=1)

        # Header with title and description
        self.create_header(main_container)

        # Search and filter bar
        self.create_search_filter_bar(main_container)

        # SOPs grid container
        self.create_sops_container(main_container)

        # Display all SOPs initially
        self.display_sops(self.sops_data)

    def create_header(self, parent):
        """Create the page header"""
        header_frame = ctk.CTkFrame(parent, fg_color="transparent")
        header_frame.grid(row=0, column=0, pady=(0, 20), sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1)

        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text="Standard Operating Procedures",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.grid(row=0, column=0, sticky="w")

        # Description
        desc_label = ctk.CTkLabel(
            header_frame,
            text="Browse guides and tutorials for running different scripts effectively",
            font=ctk.CTkFont(size=14),
            text_color=("gray40", "gray60")
        )
        desc_label.grid(row=1, column=0, sticky="w", pady=(5, 0))

        # Quick stats
        stats_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        stats_frame.grid(row=0, column=1, rowspan=2, sticky="e")

        total_label = ctk.CTkLabel(
            stats_frame,
            text=f"{len(self.sops_data)} SOPs Available",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("#1f6aa5", "#1f6aa5")
        )
        total_label.grid(row=0, column=0, padx=10)

    def create_search_filter_bar(self, parent):
        """Create search and filter controls"""
        control_frame = ctk.CTkFrame(parent)
        control_frame.grid(row=1, column=0, pady=(0, 20), sticky="ew")
        control_frame.grid_columnconfigure(1, weight=1)

        # Category filter
        filter_label = ctk.CTkLabel(
            control_frame,
            text="Category:",
            font=ctk.CTkFont(size=14)
        )
        filter_label.grid(row=0, column=0, padx=(20, 10), pady=15)

        self.category_menu = ctk.CTkOptionMenu(
            control_frame,
            values=["All"] + sorted(self.categories),
            command=self.on_category_changed,
            width=150
        )
        self.category_menu.grid(row=0, column=1, padx=(0, 20), pady=15, sticky="w")

        # Search bar
        search_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        search_frame.grid(row=0, column=2, padx=(0, 20), pady=15, sticky="e")

        search_label = ctk.CTkLabel(
            search_frame,
            text="🔍",
            font=ctk.CTkFont(size=16)
        )
        search_label.grid(row=0, column=0, padx=(0, 5))

        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search SOPs...",
            textvariable=self.search_var,
            width=200
        )
        self.search_entry.grid(row=0, column=1)

    def create_sops_container(self, parent):
        """Create the scrollable container for SOP cards"""
        # Container frame
        container_frame = ctk.CTkFrame(parent)
        container_frame.grid(row=2, column=0, sticky="nsew")
        container_frame.grid_columnconfigure(0, weight=1)
        container_frame.grid_rowconfigure(0, weight=1)

        # Scrollable frame
        self.scrollable_frame = ctk.CTkScrollableFrame(container_frame)
        self.scrollable_frame.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)

        # Configure grid for responsive layout
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        self.scrollable_frame.grid_columnconfigure(1, weight=1)

    def display_sops(self, sops_list):
        """Display SOP cards in a grid layout"""
        # Clear existing widgets
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        if not sops_list:
            # Show empty state
            self.show_empty_state()
            return

        # Create SOP cards in a 2-column grid
        for i, sop in enumerate(sops_list):
            row = i // 2
            col = i % 2
            self.create_sop_card(sop, row, col)

    def create_sop_card(self, sop: Dict[str, Any], row: int, col: int):
        """Create a card for an SOP"""
        # Card frame
        card = ctk.CTkFrame(
            self.scrollable_frame,
            corner_radius=10,
            border_width=2,
            border_color=("gray70", "gray30")
        )
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        # self.scrollable_frame.grid_rowconfigure(row, weight=1) # Keep row weight if you want all cards in a row to have same height

        # Card content
        content_frame = ctk.CTkFrame(card, fg_color="transparent")
        content_frame.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")  # Reduced padx/pady a bit
        content_frame.grid_columnconfigure(0, weight=1)  # Allow content to fill width

        # Icon and title
        title_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        title_frame.grid(row=0, column=0, sticky="ew")
        # title_frame.grid_columnconfigure(0, weight=0) # Icon column
        title_frame.grid_columnconfigure(1, weight=1)  # Title label column (allow to expand)

        icon_label = ctk.CTkLabel(
            title_frame,
            text=sop.get('icon', '📄'),
            font=ctk.CTkFont(size=24)
        )
        icon_label.grid(row=0, column=0, padx=(0, 10), sticky="ns")

        title_label = ctk.CTkLabel(
            title_frame,
            text=sop.get('title', 'No Title'),
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w",
            justify="left",  # Ensure text is left-justified when wrapped
            wraplength=220  # *** ADDED: Adjust this based on your card width / icon size / padding ***
        )
        title_label.grid(row=0, column=1, sticky="ew")

        # Category, difficulty, and duration badges
        badge_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        badge_frame.grid(row=1, column=0, pady=(8, 0),
                         sticky="ew")  # Use sticky="ew" to allow internal elements to align
        # We'll let the badges flow using grid columns within badge_frame

        current_badge_column = 0
        badge_wraplength = 70  # *** ADDED: wraplength for individual badges ***

        if sop.get('category'):
            category_badge = ctk.CTkLabel(
                badge_frame,
                text=sop['category'],
                font=ctk.CTkFont(size=11),
                fg_color=("#e0e0e0", "#374151"),
                corner_radius=12,
                padx=8,
                pady=2,
                wraplength=badge_wraplength,  # *** ADDED ***
                justify="center"
            )
            category_badge.grid(row=0, column=current_badge_column, padx=(0, 5), pady=(0, 2), sticky="w")
            current_badge_column += 1

        if sop.get('difficulty'):
            diff_colors = {
                'Beginner': ("#4CAF50", "#2d5a2f"),
                'Intermediate': ("#FF9800", "#b36a00"),
                'Advanced': ("#f44336", "#961f17")
            }
            difficulty_badge = ctk.CTkLabel(
                badge_frame,
                text=sop['difficulty'],
                font=ctk.CTkFont(size=11),
                fg_color=diff_colors.get(sop['difficulty'], ("#757575", "#424242")),
                text_color="white",
                corner_radius=12,
                padx=8,
                pady=2,
                wraplength=badge_wraplength,  # *** ADDED ***
                justify="center"
            )
            difficulty_badge.grid(row=0, column=current_badge_column, padx=5 if current_badge_column > 0 else (0, 5),
                                  pady=(0, 2), sticky="w")
            current_badge_column += 1

        if sop.get('duration'):
            duration_label = ctk.CTkLabel(
                badge_frame,
                text=f"⏱️ {sop['duration']}",
                font=ctk.CTkFont(size=11),
                text_color=("gray40", "gray60"),
                wraplength=badge_wraplength + 20,  # Duration might be slightly longer with icon
                justify="center"
            )
            duration_label.grid(row=0, column=current_badge_column, padx=5 if current_badge_column > 0 else (0, 5),
                                pady=(0, 2), sticky="w")

        # Description
        desc_label = ctk.CTkLabel(
            content_frame,
            text=sop.get('description', ''),
            font=ctk.CTkFont(size=12),
            text_color=("gray30", "gray70"),
            anchor="w",
            justify="left",
            wraplength=250  # This was already there, ensure it's appropriate
        )
        desc_label.grid(row=2, column=0, pady=(8, 0), sticky="ew")

        # Tags
        if sop.get('tags'):
            tags_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
            tags_frame.grid(row=3, column=0, pady=(8, 0), sticky="ew")  # Use sticky="ew"
            # Add column configure for tags frame to allow wrapping if you have many tags
            # For now, limiting to 3 tags should prevent overflow issues mostly

            for i, tag_text in enumerate(sop['tags'][:3]):
                tag_label = ctk.CTkLabel(
                    tags_frame,
                    text=f"#{tag_text}",
                    font=ctk.CTkFont(size=10),
                    text_color=("#1f6aa5", "#4d94ff"),
                    wraplength=70,  # *** ADDED: Optional wraplength for individual tags ***
                    justify="left"
                )
                tag_label.grid(row=0, column=i, padx=(0, 8), sticky="w")

        # Action buttons
        button_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        button_frame.grid(row=4, column=0, pady=(15, 0), sticky="ew")
        button_frame.grid_columnconfigure(0, weight=1)  # Allow button to fill width

        view_btn = ctk.CTkButton(
            button_frame,
            text="View SOP",
            command=lambda s=sop: self.open_sop(s),
            height=32,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        view_btn.grid(row=0, column=0, sticky="ew", padx=(0, 5))

        # Make card interactive
        card.bind("<Enter>", lambda e, c=card: c.configure(border_color=("#1f6aa5", "#1f6aa5")))
        card.bind("<Leave>", lambda e, c=card: c.configure(border_color=("gray70", "gray30")))

    def show_empty_state(self):
        """Show empty state when no SOPs match the filter"""
        empty_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        empty_frame.grid(row=0, column=0, columnspan=2, padx=50, pady=50)

        empty_label = ctk.CTkLabel(
            empty_frame,
            text="No SOPs found",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=("gray40", "gray60")
        )
        empty_label.grid(row=0, column=0, pady=(0, 10))

        help_label = ctk.CTkLabel(
            empty_frame,
            text="Try adjusting your search or filter criteria",
            font=ctk.CTkFont(size=14),
            text_color=("gray30", "gray70")
        )
        help_label.grid(row=1, column=0)

    def filter_sops(self):
        """Filter SOPs based on search and category"""
        search_term = self.search_var.get().lower()
        filtered_sops = []

        for sop in self.sops_data:
            # Category filter
            if self.selected_category != "All" and sop['category'] != self.selected_category:
                continue

            # Search filter
            if search_term:
                searchable_text = f"{sop['title']} {sop['description']} {' '.join(sop['tags'])}".lower()
                if search_term not in searchable_text:
                    continue

            filtered_sops.append(sop)

        self.display_sops(filtered_sops)

    def on_category_changed(self, category):
        """Handle category filter change"""
        self.selected_category = category
        self.filter_sops()

    def open_sop(self, sop: Dict[str, Any]):
        """Open the SOP link in the default browser"""
        try:
            webbrowser.open(sop['link'])
            self.publish_event('sop.opened', {
                'sop_id': sop['id'],
                'title': sop['title']
            })
            self.show_message(f"Opening {sop['title']} in your browser...", "info")
        except Exception as e:
            self.show_message(f"Failed to open SOP: {str(e)}", "error")

    def add_sop(self, sop_data: Dict[str, Any]):
        """Add a new SOP to the list - for easy extensibility"""
        self.sops_data.append(sop_data)
        self.categories = list(set(sop['category'] for sop in self.sops_data))
        self.category_menu.configure(values=["All"] + sorted(self.categories))
        self.filter_sops()

    def remove_sop(self, sop_id: str):
        """Remove an SOP from the list"""
        # self.sops_data = [sop for sop in self.sops_data if sop['id'] != sop_id]
        self.sops_data = SOPS_DATA  # This line is for selecting the data from hte SOP Config file. Use the line above if you want to use the values on this file.
        self.filter_sops()

    def on_activate(self):
        """Called when the SOPs page becomes active"""
        super().on_activate()

        # Check if we need to highlight a specific SOP
        highlight_sop_id = self.get_state('highlight_sop_id')
        if highlight_sop_id:
            # Clear the state
            self.set_state('highlight_sop_id', None)

            # Find and scroll to the SOP
            self.highlight_sop(highlight_sop_id)

    def highlight_sop(self, sop_id: str):
        """Highlight and scroll to a specific SOP"""
        # Clear any existing filters
        self.search_var.set("")
        self.selected_category = "All"
        self.category_menu.set("All")

        # Redisplay all SOPs
        self.display_sops(self.sops_data)

        # Find the SOP card and highlight it
        # This would require storing card references during creation
        # For now, just show a message
        for sop in self.sops_data:
            if sop['id'] == sop_id:
                self.show_message(f"Highlighted: {sop['title']}", "info")
                break

    def setup_event_subscriptions(self):
        """Set up event subscriptions"""
        # Listen for SOP-related events
        self.event_bus.subscribe('sop.added', lambda data: self.add_sop(data))
        self.event_bus.subscribe('sop.removed', lambda data: self.remove_sop(data['id']))
