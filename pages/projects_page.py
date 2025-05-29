"""Projects page - manage and organize scripts"""

import customtkinter as ctk
from pages.base_page import BasePage
from typing import List, Dict, Any
from utils.script_history import get_history_manager  # Add this import
from utils.event_bus import Events  # Add this import

# Import script configuration to match names
try:
    from config.scripts_config import AVAILABLE_SCRIPTS
except ImportError:
    AVAILABLE_SCRIPTS = {}


class ProjectsPage(BasePage):
    """Projects page for managing scripts and projects"""

    def __init__(self, parent, state_manager, event_bus, **kwargs):
        # Initialize history manager
        self.history_manager = get_history_manager()

        super().__init__(parent, state_manager, event_bus, **kwargs)

    def setup_ui(self):
        """Set up the Projects page UI"""
        # Main container
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_rowconfigure(1, weight=1)

        # Header
        header_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        header_frame.grid(row=0, column=0, pady=(0, 20), sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1)

        title_label = ctk.CTkLabel(
            header_frame,
            text="Script Projects",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.grid(row=0, column=0, sticky="w")

        # Add new project button
        add_btn = ctk.CTkButton(
            header_frame,
            text="+ New Project",
            width=120,
            command=self.add_new_project
        )
        add_btn.grid(row=0, column=1, sticky="e")

        # Projects list container
        list_container = ctk.CTkFrame(main_container)
        list_container.grid(row=1, column=0, sticky="nsew")
        list_container.grid_columnconfigure(0, weight=1)
        list_container.grid_rowconfigure(0, weight=1)

        # Scrollable frame for projects
        self.scrollable_frame = ctk.CTkScrollableFrame(list_container)
        self.scrollable_frame.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

        # Load and display projects
        self.refresh_projects()

    def refresh_projects(self):
        """Refresh the projects list with current history data"""
        # Build projects list from available scripts configuration
        self.projects = []

        for script_name, script_info in AVAILABLE_SCRIPTS.items():
            # Get history info for this script
            last_run_time, last_status = self.history_manager.get_last_run_info(script_name)

            # Build project entry
            project = {
                'name': script_name,
                'description': script_info.get('description', 'No description available'),
                'path': script_info.get('path', ''),
                'last_run': last_run_time or 'Never',
                'status': last_status or 'idle',
                'sop_id': script_info.get('sop_id')  # Keep SOP functionality
            }

            self.projects.append(project)

        # Display the projects
        self.display_projects()

    def display_projects(self):
        """Display the list of projects"""
        # Clear existing widgets
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # Create project cards
        for i, project in enumerate(self.projects):
            self.create_project_card(project, i)

        # Info panel (shown when no projects)
        if not self.projects:
            self.show_empty_state()

    def create_project_card(self, project: Dict[str, Any], index: int):
        """Create a card for a project"""
        # Card frame
        card = ctk.CTkFrame(self.scrollable_frame)
        card.grid(row=index, column=0, padx=10, pady=5, sticky="ew")
        card.grid_columnconfigure(0, weight=1)

        # Content frame
        content_frame = ctk.CTkFrame(card, fg_color="transparent")
        content_frame.grid(row=0, column=0, padx=15, pady=15, sticky="ew")
        content_frame.grid_columnconfigure(0, weight=1)

        # Project name
        name_label = ctk.CTkLabel(
            content_frame,
            text=project['name'],
            font=ctk.CTkFont(size=16, weight="bold")
        )
        name_label.grid(row=0, column=0, sticky="w")

        # Status indicator
        status_colors = {
            'success': "#4CAF50",
            'error': "#f44336",
            'stopped': "#FF9800",
            'idle': "#757575",
            'unknown': "#9E9E9E"
        }

        status_text = {
            'success': "Success",
            'error': "Failed",
            'stopped': "Stopped",
            'idle': "Not Run",
            'unknown': "Unknown"
        }

        status = project.get('status', 'idle')
        status_label = ctk.CTkLabel(
            content_frame,
            text=f"● {status_text.get(status, status.title())}",
            text_color=status_colors.get(status, "#757575"),
            font=ctk.CTkFont(size=12)
        )
        status_label.grid(row=0, column=1, sticky="e", padx=(10, 0))

        # Description
        desc_label = ctk.CTkLabel(
            content_frame,
            text=project['description'],
            font=ctk.CTkFont(size=12),
            text_color=("gray40", "gray60"),
            anchor="w"
        )
        desc_label.grid(row=1, column=0, columnspan=2, sticky="w", pady=(5, 0))

        # Path and last run info
        info_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        info_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(10, 0))

        # Only show path if it exists
        if project.get('path'):
            path_label = ctk.CTkLabel(
                info_frame,
                text=f"Path: {project['path']}",
                font=ctk.CTkFont(size=11),
                text_color=("gray30", "gray70")
            )
            path_label.grid(row=0, column=0, sticky="w")

        last_run_label = ctk.CTkLabel(
            info_frame,
            text=f"Last run: {project['last_run']}",
            font=ctk.CTkFont(size=11),
            text_color=("gray30", "gray70")
        )
        last_run_label.grid(row=0, column=1, sticky="e", padx=(20, 0))

        info_frame.grid_columnconfigure(0, weight=1)

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
        """Show empty state when no projects exist"""
        empty_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        empty_frame.grid(row=0, column=0, padx=50, pady=50)

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

    def add_new_project(self):
        """Add a new project"""
        self.show_message("To add a new script, edit config/scripts_config.py", "info")

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

        # Format the statistics message
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
            self.refresh_projects()  # Refresh the display
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
        # Refresh project list to show latest history
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
