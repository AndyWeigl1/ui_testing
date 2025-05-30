"""
Detailed Script History Dialog - Shows comprehensive execution history for scripts
Save this as: components/script_history_dialog.py
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import csv
import os


class ScriptHistoryDialog(ctk.CTkToplevel):
    """Dialog for displaying detailed script execution history"""

    def __init__(self, parent, script_name: str, history_manager, **kwargs):
        """Initialize the script history dialog

        Args:
            parent: Parent window
            script_name: Name of the script to show history for
            history_manager: ScriptHistoryManager instance
        """
        super().__init__(parent, **kwargs)

        self.script_name = script_name
        self.history_manager = history_manager
        self.all_history = []
        self.filtered_history = []

        # Window setup
        self.title(f"Execution History - {script_name}")
        self.geometry("1000x700")
        self.resizable(True, True)

        # Make dialog modal
        self.transient(parent)
        self.grab_set()

        # Center the dialog
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (1000 // 2)
        y = (self.winfo_screenheight() // 2) - (700 // 2)
        self.geometry(f"+{x}+{y}")

        # Load history data
        self.load_history_data()

        # Create UI
        self.create_ui()

        # Apply initial filter
        self.apply_filters()

        # Focus on the window
        self.focus_set()

    def load_history_data(self):
        """Load history data from the history manager"""
        all_history = self.history_manager.load_history()
        self.all_history = all_history.get(self.script_name, [])

        # Sort by start time (most recent first)
        self.all_history.sort(key=lambda x: x.get('start_time', ''), reverse=True)

    def create_ui(self):
        """Create the dialog UI"""
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Header section
        self.create_header()

        # Filter section
        self.create_filters()

        # History table
        self.create_history_table()

        # Button section
        self.create_buttons()

    def create_header(self):
        """Create the header with summary statistics"""
        header_frame = ctk.CTkFrame(self)
        header_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        header_frame.grid_columnconfigure(1, weight=1)

        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text=f"Execution History: {self.script_name}",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.grid(row=0, column=0, columnspan=4, pady=(15, 10), sticky="w", padx=15)

        # Get summary stats
        stats = self.history_manager.get_script_stats(self.script_name)

        # Stats cards
        stats_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        stats_frame.grid(row=1, column=0, columnspan=4, pady=(0, 15), padx=15, sticky="ew")

        # Total runs
        self.create_stat_card(stats_frame, "Total Runs", str(stats['total_runs']), 0)

        # Success rate
        success_rate = f"{stats['success_rate']:.1f}%"
        self.create_stat_card(stats_frame, "Success Rate", success_rate, 1)

        # Average duration
        avg_duration = f"{stats['avg_duration']:.1f}s"
        self.create_stat_card(stats_frame, "Avg Duration", avg_duration, 2)

        # Last run
        if self.all_history:
            last_run = self.format_datetime(self.all_history[0]['end_time'])
            last_status = self.all_history[0]['status'].title()
            self.create_stat_card(stats_frame, "Last Run", f"{last_run}\n({last_status})", 3)

    def create_stat_card(self, parent, title: str, value: str, column: int):
        """Create a small statistics card"""
        card = ctk.CTkFrame(parent)
        card.grid(row=0, column=column, padx=5, pady=5, sticky="ew")
        parent.grid_columnconfigure(column, weight=1)

        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("gray40", "gray60")
        )
        title_label.grid(row=0, column=0, pady=(10, 2), padx=10)

        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        value_label.grid(row=1, column=0, pady=(2, 10), padx=10)

    def create_filters(self):
        """Create filter controls"""
        filter_frame = ctk.CTkFrame(self)
        filter_frame.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="ew")
        filter_frame.grid_columnconfigure(2, weight=1)

        # Status filter
        status_label = ctk.CTkLabel(filter_frame, text="Status:")
        status_label.grid(row=0, column=0, padx=(15, 5), pady=10)

        self.status_var = ctk.StringVar(value="All")
        self.status_filter = ctk.CTkOptionMenu(
            filter_frame,
            values=["All", "Success", "Error", "Stopped", "Unknown"],
            variable=self.status_var,
            command=self.apply_filters,
            width=120
        )
        self.status_filter.grid(row=0, column=1, padx=5, pady=10)

        # Search box
        search_label = ctk.CTkLabel(filter_frame, text="Search:")
        search_label.grid(row=0, column=2, padx=(20, 5), pady=10, sticky="e")

        self.search_var = ctk.StringVar()
        self.search_var.trace('w', lambda *args: self.apply_filters())

        self.search_entry = ctk.CTkEntry(
            filter_frame,
            placeholder_text="Search in error messages...",
            textvariable=self.search_var,
            width=200
        )
        self.search_entry.grid(row=0, column=3, padx=(5, 15), pady=10)

    def create_history_table(self):
        """Create the history table using tkinter Treeview"""
        table_frame = ctk.CTkFrame(self)
        table_frame.grid(row=2, column=0, padx=20, pady=(0, 10), sticky="nsew")
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)

        # Create treeview with scrollbar
        tree_container = tk.Frame(table_frame, bg=self._apply_appearance_mode(("#dbdbdb", "#212121")))
        tree_container.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        tree_container.grid_columnconfigure(0, weight=1)
        tree_container.grid_rowconfigure(0, weight=1)

        # Define columns
        columns = ("datetime", "status", "duration", "exit_code", "error_message")

        self.tree = ttk.Treeview(tree_container, columns=columns, show="headings", height=25)

        # Configure column headings and widths
        self.tree.heading("datetime", text="Date & Time")
        self.tree.heading("status", text="Status")
        self.tree.heading("duration", text="Duration")
        self.tree.heading("exit_code", text="Exit Code")
        self.tree.heading("error_message", text="Error Message")

        self.tree.column("datetime", width=150, minwidth=120)
        self.tree.column("status", width=80, minwidth=60)
        self.tree.column("duration", width=80, minwidth=60)
        self.tree.column("exit_code", width=80, minwidth=60)
        self.tree.column("error_message", width=400, minwidth=200)

        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_container, orient="horizontal", command=self.tree.xview)

        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # Grid the tree and scrollbars
        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")

        # Configure tags for different statuses
        self.tree.tag_configure("success", foreground="#4CAF50")
        self.tree.tag_configure("error", foreground="#f44336")
        self.tree.tag_configure("stopped", foreground="#FF9800")
        self.tree.tag_configure("unknown", foreground="#9E9E9E")

        # Bind double-click for details
        self.tree.bind("<Double-1>", self.show_run_details)

    def create_buttons(self):
        """Create action buttons"""
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="ew")
        button_frame.grid_columnconfigure(0, weight=1)

        # Left side buttons
        left_buttons = ctk.CTkFrame(button_frame, fg_color="transparent")
        left_buttons.grid(row=0, column=0, sticky="w")

        refresh_btn = ctk.CTkButton(
            left_buttons,
            text="🔄 Refresh",
            width=100,
            command=self.refresh_data,
            fg_color=("gray70", "gray30")
        )
        refresh_btn.grid(row=0, column=0, padx=(0, 10))

        export_btn = ctk.CTkButton(
            left_buttons,
            text="📊 Export CSV",
            width=120,
            command=self.export_to_csv,
            fg_color=("gray70", "gray30")
        )
        export_btn.grid(row=0, column=1, padx=(0, 10))

        clear_btn = ctk.CTkButton(
            left_buttons,
            text="🗑 Clear History",
            width=120,
            command=self.clear_history,
            fg_color=("#f44336", "#d32f2f"),
            hover_color=("#d32f2f", "#b71c1c")
        )
        clear_btn.grid(row=0, column=2)

        # Right side buttons
        right_buttons = ctk.CTkFrame(button_frame, fg_color="transparent")
        right_buttons.grid(row=0, column=1, sticky="e")

        close_btn = ctk.CTkButton(
            right_buttons,
            text="Close",
            width=100,
            command=self.destroy
        )
        close_btn.grid(row=0, column=0)

    def apply_filters(self, *args):
        """Apply current filters to the history data"""
        status_filter = self.status_var.get()
        search_term = self.search_var.get().lower()

        # Filter the history
        self.filtered_history = []
        for run in self.all_history:
            # Status filter
            if status_filter != "All" and run['status'].lower() != status_filter.lower():
                continue

            # Search filter
            if search_term:
                searchable_text = f"{run.get('error_message', '')}".lower()
                if search_term not in searchable_text:
                    continue

            self.filtered_history.append(run)

        # Update the table
        self.update_table()

    def update_table(self):
        """Update the table with filtered history data"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Add filtered history
        for run in self.filtered_history:
            # Format the data
            datetime_str = self.format_datetime(run['end_time'])
            status = run['status'].title()
            duration = f"{run.get('duration', 0):.1f}s"
            exit_code = str(run.get('exit_code', 'N/A'))
            error_msg = run.get('error_message', '') or ''

            # Truncate long error messages
            if len(error_msg) > 50:
                error_msg = error_msg[:47] + "..."

            # Insert into tree with appropriate tag
            tag = run['status'].lower()
            self.tree.insert("", "end", values=(
                datetime_str, status, duration, exit_code, error_msg
            ), tags=(tag,))

    def format_datetime(self, iso_string: str) -> str:
        """Format ISO datetime string for display"""
        try:
            dt = datetime.fromisoformat(iso_string)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except:
            return iso_string

    def show_run_details(self, event):
        """Show detailed information for a selected run"""
        selection = self.tree.selection()
        if not selection:
            return

        item = self.tree.item(selection[0])
        values = item['values']

        if not values:
            return

        # Find the corresponding run data
        datetime_str = values[0]
        matching_run = None

        for run in self.filtered_history:
            if self.format_datetime(run['end_time']) == datetime_str:
                matching_run = run
                break

        if matching_run:
            self.show_detailed_run_info(matching_run)

    def show_detailed_run_info(self, run_data: Dict[str, Any]):
        """Show detailed information about a specific run"""
        details_window = ctk.CTkToplevel(self)
        details_window.title("Run Details")
        details_window.geometry("600x400")
        details_window.transient(self)
        details_window.grab_set()

        # Center the window
        details_window.update_idletasks()
        x = (details_window.winfo_screenwidth() // 2) - (600 // 2)
        y = (details_window.winfo_screenheight() // 2) - (400 // 2)
        details_window.geometry(f"+{x}+{y}")

        # Create scrollable text widget
        text_frame = ctk.CTkFrame(details_window)
        text_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        details_window.grid_columnconfigure(0, weight=1)
        details_window.grid_rowconfigure(0, weight=1)

        text_widget = ctk.CTkTextbox(text_frame, wrap="word")
        text_widget.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        text_frame.grid_columnconfigure(0, weight=1)
        text_frame.grid_rowconfigure(0, weight=1)

        # Format the run data
        details_text = f"""Script Execution Details

Script Name: {run_data.get('script_name', 'N/A')}
Script Path: {run_data.get('script_path', 'N/A')}

Execution Timeline:
  Start Time: {self.format_datetime(run_data.get('start_time', ''))}
  End Time: {self.format_datetime(run_data.get('end_time', ''))}
  Duration: {run_data.get('duration', 0):.2f} seconds

Result:
  Status: {run_data.get('status', 'Unknown').title()}
  Exit Code: {run_data.get('exit_code', 'N/A')}

Error Information:
"""

        error_msg = run_data.get('error_message', '')
        if error_msg:
            details_text += f"  {error_msg}"
        else:
            details_text += "  No error message recorded"

        text_widget.insert("0.0", details_text)
        text_widget.configure(state="disabled")

        # Close button
        close_btn = ctk.CTkButton(
            details_window,
            text="Close",
            command=details_window.destroy
        )
        close_btn.grid(row=1, column=0, pady=(0, 20))

    def refresh_data(self):
        """Refresh the history data"""
        self.load_history_data()
        self.apply_filters()

    def export_to_csv(self):
        """Export the filtered history to CSV"""
        if not self.filtered_history:
            messagebox.showinfo("No Data", "No history data to export.")
            return

        filename = filedialog.asksaveasfilename(
            title="Export History to CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialname=f"{self.script_name}_history.csv"
        )

        if filename:
            try:
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    fieldnames = ['script_name', 'start_time', 'end_time', 'duration',
                                'status', 'exit_code', 'error_message']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                    writer.writeheader()
                    for run in self.filtered_history:
                        writer.writerow({
                            'script_name': run.get('script_name', ''),
                            'start_time': run.get('start_time', ''),
                            'end_time': run.get('end_time', ''),
                            'duration': run.get('duration', 0),
                            'status': run.get('status', ''),
                            'exit_code': run.get('exit_code', ''),
                            'error_message': run.get('error_message', '')
                        })

                messagebox.showinfo("Export Complete", f"History exported to:\n{filename}")

            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export history:\n{str(e)}")

    def clear_history(self):
        """Clear the history for this script"""
        result = messagebox.askyesno(
            "Clear History",
            f"Are you sure you want to clear all execution history for '{self.script_name}'?\n\n"
            "This action cannot be undone.",
            icon="warning"
        )

        if result:
            success = self.history_manager.clear_history(self.script_name)
            if success:
                messagebox.showinfo("History Cleared", "Script history has been cleared successfully.")
                self.load_history_data()
                self.apply_filters()
            else:
                messagebox.showerror("Error", "Failed to clear script history.")