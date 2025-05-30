"""
Script execution history manager for tracking script runs and their results
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path


class ScriptHistory:
    """Represents a single script execution record"""

    def __init__(self, script_name: str, script_path: str, status: str,
                 exit_code: int, start_time: str, end_time: str,
                 duration: float, error_message: Optional[str] = None):
        self.script_name = script_name
        self.script_path = script_path
        self.status = status  # 'success', 'error', 'stopped'
        self.exit_code = exit_code
        self.start_time = start_time
        self.end_time = end_time
        self.duration = duration  # in seconds
        self.error_message = error_message

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'script_name': self.script_name,
            'script_path': self.script_path,
            'status': self.status,
            'exit_code': self.exit_code,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'duration': self.duration,
            'error_message': self.error_message
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create ScriptHistory from dictionary"""
        return cls(
            script_name=data['script_name'],
            script_path=data['script_path'],
            status=data['status'],
            exit_code=data.get('exit_code', 0),
            start_time=data['start_time'],
            end_time=data['end_time'],
            duration=data.get('duration', 0),
            error_message=data.get('error_message')
        )


class ScriptHistoryManager:
    """Manages script execution history storage and retrieval"""

    def __init__(self, history_dir: str = "data/script_history"):
        """Initialize the history manager

        Args:
            history_dir: Directory to store history files
        """
        self.history_dir = history_dir
        self.history_file = os.path.join(history_dir, "execution_history.json")
        self.ensure_history_directory()
        self._history_cache = None
        self._current_run = {}  # Track current running scripts

    def ensure_history_directory(self):
        """Ensure the history directory exists"""
        os.makedirs(self.history_dir, exist_ok=True)

    def load_history(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load all script execution history

        Returns:
            Dictionary mapping script names to their execution history
        """
        if self._history_cache is not None:
            return self._history_cache

        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    self._history_cache = json.load(f)
                    return self._history_cache
            except Exception as e:
                print(f"Error loading history: {e}")
                return {}
        return {}

    def save_history(self, history: Dict[str, List[Dict[str, Any]]]) -> bool:
        """Save history to file

        Args:
            history: Complete history dictionary

        Returns:
            True if successful, False otherwise
        """
        try:
            with open(self.history_file, 'w') as f:
                json.dump(history, f, indent=2)
            self._history_cache = history
            return True
        except Exception as e:
            print(f"Error saving history: {e}")
            return False

    def start_script_run(self, script_name: str, script_path: str) -> str:
        """Record the start of a script execution

        Args:
            script_name: Display name of the script
            script_path: Path to the script file

        Returns:
            Run ID (timestamp) for this execution
        """
        start_time = datetime.now().isoformat()
        run_id = start_time

        self._current_run[script_name] = {
            'script_name': script_name,
            'script_path': script_path,
            'start_time': start_time,
            'run_id': run_id
        }

        return run_id

    def end_script_run(self, script_name: str, status: str, exit_code: int,
                       error_message: Optional[str] = None) -> bool:
        """Record the end of a script execution

        Args:
            script_name: Display name of the script
            status: Final status ('success', 'error', 'stopped')
            exit_code: Process exit code
            error_message: Optional error message

        Returns:
            True if successful, False otherwise
        """
        if script_name not in self._current_run:
            print(f"No active run found for script: {script_name}")
            return False

        run_data = self._current_run[script_name]
        end_time = datetime.now().isoformat()

        # Calculate duration
        start_dt = datetime.fromisoformat(run_data['start_time'])
        end_dt = datetime.fromisoformat(end_time)
        duration = (end_dt - start_dt).total_seconds()

        # Create history entry
        history_entry = ScriptHistory(
            script_name=script_name,
            script_path=run_data['script_path'],
            status=status,
            exit_code=exit_code,
            start_time=run_data['start_time'],
            end_time=end_time,
            duration=duration,
            error_message=error_message
        )

        # Add to history
        history = self.load_history()
        if script_name not in history:
            history[script_name] = []

        history[script_name].append(history_entry.to_dict())

        # Keep only last 100 runs per script
        if len(history[script_name]) > 100:
            history[script_name] = history[script_name][-100:]

        # Save and cleanup
        success = self.save_history(history)
        if success:
            del self._current_run[script_name]

        return success

    def get_last_run(self, script_name: str) -> Optional[Dict[str, Any]]:
        """Get the most recent run for a script

        Args:
            script_name: Display name of the script

        Returns:
            Dictionary with last run info or None if no history
        """
        history = self.load_history()
        script_history = history.get(script_name, [])

        if script_history:
            return script_history[-1]
        return None

    def get_last_run_info(self, script_name: str) -> tuple[Optional[str], Optional[str]]:
        """Get formatted last run time and status for display

        Args:
            script_name: Display name of the script

        Returns:
            Tuple of (formatted_time, status) or (None, None) if no history
        """
        last_run = self.get_last_run(script_name)

        if not last_run:
            return None, None

        # Format the time
        try:
            run_time = datetime.fromisoformat(last_run['end_time'])
            now = datetime.now()

            # Format based on how recent
            if run_time.date() == now.date():
                formatted_time = run_time.strftime("Today at %I:%M %p")
            elif (now - run_time).days == 1:
                formatted_time = run_time.strftime("Yesterday at %I:%M %p")
            elif (now - run_time).days < 7:
                formatted_time = run_time.strftime("%A at %I:%M %p")
            else:
                formatted_time = run_time.strftime("%Y-%m-%d %I:%M %p")

        except:
            formatted_time = "Unknown"

        return formatted_time, last_run.get('status', 'unknown')

    def get_script_stats(self, script_name: str) -> Dict[str, Any]:
        """Get statistics for a script

        Args:
            script_name: Display name of the script

        Returns:
            Dictionary with stats (total_runs, success_rate, avg_duration, etc.)
        """
        history = self.load_history()
        script_history = history.get(script_name, [])

        if not script_history:
            return {
                'total_runs': 0,
                'success_rate': 0,
                'avg_duration': 0,
                'last_success': None,
                'last_failure': None
            }

        total_runs = len(script_history)
        successful_runs = sum(1 for run in script_history if run['status'] == 'success')
        total_duration = sum(run.get('duration', 0) for run in script_history)

        last_success = None
        last_failure = None

        for run in reversed(script_history):
            if run['status'] == 'success' and last_success is None:
                last_success = run['end_time']
            elif run['status'] == 'error' and last_failure is None:
                last_failure = run['end_time']

            if last_success and last_failure:
                break

        return {
            'total_runs': total_runs,
            'success_rate': (successful_runs / total_runs * 100) if total_runs > 0 else 0,
            'avg_duration': total_duration / total_runs if total_runs > 0 else 0,
            'last_success': last_success,
            'last_failure': last_failure
        }

    def get_runs_by_status(self, script_name: str, status: str) -> List[Dict[str, Any]]:
        """Get all runs for a script filtered by status

        Args:
            script_name: Display name of the script
            status: Status to filter by ('success', 'error', 'stopped')

        Returns:
            List of run dictionaries matching the status
        """
        history = self.load_history()
        script_history = history.get(script_name, [])

        return [run for run in script_history if run.get('status') == status]

    def get_runs_in_date_range(self, script_name: str, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Get runs within a specific date range

        Args:
            script_name: Display name of the script
            start_date: Start date in ISO format
            end_date: End date in ISO format

        Returns:
            List of run dictionaries within the date range
        """
        from datetime import datetime

        history = self.load_history()
        script_history = history.get(script_name, [])

        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)

        filtered_runs = []
        for run in script_history:
            try:
                run_dt = datetime.fromisoformat(run.get('end_time', ''))
                if start_dt <= run_dt <= end_dt:
                    filtered_runs.append(run)
            except ValueError:
                continue  # Skip runs with invalid timestamps

        return filtered_runs

    def get_recent_runs(self, script_name: str, days: int = 7) -> List[Dict[str, Any]]:
        """Get recent runs for a script

        Args:
            script_name: Display name of the script
            days: Number of days to look back

        Returns:
            List of recent run dictionaries
        """
        from datetime import datetime, timedelta

        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        return self.get_runs_in_date_range(
            script_name,
            start_date.isoformat(),
            end_date.isoformat()
        )

    def get_error_summary(self, script_name: str) -> Dict[str, int]:
        """Get a summary of error types for a script

        Args:
            script_name: Display name of the script

        Returns:
            Dictionary mapping error types/exit codes to their counts
        """
        error_runs = self.get_runs_by_status(script_name, 'error')
        error_summary = {}

        for run in error_runs:
            exit_code = run.get('exit_code', 'Unknown')
            error_key = f"Exit Code {exit_code}"

            if run.get('error_message'):
                # Try to categorize by error message keywords
                error_msg = run['error_message'].lower()
                if 'file not found' in error_msg or 'no such file' in error_msg:
                    error_key = "File Not Found"
                elif 'permission denied' in error_msg:
                    error_key = "Permission Denied"
                elif 'timeout' in error_msg:
                    error_key = "Timeout"
                elif 'connection' in error_msg:
                    error_key = "Connection Error"
                # Add more categorizations as needed

            error_summary[error_key] = error_summary.get(error_key, 0) + 1

        return error_summary

    def get_performance_metrics(self, script_name: str) -> Dict[str, float]:
        """Get performance metrics for a script

        Args:
            script_name: Display name of the script

        Returns:
            Dictionary with performance metrics
        """
        history = self.load_history()
        script_history = history.get(script_name, [])

        if not script_history:
            return {
                'min_duration': 0,
                'max_duration': 0,
                'median_duration': 0,
                'percentile_95': 0
            }

        durations = [run.get('duration', 0) for run in script_history if run.get('duration')]
        durations.sort()

        if not durations:
            return {
                'min_duration': 0,
                'max_duration': 0,
                'median_duration': 0,
                'percentile_95': 0
            }

        n = len(durations)

        return {
            'min_duration': durations[0],
            'max_duration': durations[-1],
            'median_duration': durations[n // 2],
            'percentile_95': durations[int(n * 0.95)] if n > 0 else 0
        }

    def export_script_history(self, script_name: str, file_path: str, format: str = 'csv') -> bool:
        """Export script history to a file

        Args:
            script_name: Display name of the script
            file_path: Path where to save the export
            format: Export format ('csv', 'json')

        Returns:
            True if successful, False otherwise
        """
        history = self.load_history()
        script_history = history.get(script_name, [])

        if not script_history:
            return False

        try:
            if format.lower() == 'csv':
                import csv
                with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                    fieldnames = ['script_name', 'script_path', 'status', 'exit_code',
                                  'start_time', 'end_time', 'duration', 'error_message']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                    writer.writeheader()
                    for run in script_history:
                        writer.writerow(run)

            elif format.lower() == 'json':
                import json
                with open(file_path, 'w', encoding='utf-8') as jsonfile:
                    json.dump({script_name: script_history}, jsonfile, indent=2)

            else:
                return False

            return True

        except Exception as e:
            print(f"Error exporting history: {e}")
            return False

    def clear_history(self, script_name: Optional[str] = None) -> bool:
        """Clear execution history

        Args:
            script_name: If provided, clear only this script's history.
                        If None, clear all history.

        Returns:
            True if successful, False otherwise
        """
        if script_name:
            history = self.load_history()
            if script_name in history:
                del history[script_name]
                return self.save_history(history)
        else:
            # Clear all history
            return self.save_history({})

        return True


# Global instance
_history_manager = None


def get_history_manager() -> ScriptHistoryManager:
    """Get the global history manager instance"""
    global _history_manager
    if _history_manager is None:
        _history_manager = ScriptHistoryManager()
    return _history_manager
