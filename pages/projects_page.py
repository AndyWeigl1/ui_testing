"""Projects page - manage and organize scripts"""

import customtkinter as ctk
from pages.base_page import BasePage
from typing import List, Dict, Any


class ProjectsPage(BasePage):
    """Projects page for managing scripts and projects"""
    
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
        
        # Sample projects (in real app, these would come from storage)
        self.projects = [
            {
                'name': 'Data Processing Script',
                'description': 'Processes CSV files and generates reports',
                'path': '/scripts/data_processor.py',
                'last_run': '2024-01-15',
                'status': 'success',
                'sop_id': 'data_processing'  # Add this field
            },
            {
                'name': 'Web Scraper',
                'description': 'Extracts data from websites',
                'path': '/scripts/web_scraper.py',
                'last_run': '2024-01-14',
                'status': 'success',
                'sop_id': 'web_scraping'  # Add this field
            },
            {
                'name': 'Backup Automation',
                'description': 'Automated backup of important files',
                'path': '/scripts/backup.py',
                'last_run': '2024-01-13',
                'status': 'error'
            },
            {
                'name': 'Image Processor',
                'description': 'Batch image resizing and optimization',
                'path': '/scripts/image_processor.py',
                'last_run': 'Never',
                'status': 'idle'
            }
        ]
        
        # Display projects
        self.display_projects()
        
        # Info panel (shown when no projects)
        if not self.projects:
            self.show_empty_state()
            
    def display_projects(self):
        """Display the list of projects"""
        # Clear existing widgets
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
            
        # Create project cards
        for i, project in enumerate(self.projects):
            self.create_project_card(project, i)
            
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
            'idle': "#757575"
        }
        status_label = ctk.CTkLabel(
            content_frame,
            text=f"● {project['status'].title()}",
            text_color=status_colors.get(project['status'], "#757575"),
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

        # Add SOP button if project has an associated SOP
        if project.get('sop_id'):
            sop_btn = ctk.CTkButton(
                button_frame,
                text="📖 SOP",
                width=80,
                height=28,
                fg_color=("#1f6aa5", "#1f6aa5"),
                hover_color=("#144870", "#144870"),
                command=lambda p=project: self.open_project_sop(p)
            )
            sop_btn.grid(row=0, column=1, padx=5)
        
        edit_btn = ctk.CTkButton(
            button_frame,
            text="Edit",
            width=80,
            height=28,
            fg_color=("gray70", "gray30"),
            command=lambda p=project: self.edit_project(p)
        )
        edit_btn.grid(row=0, column=1, padx=5)
        
        delete_btn = ctk.CTkButton(
            button_frame,
            text="Delete",
            width=80,
            height=28,
            fg_color=("gray70", "gray30"),
            hover_color=("gray60", "gray40"),
            command=lambda p=project: self.delete_project(p)
        )
        delete_btn.grid(row=0, column=2, padx=(5, 0))
        
    def show_empty_state(self):
        """Show empty state when no projects exist"""
        empty_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        empty_frame.grid(row=0, column=0, padx=50, pady=50)
        
        empty_label = ctk.CTkLabel(
            empty_frame,
            text="No projects yet",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=("gray40", "gray60")
        )
        empty_label.grid(row=0, column=0, pady=(0, 10))
        
        help_label = ctk.CTkLabel(
            empty_frame,
            text="Click '+ New Project' to create your first script project",
            font=ctk.CTkFont(size=14),
            text_color=("gray30", "gray70")
        )
        help_label.grid(row=1, column=0)
        
    def add_new_project(self):
        """Add a new project"""
        self.show_message("Project creation dialog would appear here", "info")
        # In a real app, this would open a dialog to create a new project
        
    def run_project(self, project: Dict[str, Any]):
        """Run a project"""
        # Switch to Process page and load the script
        self.set_state('current_page', 'Process')
        self.set_state('script_path', project['path'])
        self.publish_event('project.run', {'project': project})
        self.show_message(f"Running project: {project['name']}", "info")
        
    def edit_project(self, project: Dict[str, Any]):
        """Edit a project"""
        self.show_message(f"Edit dialog for '{project['name']}' would appear here", "info")
        # In a real app, this would open an edit dialog
        
    def delete_project(self, project: Dict[str, Any]):
        """Delete a project"""
        self.show_message(f"Confirm deletion of '{project['name']}'", "warning")
        # In a real app, this would show a confirmation dialog
        
    def on_activate(self):
        """Called when the Projects page becomes active"""
        super().on_activate()
        # Could refresh project list from storage here
        
    def setup_event_subscriptions(self):
        """Set up event subscriptions"""
        # Listen for project-related events
        self.event_bus.subscribe('project.created', lambda data: self.display_projects())
        self.event_bus.subscribe('project.updated', lambda data: self.display_projects())
        self.event_bus.subscribe('project.deleted', lambda data: self.display_projects())

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
