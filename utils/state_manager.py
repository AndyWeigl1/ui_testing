"""State management system for centralized application state with observer pattern"""

from typing import Dict, Any, Callable, List, Optional, Set
import logging
from copy import deepcopy
from .event_bus import get_event_bus, Events


class StateManager:
    """Centralized state management with observer pattern support"""
    
    def __init__(self, initial_state: Optional[Dict[str, Any]] = None):
        """Initialize the state manager with optional initial state
        
        Args:
            initial_state: Optional dictionary of initial state values
        """
        # Default state values
        self._state: Dict[str, Any] = {
            'current_page': 'About',
            'script_running': False,
            'theme': 'dark',
            'font_size': 12,
            'window_title': 'Script Runner - Modern UI',
            'status': 'idle',
            'last_output': None,
            'script_path': None,
            'export_path': None,
        }
        
        # Override with any provided initial state
        if initial_state:
            self._state.update(initial_state)
        
        # Store observers for each state key
        self._observers: Dict[str, List[Callable[[Any], None]]] = {}
        
        # Store the previous state for comparison
        self._previous_state: Dict[str, Any] = deepcopy(self._state)
        
        # Logger
        self._logger = logging.getLogger(__name__)
        
        # Get event bus for integration
        self._event_bus = get_event_bus()
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a state value by key
        
        Args:
            key: The state key to retrieve
            default: Default value if key doesn't exist
            
        Returns:
            The state value or default if not found
        """
        return self._state.get(key, default)
    
    def get_all(self) -> Dict[str, Any]:
        """Get a copy of the entire state
        
        Returns:
            A deep copy of the current state
        """
        return deepcopy(self._state)
    
    def set(self, key: str, value: Any, notify: bool = True) -> None:
        """Set a state value and notify observers
        
        Args:
            key: The state key to set
            value: The new value
            notify: Whether to notify observers of the change
        """
        old_value = self._state.get(key)
        
        # Only update if the value has changed
        if old_value != value:
            self._logger.debug(f"State change: {key} = {value} (was {old_value})")
            
            # Update the state
            self._state[key] = value
            
            # Notify observers if requested
            if notify:
                self._notify_observers(key, value, old_value)
                
                # Publish state change event
                self._event_bus.publish('state.changed', {
                    'key': key,
                    'value': value,
                    'old_value': old_value
                })
    
    def update(self, updates: Dict[str, Any], notify: bool = True) -> None:
        """Update multiple state values at once
        
        Args:
            updates: Dictionary of key-value pairs to update
            notify: Whether to notify observers of changes
        """
        changed_keys = []
        
        for key, value in updates.items():
            if self._state.get(key) != value:
                changed_keys.append(key)
                self.set(key, value, notify=False)
        
        # Notify observers for all changed keys if requested
        if notify and changed_keys:
            for key in changed_keys:
                self._notify_observers(key, self._state[key], self._previous_state.get(key))
            
            # Publish batch update event
            self._event_bus.publish('state.batch_update', {
                'keys': changed_keys,
                'updates': {k: self._state[k] for k in changed_keys}
            })
    
    def subscribe(self, key: str, callback: Callable[[Any], None]) -> None:
        """Subscribe to changes for a specific state key
        
        Args:
            key: The state key to watch
            callback: Function to call when the value changes
        """
        if key not in self._observers:
            self._observers[key] = []
        
        if callback not in self._observers[key]:
            self._observers[key].append(callback)
            self._logger.debug(f"Subscribed to state key '{key}': {callback.__name__}")
    
    def subscribe_multiple(self, keys: List[str], callback: Callable[[str, Any], None]) -> None:
        """Subscribe to changes for multiple state keys with a single callback
        
        Args:
            keys: List of state keys to watch
            callback: Function to call when any value changes (receives key and value)
        """
        for key in keys:
            # Wrap the callback to include the key
            wrapped_callback = lambda value, k=key: callback(k, value)
            self.subscribe(key, wrapped_callback)
    
    def unsubscribe(self, key: str, callback: Callable[[Any], None]) -> bool:
        """Unsubscribe from changes for a specific state key
        
        Args:
            key: The state key to stop watching
            callback: The callback function to remove
            
        Returns:
            True if the callback was found and removed, False otherwise
        """
        if key in self._observers:
            try:
                self._observers[key].remove(callback)
                self._logger.debug(f"Unsubscribed from state key '{key}': {callback.__name__}")
                
                # Clean up empty observer lists
                if not self._observers[key]:
                    del self._observers[key]
                
                return True
            except ValueError:
                pass
        
        return False
    
    def _notify_observers(self, key: str, value: Any, old_value: Any) -> None:
        """Notify all observers of a state change
        
        Args:
            key: The state key that changed
            value: The new value
            old_value: The previous value
        """
        if key in self._observers:
            self._logger.debug(f"Notifying {len(self._observers[key])} observers for key '{key}'")
            
            for callback in self._observers[key].copy():  # Copy to avoid modification during iteration
                try:
                    callback(value)
                except Exception as e:
                    self._logger.error(f"Error calling observer {callback.__name__} for key '{key}': {e}")
    
    def has_observers(self, key: str) -> bool:
        """Check if a state key has any observers
        
        Args:
            key: The state key to check
            
        Returns:
            True if the key has observers, False otherwise
        """
        return key in self._observers and len(self._observers[key]) > 0
    
    def get_observer_count(self, key: str) -> int:
        """Get the number of observers for a state key
        
        Args:
            key: The state key to check
            
        Returns:
            Number of observers for the key
        """
        return len(self._observers.get(key, []))
    
    def clear_observers(self, key: Optional[str] = None) -> None:
        """Clear observers for a specific key or all keys
        
        Args:
            key: Optional state key to clear observers for. If None, clears all observers.
        """
        if key is None:
            self._observers.clear()
            self._logger.debug("Cleared all state observers")
        elif key in self._observers:
            del self._observers[key]
            self._logger.debug(f"Cleared observers for state key '{key}'")
    
    def reset(self, preserve_keys: Optional[List[str]] = None) -> None:
        """Reset state to initial values
        
        Args:
            preserve_keys: Optional list of keys to preserve during reset
        """
        preserved_values = {}
        
        if preserve_keys:
            for key in preserve_keys:
                if key in self._state:
                    preserved_values[key] = self._state[key]
        
        # Reset to initial state
        self._state = {
            'current_page': 'About',
            'script_running': False,
            'theme': 'dark',
            'font_size': 12,
            'window_title': 'Script Runner - Modern UI',
            'status': 'idle',
            'last_output': None,
            'script_path': None,
            'export_path': None,
        }
        
        # Restore preserved values
        self._state.update(preserved_values)
        
        # Notify all observers of reset
        for key in self._state:
            if key in self._observers:
                self._notify_observers(key, self._state[key], self._previous_state.get(key))
        
        self._event_bus.publish('state.reset', {'preserved_keys': preserve_keys})
        self._logger.info(f"State reset with preserved keys: {preserve_keys}")
    
    def get_diff(self) -> Dict[str, tuple]:
        """Get the differences between current and previous state
        
        Returns:
            Dictionary of changed keys with (old_value, new_value) tuples
        """
        diff = {}
        
        all_keys = set(self._state.keys()) | set(self._previous_state.keys())
        
        for key in all_keys:
            current = self._state.get(key)
            previous = self._previous_state.get(key)
            
            if current != previous:
                diff[key] = (previous, current)
        
        return diff
    
    def commit(self) -> None:
        """Commit the current state as the new previous state"""
        self._previous_state = deepcopy(self._state)
    
    def rollback(self) -> None:
        """Rollback to the previous state"""
        self._state = deepcopy(self._previous_state)
        
        # Notify all observers
        for key in self._state:
            if key in self._observers:
                self._notify_observers(key, self._state[key], None)
        
        self._event_bus.publish('state.rollback', {})
        self._logger.info("State rolled back to previous state")

    def save_to_file(self, filepath: str = "config/user_settings.json") -> bool:
        """Save current state to a JSON file

        Args:
            filepath: Path to save the settings file

        Returns:
            True if successful, False otherwise
        """
        try:
            import json
            import os

            # Ensure directory exists
            os.makedirs(os.path.dirname(filepath), exist_ok=True)

            # Save state to file
            with open(filepath, 'w') as f:
                json.dump(self._state, f, indent=2)

            self._logger.info(f"Settings saved to {filepath}")
            return True
        except Exception as e:
            self._logger.error(f"Error saving settings to file: {e}")
            return False

    def load_from_file(self, filepath: str = "config/user_settings.json") -> bool:
        """Load state from a JSON file

        Args:
            filepath: Path to load the settings file from

        Returns:
            True if successful, False otherwise
        """
        try:
            import json
            import os

            if not os.path.exists(filepath):
                self._logger.info(f"Settings file {filepath} not found, using defaults")
                return False

            with open(filepath, 'r') as f:
                loaded_state = json.load(f)

            # Update current state with loaded values
            self._state.update(loaded_state)

            self._logger.info(f"Settings loaded from {filepath}")
            return True
        except Exception as e:
            self._logger.error(f"Error loading settings from file: {e}")
            return False


# Global state manager instance
_global_state_manager: Optional[StateManager] = None


def get_state_manager() -> StateManager:
    """Get the global state manager instance (singleton pattern)
    
    Returns:
        The global StateManager instance
    """
    global _global_state_manager
    if _global_state_manager is None:
        _global_state_manager = StateManager()
    return _global_state_manager


def reset_state_manager() -> None:
    """Reset the global state manager (mainly for testing)"""
    global _global_state_manager
    _global_state_manager = None


# Convenience functions for common state operations
def get_state(key: str, default: Any = None) -> Any:
    """Get a state value from the global state manager"""
    return get_state_manager().get(key, default)


def set_state(key: str, value: Any) -> None:
    """Set a state value in the global state manager"""
    get_state_manager().set(key, value)


def update_state(updates: Dict[str, Any]) -> None:
    """Update multiple state values in the global state manager"""
    get_state_manager().update(updates)


def subscribe_to_state(key: str, callback: Callable[[Any], None]) -> None:
    """Subscribe to state changes in the global state manager"""
    get_state_manager().subscribe(key, callback)
