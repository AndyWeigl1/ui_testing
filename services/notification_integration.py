"""
System notification integration service - connects notification manager to application events
Save this as: services/notification_integration.py
"""

import logging
from typing import Dict, Any, Optional
from utils.event_bus import get_event_bus, Events
from utils.state_manager import get_state_manager
from services.notification_manager import get_notification_manager


class NotificationIntegration:
    """Integrates system notifications with application events"""

    def __init__(self):
        """Initialize the notification integration service"""
        self.logger = logging.getLogger(__name__)

        # Get managers
        self.event_bus = get_event_bus()
        self.state_manager = get_state_manager()
        self.notification_manager = get_notification_manager()

        # Setup event subscriptions
        self.setup_event_subscriptions()

        # Load initial settings
        self.load_notification_settings()

    def setup_event_subscriptions(self):
        """Subscribe to relevant application events"""
        # Script execution events
        self.event_bus.subscribe(Events.SCRIPT_STARTED, self.on_script_started)
        self.event_bus.subscribe(Events.SCRIPT_COMPLETED, self.on_script_completed)
        self.event_bus.subscribe(Events.SCRIPT_ERROR, self.on_script_error)
        self.event_bus.subscribe(Events.SCRIPT_STOPPED, self.on_script_stopped)

        # Settings change events
        self.event_bus.subscribe('settings.saved', self.on_settings_changed)
        self.event_bus.subscribe('state.changed', self.on_state_changed)

    def load_notification_settings(self):
        """Load notification settings from state manager"""
        try:
            # Get notification preferences
            notifications_enabled = self.state_manager.get('notifications_enabled', True)
            notification_duration = self.state_manager.get('notification_duration', 5)

            # Apply to notification manager
            self.notification_manager.set_enabled(notifications_enabled)
            self.notification_manager.set_duration(notification_duration)

            self.logger.info(
                f"Notification settings loaded: enabled={notifications_enabled}, duration={notification_duration}s")

        except Exception as e:
            self.logger.error(f"Error loading notification settings: {e}")

    def should_show_notification(self, notification_type: str) -> bool:
        """Check if a specific notification type should be shown"""
        # Check if notifications are globally enabled
        if not self.state_manager.get('notifications_enabled', True):
            return False

        # Check if this specific notification type is enabled
        setting_key = f'notification_{notification_type}'
        return self.state_manager.get(setting_key, True)

    def format_script_name(self, script_name: str) -> str:
        """Format script name for display in notifications"""
        # Remove file extensions and clean up the name
        if script_name:
            # Remove common extensions
            for ext in ['.py', '.pyw', '.bat', '.sh']:
                if script_name.lower().endswith(ext):
                    script_name = script_name[:-len(ext)]
                    break

            # Replace underscores with spaces and title case
            script_name = script_name.replace('_', ' ').title()

        return script_name or "Script"

    def on_script_started(self, data: Dict[str, Any]):
        """Handle script started event"""
        try:
            if self.should_show_notification('script_start'):
                script_name = self.format_script_name(data.get('script_name', 'Script'))

                title = "Script Started"
                message = f"{script_name} has begun execution"

                self.notification_manager.show_notification(title, message, 'start')
                self.logger.debug(f"Showed script start notification for: {script_name}")

        except Exception as e:
            self.logger.error(f"Error showing script start notification: {e}")

    def on_script_completed(self, data: Dict[str, Any]):
        """Handle script completed event"""
        try:
            # Determine if it was successful or not
            status = data.get('status', 'unknown')
            exit_code = data.get('exit_code', 0)
            script_name = self.format_script_name(data.get('script_name', 'Script'))

            if status == 'success' or exit_code == 0:
                if self.should_show_notification('script_success'):
                    title = "Script Completed Successfully"
                    message = f"{script_name} finished without errors"

                    self.notification_manager.show_notification(title, message, 'success')
                    self.logger.debug(f"Showed script success notification for: {script_name}")
            else:
                if self.should_show_notification('script_error'):
                    title = "Script Failed"
                    message = f"{script_name} encountered an error (exit code: {exit_code})"

                    self.notification_manager.show_notification(title, message, 'error')
                    self.logger.debug(f"Showed script error notification for: {script_name}")

        except Exception as e:
            self.logger.error(f"Error showing script completion notification: {e}")

    def on_script_error(self, data: Dict[str, Any]):
        """Handle script error event"""
        try:
            if self.should_show_notification('script_error'):
                script_name = self.format_script_name(data.get('script_name', 'Script'))
                exit_code = data.get('exit_code', 'Unknown')
                error_msg = data.get('error', '')

                title = "Script Error"

                # Create informative message
                if error_msg:
                    # Truncate long error messages for notification
                    if len(error_msg) > 100:
                        error_msg = error_msg[:97] + "..."
                    message = f"{script_name} failed: {error_msg}"
                else:
                    message = f"{script_name} failed with exit code {exit_code}"

                self.notification_manager.show_notification(title, message, 'error')
                self.logger.debug(f"Showed script error notification for: {script_name}")

        except Exception as e:
            self.logger.error(f"Error showing script error notification: {e}")

    def on_script_stopped(self, data: Dict[str, Any]):
        """Handle script stopped event"""
        try:
            reason = data.get('reason', 'unknown')
            script_name = self.format_script_name(data.get('script_name', 'Script'))

            if reason == 'user_request':
                # User manually stopped - show warning notification
                if self.should_show_notification('script_warning'):
                    title = "Script Stopped"
                    message = f"{script_name} was stopped by user"

                    self.notification_manager.show_notification(title, message, 'warning')
                    self.logger.debug(f"Showed script stopped notification for: {script_name}")
            else:
                # Script stopped due to error - treat as error
                if self.should_show_notification('script_error'):
                    title = "Script Terminated"
                    message = f"{script_name} was terminated unexpectedly"

                    self.notification_manager.show_notification(title, message, 'error')
                    self.logger.debug(f"Showed script termination notification for: {script_name}")

        except Exception as e:
            self.logger.error(f"Error showing script stopped notification: {e}")

    def on_settings_changed(self, data: Dict[str, Any]):
        """Handle settings change event"""
        try:
            settings = data.get('settings', {})

            # Update notification manager settings
            if 'notifications_enabled' in settings:
                self.notification_manager.set_enabled(settings['notifications_enabled'])

            if 'notification_duration' in settings:
                self.notification_manager.set_duration(settings['notification_duration'])

            self.logger.debug("Updated notification settings from settings change")

        except Exception as e:
            self.logger.error(f"Error updating notification settings: {e}")

    def on_state_changed(self, data: Dict[str, Any]):
        """Handle individual state changes"""
        try:
            key = data.get('key')
            value = data.get('value')

            if key == 'notifications_enabled':
                self.notification_manager.set_enabled(value)
            elif key == 'notification_duration':
                self.notification_manager.set_duration(value)

        except Exception as e:
            self.logger.error(f"Error handling state change for notifications: {e}")

    def show_test_notification(self, notification_type: str = 'info'):
        """Show a test notification of the specified type"""
        self.notification_manager.test_notification(notification_type)

    def test_integration(self):
        """Test the notification integration by simulating events"""
        self.logger.info("Testing notification integration...")

        # Test script start
        self.on_script_started({'script_name': 'test_script.py'})

        # Wait a bit then test success
        import time
        time.sleep(2)
        self.on_script_completed({
            'status': 'success',
            'exit_code': 0,
            'script_name': 'test_script.py'
        })

        # Wait a bit then test error
        time.sleep(2)
        self.on_script_error({
            'exit_code': 1,
            'error': 'Test error message',
            'script_name': 'test_script.py'
        })

        self.logger.info("Notification integration test complete")

    def cleanup(self):
        """Clean up resources"""
        try:
            # Unsubscribe from events
            self.event_bus.unsubscribe(Events.SCRIPT_STARTED, self.on_script_started)
            self.event_bus.unsubscribe(Events.SCRIPT_COMPLETED, self.on_script_completed)
            self.event_bus.unsubscribe(Events.SCRIPT_ERROR, self.on_script_error)
            self.event_bus.unsubscribe(Events.SCRIPT_STOPPED, self.on_script_stopped)
            self.event_bus.unsubscribe('settings.saved', self.on_settings_changed)
            self.event_bus.unsubscribe('state.changed', self.on_state_changed)

            # Clean up notification manager
            self.notification_manager.cleanup()

            self.logger.info("Notification integration cleaned up")

        except Exception as e:
            self.logger.error(f"Error during notification integration cleanup: {e}")


# Global instance
_notification_integration = None


def get_notification_integration() -> NotificationIntegration:
    """Get the global notification integration instance"""
    global _notification_integration
    if _notification_integration is None:
        _notification_integration = NotificationIntegration()
    return _notification_integration


def initialize_notification_integration():
    """Initialize the notification integration service"""
    get_notification_integration()


def cleanup_notification_integration():
    """Clean up the notification integration service"""
    global _notification_integration
    if _notification_integration:
        _notification_integration.cleanup()
        _notification_integration = None