"""Projects page - manage and organize scripts (OPTIMIZED VERSION)"""

import customtkinter as ctk
from pages.base_page import BasePage
from typing import List, Dict, Any, Optional
from utils.script_history import get_history_manager
from utils.event_bus import Events

# Import script configuration to match names
try:
    from config.scripts_config import AVAILABLE_SCRIPTS, TAG_COLORS
except ImportError:
    AVAILABLE_SCRIPTS = {}
    TAG_COLORS = {"default": "#757575"}


class ProjectsPage(BasePage):
    """Projects page for managing scripts and projects"""

    def __init__(self, parent, state_manager, event_bus, **kwargs):
        # Initialize history manager
        self.history_manager = get_history_manager()

        # Initialize search/filter state
        self.search_var = ctk.StringVar()
        self.search_var.trace('w', lambda *args: self.filter_projects())
        self.selected_category = "All"

        # Build categories list from available scripts
        self.categories = ["All"]
        for script_info in AVAILABLE_SCRIPTS.values():
            category = script_info.get('category', 'Uncategorized')
            if category not in self.categories:
                self.categories.append(category)

        # Cache for project data and widgets
        self.all_projects = []
        self.project_cards = {}  # Cache card widgets
        self.dynamic_widgets = {}  # Cache dynamic widgets (status, last run)
        self.projects_initialized = False

        # For deferred loading
        self.pending_cards = []
        self.card_creation_after_id = None

        super().__init__(parent, state_manager, event_bus, **kwargs)

    def setup_ui(self):
        """Set up the Projects page UI"""
        # Main container
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_rowconfigure(2, weight=1)

        # Header
        header_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        header_frame.grid(row=0, column=0, pady=(0, 15), sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1)

        title_label = ctk.CTkLabel(
            header_frame,
            text="Script Projects",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.grid(row=0, column=0, sticky="w")

        # Search and filter bar
        self.create_search_filter_bar(main_container)

        # Projects list container
        list_container = ctk.CTkFrame(main_container)
        list_container.grid(row=2, column=0, sticky="nsew")
        list_container.grid_columnconfigure(0, weight=1)
        list_container.grid_rowconfigure(0, weight=1)

        # Scrollable frame for projects
        self.scrollable_frame = ctk.CTkScrollableFrame(list_container)
        self.scrollable_frame.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

        # Initialize projects data (but don't create widgets yet)
        self.initialize_projects_data()

    def create_search_filter_bar(self, parent):
        """Create search and filter controls"""
        control_frame = ctk.CTkFrame(parent)
        control_frame.grid(row=1, column=0, pady=(0, 15), sticky="ew")
        control_frame.grid_columnconfigure(2, weight=1)

        # Category filter
        filter_label = ctk.CTkLabel(
            control_frame,
            text="Category:",
            font=ctk.CTkFont(size=14)
        )
        filter_label.grid(row=0, column=0, padx=(20, 10), pady=10)

        self.category_menu = ctk.CTkOptionMenu(
            control_frame,
            values=self.categories,
            command=self.on_category_changed,
            width=150
        )
        self.category_menu.grid(row=0, column=1, padx=(0, 20), pady=10, sticky="w")

        # Search bar
        search_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        search_frame.grid(row=0, column=2, padx=(0, 20), pady=10, sticky="ew")
        search_frame.grid_columnconfigure(1, weight=1)

        search_label = ctk.CTkLabel(
            search_frame,
            text="🔍",
            font=ctk.CTkFont(size=16)
        )
        search_label.grid(row=0, column=0, padx=(0, 5))

        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search scripts by name or tag...",
            textvariable=self.search_var,
            width=300
        )
        self.search_entry.grid(row=0, column=1, sticky="ew")

        # Results count label
        self.results_label = ctk.CTkLabel(
            control_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color=("gray40", "gray60")
        )
        self.results_label.grid(row=0, column=3, padx=(10, 20), pady=10)

    def initialize_projects_data(self):
        """Initialize project data without creating widgets"""
        if self.projects_initialized:
            return

        # Build projects list from available scripts configuration
        self.all_projects = []

        for script_name, script_info in AVAILABLE_SCRIPTS.items():
            # Build project entry (without dynamic data initially)
            project = {
                'name': script_name,
                'description': script_info.get('description', 'No description available'),
                'path': script_info.get('path', ''),
                'category': script_info.get('category', 'Uncategorized'),
                'tags': script_info.get('tags', []),
                'last_run': 'Loading...',
                'status': 'loading',
                'sop_id': script_info.get('sop_id')
            }

            self.all_projects.append(project)

        self.projects_initialized = True

    def update_dynamic_data(self):
        """Update only the dynamic data (last run, status) for all projects"""
        for project in self.all_projects:
            # Get history info for this script
            last_run_time, last_status = self.history_manager.get_last_run_info(project['name'])

            project['last_run'] = last_run_time or 'Never'
            project['status'] = last_status or 'idle'

            # Update the UI if card exists
            if project['name'] in self.dynamic_widgets:
                widgets = self.dynamic_widgets[project['name']]
                if 'status_label' in widgets:
                    self.update_status_label(widgets['status_label'], project['status'])
                if 'last_run_label' in widgets:
                    widgets['last_run_label'].configure(text=f"Last run: {project['last_run']}")

    def update_status_label(self, label, status):
        """Update a status label with appropriate color and text"""
        status_colors = {
            'success': "#4CAF50",
            'error': "#f44336",
            'stopped': "#FF9800",
            'idle': "#757575",
            'unknown': "#9E9E9E",
            'loading': "#2196F3"
        }

        status_text = {
            'success': "Success",
            'error': "Failed",
            'stopped': "Stopped",
            'idle': "Not Run",
            'unknown': "Unknown",
            'loading': "Loading..."
        }

        label.configure(
            text=f"● {status_text.get(status, status.title())}",
            text_color=status_colors.get(status, "#757575")
        )

    def filter_projects(self):
        """Filter projects based on search and category"""
        search_term = self.search_var.get().lower()
        filtered_projects = []

        for project in self.all_projects:
            # Category filter
            if self.selected_category != "All" and project['category'] != self.selected_category:
                continue

            # Search filter
            if search_term:
                # Search in name, description, and tags
                searchable_text = f"{project['name']} {project['description']} {' '.join(project['tags'])}".lower()
                if search_term not in searchable_text:
                    continue

            filtered_projects.append(project)

        # Update results count
        total = len(self.all_projects)
        filtered = len(filtered_projects)
        if search_term or self.selected_category != "All":
            self.results_label.configure(text=f"Showing {filtered} of {total} scripts")
        else:
            self.results_label.configure(text=f"{total} scripts")

        # Display the filtered projects
        self.display_projects(filtered_projects)

    def on_category_changed(self, category):
        """Handle category filter change"""
        self.selected_category = category
        self.filter_projects()

    def display_projects(self, projects):
        """Display the list of projects using cached widgets where possible"""
        # Hide all existing cards first
        for widget in self.scrollable_frame.winfo_children():
            widget.grid_forget()

        # Cancel any pending card creation
        if self.card_creation_after_id:
            self.after_cancel(self.card_creation_after_id)
            self.card_creation_after_id = None

        # Prepare list of cards to create/show
        self.pending_cards = []

        # Create/show project cards
        for i, project in enumerate(projects):
            if project['name'] in self.project_cards:
                # Card already exists, just show it
                card = self.project_cards[project['name']]
                card.grid(row=i, column=0, padx=10, pady=5, sticky="ew")
                # Update dynamic data is already handled by update_dynamic_data()
            else:
                # Need to create new card - add to pending list
                self.pending_cards.append((project, i))

        # Start deferred card creation if there are pending cards
        if self.pending_cards:
            self.create_next_card()

        # Show empty state if no projects
        if not projects:
            self.show_empty_state()

    def create_next_card(self):
        """Create the next pending card (deferred loading)"""
        if not self.pending_cards:
            return

        # Create one card
        project, index = self.pending_cards.pop(0)
        self.create_project_card(project, index)

        # Schedule next card creation
        if self.pending_cards:
            self.card_creation_after_id = self.after(10, self.create_next_card)

    def create_project_card(self, project: Dict[str, Any], index: int):
        """Create a card for a project with tags (OPTIMIZED: removed path, cache widgets)"""
        # Card frame
        card = ctk.CTkFrame(self.scrollable_frame)
        card.grid(row=index, column=0, padx=10, pady=5, sticky="ew")
        card.grid_columnconfigure(0, weight=1)

        # Cache the card
        self.project_cards[project['name']] = card
        self.dynamic_widgets[project['name']] = {}

        # Content frame
        content_frame = ctk.CTkFrame(card, fg_color="transparent")
        content_frame.grid(row=0, column=0, padx=15, pady=15, sticky="ew")
        content_frame.grid_columnconfigure(0, weight=1)

        # Project name and category
        header_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew")
        header_frame.grid_columnconfigure(0, weight=0)
        header_frame.grid_columnconfigure(1, weight=1)
        header_frame.grid_columnconfigure(2, weight=0)

        name_label = ctk.CTkLabel(
            header_frame,
            text=project['name'],
            font=ctk.CTkFont(size=16, weight="bold")
        )
        name_label.grid(row=0, column=0, sticky="w")

        # Category badge
        category_label = ctk.CTkLabel(
            header_frame,
            text=project['category'],
            font=ctk.CTkFont(size=11),
            fg_color=("#e0e0e0", "#374151"),
            corner_radius=12,
            padx=10,
            pady=2
        )
        category_label.grid(row=0, column=1, sticky="w", padx=(10, 0))

        # Status indicator (dynamic - cache this widget)
        status_label = ctk.CTkLabel(
            header_frame,
            text="",
            font=ctk.CTkFont(size=12)
        )
        status_label.grid(row=0, column=2, sticky="e", padx=(10, 0))
        self.dynamic_widgets[project['name']]['status_label'] = status_label
        self.update_status_label(status_label, project['status'])

        # Description
        desc_label = ctk.CTkLabel(
            content_frame,
            text=project['description'],
            font=ctk.CTkFont(size=12),
            text_color=("gray40", "gray60"),
            anchor="w"
        )
        desc_label.grid(row=1, column=0, sticky="w", pady=(5, 0))

        # Tags
        if project.get('tags'):
            tags_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
            tags_frame.grid(row=2, column=0, sticky="w", pady=(8, 0))

            for i, tag in enumerate(project['tags']):
                # Get color for tag
                tag_color = TAG_COLORS.get(tag, TAG_COLORS.get("default", "#757575"))

                tag_label = ctk.CTkLabel(
                    tags_frame,
                    text=f"#{tag}",
                    font=ctk.CTkFont(size=11),
                    fg_color=tag_color,
                    text_color="white",
                    corner_radius=10,
                    padx=8,
                    pady=2
                )
                tag_label.grid(row=0, column=i, padx=(0, 5), sticky="w")

        # Last run info only (removed path)
        info_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        info_frame.grid(row=3, column=0, sticky="ew", pady=(8, 0))
        info_frame.grid_columnconfigure(0, weight=1)

        last_run_label = ctk.CTkLabel(
            info_frame,
            text=f"Last run: {project['last_run']}",
            font=ctk.CTkFont(size=11),
            text_color=("gray30", "gray70")
        )
        last_run_label.grid(row=0, column=0, sticky="e")
        self.dynamic_widgets[project['name']]['last_run_label'] = last_run_label

        # Action buttons
        button_frame = ctk.CTkFrame(card, fg_color="transparent")
        button_frame.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="ew")

        run_btn = ctk.CTkButton(
            button_frame,
            text="Run",
            width=80,
            height=28,
            command=lambda p=project: self.run_project(p)
        )
        run_btn.grid(row=0, column=0, padx=(0, 5))

        next_button_column = 1

        # Add SOP button if project has an associated SOP
        if project.get('sop_id'):
            sop_btn = ctk.CTkButton(
                button_frame,
                text="SOP",
                width=80,
                height=28,
                fg_color=("#1f6aa5", "#1f6aa5"),
                hover_color=("#144870", "#144870"),
                command=lambda p=project: self.open_project_sop(p)
            )
            sop_btn.grid(row=0, column=next_button_column, padx=5)
            next_button_column += 1

        # Stats button to show detailed history
        stats_btn = ctk.CTkButton(
            button_frame,
            text="Stats",
            width=80,
            height=28,
            fg_color=("gray70", "gray30"),
            command=lambda p=project: self.show_project_stats(p)
        )
        stats_btn.grid(row=0, column=next_button_column, padx=5)
        next_button_column += 1

        # Clear history button
        clear_btn = ctk.CTkButton(
            button_frame,
            text="Clear History",
            width=100,
            height=28,
            fg_color=("gray70", "gray30"),
            hover_color=("gray60", "gray40"),
            command=lambda p=project: self.clear_project_history(p)
        )
        clear_btn.grid(row=0, column=next_button_column, padx=(5, 0))

    def show_empty_state(self):
        """Show empty state when no projects match the filter"""
        empty_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        empty_frame.grid(row=0, column=0, padx=50, pady=50)

        if self.search_var.get() or self.selected_category != "All":
            # No results from search/filter
            empty_label = ctk.CTkLabel(
                empty_frame,
                text="No scripts found",
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
        else:
            # No scripts at all
            empty_label = ctk.CTkLabel(
                empty_frame,
                text="No scripts configured",
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color=("gray40", "gray60")
            )
            empty_label.grid(row=0, column=0, pady=(0, 10))

            help_label = ctk.CTkLabel(
                empty_frame,
                text="Scripts can be configured in config/scripts_config.py",
                font=ctk.CTkFont(size=14),
                text_color=("gray30", "gray70")
            )
            help_label.grid(row=1, column=0)

    def refresh_projects(self):
        """Refresh only the dynamic data, not the entire UI"""
        # Update dynamic data
        self.update_dynamic_data()

        # If we haven't displayed projects yet, do it now
        if not self.project_cards:
            self.filter_projects()

    def run_project(self, project: Dict[str, Any]):
        """Run a project"""
        # Switch to Console page and set the script
        self.set_state('current_page', 'Console')
        self.set_state('script_to_run', project['name'])
        self.publish_event('project.run', {'project': project})

        # Navigate to Console page
        main_app = self.winfo_toplevel()
        if hasattr(main_app, 'switch_page'):
            main_app.switch_page('Console')

            # Set the selected script in the dropdown
            console_page = main_app.pages.get('Console')
            if console_page and hasattr(console_page, 'script_type_var'):
                console_page.script_type_var.set(project['name'])
                # Trigger the run
                console_page.run_script()

    def show_project_stats(self, project: Dict[str, Any]):
        """Show detailed statistics for a project"""
        stats = self.history_manager.get_script_stats(project['name'])

        if stats['total_runs'] == 0:
            self.show_message(f"No execution history for '{project['name']}'", "info")
            return

        # Import and open the detailed history dialog
        from components.script_history_dialog import ScriptHistoryDialog

        try:
            dialog = ScriptHistoryDialog(
                parent=self,
                script_name=project['name'],
                history_manager=self.history_manager
            )

            # Wait for dialog to close (it's modal)
            self.wait_window(dialog)

        except Exception as e:
            # Fallback to simple message if dialog fails
            self.show_message(f"Error opening history dialog: {str(e)}", "error")

            # Show basic stats as fallback
            message = f"Statistics for '{project['name']}':\n\n"
            message += f"Total runs: {stats['total_runs']}\n"
            message += f"Success rate: {stats['success_rate']:.1f}%\n"
            message += f"Average duration: {stats['avg_duration']:.1f} seconds\n"

            if stats['last_success']:
                message += f"\nLast successful run: {stats['last_success']}"
            if stats['last_failure']:
                message += f"\nLast failed run: {stats['last_failure']}"

            self.show_message(message, "info")

    def clear_project_history(self, project: Dict[str, Any]):
        """Clear history for a specific project"""
        # In a real app, you'd show a confirmation dialog
        success = self.history_manager.clear_history(project['name'])

        if success:
            self.show_message(f"History cleared for '{project['name']}'", "success")
            # Update only the dynamic data for this project
            self.update_dynamic_data()
        else:
            self.show_message(f"Failed to clear history for '{project['name']}'", "error")

    def open_project_sop(self, project: Dict[str, Any]):
        """Navigate to the SOPs page and highlight the relevant SOP"""
        if project.get('sop_id'):
            # Set state to pass the SOP ID
            self.set_state('highlight_sop_id', project['sop_id'])

            # Switch to SOPs page
            self.set_state('current_page', 'SOPs')

            # Publish event
            self.publish_event('project.sop_requested', {
                'project': project['name'],
                'sop_id': project['sop_id']
            })

            self.show_message(f"Opening SOP for {project['name']}", "info")

    def on_activate(self):
        """Called when the Projects page becomes active"""
        super().on_activate()
        # Only refresh dynamic data, don't rebuild everything
        self.refresh_projects()

    def setup_event_subscriptions(self):
        """Set up event subscriptions"""
        # Listen for project-related events
        self.event_bus.subscribe('project.created', lambda data: self.refresh_projects())
        self.event_bus.subscribe('project.updated', lambda data: self.refresh_projects())
        self.event_bus.subscribe('project.deleted', lambda data: self.refresh_projects())
        # Listen for script completion to refresh history
        self.event_bus.subscribe(Events.SCRIPT_COMPLETED, lambda data: self.refresh_projects())
        self.event_bus.subscribe(Events.SCRIPT_ERROR, lambda data: self.refresh_projects())
        self.event_bus.subscribe(Events.SCRIPT_STOPPED, lambda data: self.refresh_projects())

    def cleanup(self):
        """Clean up resources when page is destroyed"""
        # Cancel any pending card creation
        if self.card_creation_after_id:
            self.after_cancel(self.card_creation_after_id)
        super().cleanup()
