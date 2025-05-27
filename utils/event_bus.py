"""Event system for component communication using publish/subscribe pattern"""

from typing import Dict, List, Callable, Any, Optional
import logging


class EventBus:
    """Central event bus for decoupled component communication"""
    
    def __init__(self):
        """Initialize the event bus with empty subscriber dictionary"""
        self._subscribers: Dict[str, List[Callable]] = {}
        self._logger = logging.getLogger(__name__)
    
    def subscribe(self, event_name: str, callback: Callable[[Any], None]) -> None:
        """Register a callback function for a specific event
        
        Args:
            event_name: Name of the event to subscribe to
            callback: Function to call when event is published
        """
        if event_name not in self._subscribers:
            self._subscribers[event_name] = []
        
        if callback not in self._subscribers[event_name]:
            self._subscribers[event_name].append(callback)
            self._logger.debug(f"Subscribed to event '{event_name}': {callback.__name__}")
    
    def unsubscribe(self, event_name: str, callback: Callable[[Any], None]) -> bool:
        """Remove a callback from an event subscription
        
        Args:
            event_name: Name of the event to unsubscribe from
            callback: The callback function to remove
            
        Returns:
            True if callback was found and removed, False otherwise
        """
        if event_name in self._subscribers:
            try:
                self._subscribers[event_name].remove(callback)
                self._logger.debug(f"Unsubscribed from event '{event_name}': {callback.__name__}")
                
                # Clean up empty event lists
                if not self._subscribers[event_name]:
                    del self._subscribers[event_name]
                
                return True
            except ValueError:
                pass
        
        return False
    
    def publish(self, event_name: str, data: Any = None) -> None:
        """Publish an event to all subscribers
        
        Args:
            event_name: Name of the event to publish
            data: Optional data to pass to subscribers
        """
        if event_name in self._subscribers:
            self._logger.debug(f"Publishing event '{event_name}' to {len(self._subscribers[event_name])} subscribers")
            
            # Call all subscribers for this event
            for callback in self._subscribers[event_name].copy():  # Copy to avoid modification during iteration
                try:
                    callback(data)
                except Exception as e:
                    self._logger.error(f"Error calling subscriber {callback.__name__} for event '{event_name}': {e}")
    
    def has_subscribers(self, event_name: str) -> bool:
        """Check if an event has any subscribers
        
        Args:
            event_name: Name of the event to check
            
        Returns:
            True if event has subscribers, False otherwise
        """
        return event_name in self._subscribers and len(self._subscribers[event_name]) > 0
    
    def get_subscriber_count(self, event_name: str) -> int:
        """Get the number of subscribers for an event
        
        Args:
            event_name: Name of the event
            
        Returns:
            Number of subscribers for the event
        """
        return len(self._subscribers.get(event_name, []))
    
    def get_all_events(self) -> List[str]:
        """Get a list of all events that have subscribers
        
        Returns:
            List of event names
        """
        return list(self._subscribers.keys())
    
    def clear_all_subscribers(self) -> None:
        """Remove all subscribers from all events"""
        self._subscribers.clear()
        self._logger.debug("Cleared all event subscribers")
    
    def clear_event_subscribers(self, event_name: str) -> bool:
        """Remove all subscribers from a specific event
        
        Args:
            event_name: Name of the event to clear
            
        Returns:
            True if event existed and was cleared, False otherwise
        """
        if event_name in self._subscribers:
            del self._subscribers[event_name]
            self._logger.debug(f"Cleared all subscribers for event '{event_name}'")
            return True
        return False


# Global event bus instance
_global_event_bus: Optional[EventBus] = None


def get_event_bus() -> EventBus:
    """Get the global event bus instance (singleton pattern)
    
    Returns:
        The global EventBus instance
    """
    global _global_event_bus
    if _global_event_bus is None:
        _global_event_bus = EventBus()
    return _global_event_bus


def reset_event_bus() -> None:
    """Reset the global event bus (mainly for testing)"""
    global _global_event_bus
    _global_event_bus = None


# Common event names as constants to avoid typos
class Events:
    """Common event names used throughout the application"""
    
    # Navigation events
    NAVIGATION_CHANGED = "navigation.changed"
    PAGE_ACTIVATED = "page.activated"
    PAGE_DEACTIVATED = "page.deactivated"
    
    # Script events
    SCRIPT_STARTED = "script.started"
    SCRIPT_STOPPED = "script.stopped"
    SCRIPT_COMPLETED = "script.completed"
    SCRIPT_ERROR = "script.error"
    SCRIPT_OUTPUT = "script.output"
    
    # UI events
    THEME_CHANGED = "theme.changed"
    FONT_SIZE_CHANGED = "font.size.changed"
    
    # Application events
    APP_CLOSING = "app.closing"
    STATUS_CHANGED = "status.changed"
    
    # Output events
    OUTPUT_CLEARED = "output.cleared"
    OUTPUT_EXPORTED = "output.exported"
