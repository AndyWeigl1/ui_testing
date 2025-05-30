"""
System notification manager for cross-platform desktop notifications
Save this as: services/notification_manager.py
"""

import os
import sys
import logging
import subprocess
from typing import Dict, Optional
from pathlib import Path

# Try to import plyer for cross-platform notifications
try:
    from plyer import notification as plyer_notification

    PLYER_AVAILABLE = True
except ImportError:
    PLYER_AVAILABLE = False


class NotificationManager:
    """Manages system notifications across different platforms"""

    def __init__(self):
        """Initialize the notification manager"""
        self.logger = logging.getLogger(__name__)
        self.notifications_enabled = True
        self.notification_duration = 5  # seconds
        self.silent_notifications = True  # NEW: Disable system notification sounds

        # App info
        self.app_name = "AutoBear Script Runner"
        self.app_icon = self._get_app_icon_path()

        # Determine the best notification method for this platform
        self.notification_backend = self._detect_notification_backend()

        self.logger.info(f"Notification manager initialized with backend: {self.notification_backend}")
        self.logger.info(f"Silent notifications: {self.silent_notifications}")

    def _detect_notification_backend(self) -> str:
        """Detect the best notification backend for the current platform"""
        if PLYER_AVAILABLE:
            return 'plyer'

        if sys.platform.startswith('win'):
            try:
                import win10toast
                return 'win10toast'
            except ImportError:
                return 'windows_fallback'
        elif sys.platform.startswith('darwin'):
            # Check if osascript is available (should be on all macOS systems)
            try:
                subprocess.run(['osascript', '-e', 'display notification "test"'],
                               capture_output=True, check=True)
                return 'osascript'
            except (subprocess.CalledProcessError, FileNotFoundError):
                return 'macos_fallback'
        else:
            # Linux and other Unix-like systems
            try:
                subprocess.run(['notify-send', '--version'],
                               capture_output=True, check=True)
                return 'notify-send'
            except (subprocess.CalledProcessError, FileNotFoundError):
                return 'linux_fallback'

    def _get_app_icon_path(self) -> Optional[str]:
        """Get the path to the application icon"""
        # Try to find the icon in the assets folder
        possible_paths = [
            # "assets/icons/kodiak.png",
            "assets/icons/kodiak.ico",
            "assets/icons/app.png",
            "assets/icons/icon.png",
            "icon.png"
        ]

        for path in possible_paths:
            if os.path.exists(path):
                return os.path.abspath(path)

        return None

    def set_enabled(self, enabled: bool):
        """Enable or disable system notifications"""
        self.notifications_enabled = enabled
        self.logger.info(f"System notifications {'enabled' if enabled else 'disabled'}")

    def set_duration(self, duration: int):
        """Set the notification duration in seconds"""
        self.notification_duration = max(1, min(30, duration))  # Clamp between 1-30 seconds

    def set_silent(self, silent: bool):
        """Enable or disable silent notifications (no system sounds)"""
        self.silent_notifications = silent
        self.logger.info(f"Silent notifications {'enabled' if silent else 'disabled'}")

    def get_available_types(self) -> Dict[str, str]:
        """Get available notification types and their descriptions"""
        return {
            'success': 'Script completed successfully',
            'error': 'Script failed or encountered an error',
            'warning': 'Script stopped or warning occurred',
            'info': 'General information notification',
            'start': 'Script execution started'
        }

    def show_notification(self, title: str, message: str, notification_type: str = 'info'):
        """Show a system notification

        Args:
            title: Notification title
            message: Notification message
            notification_type: Type of notification (success, error, warning, info, start)
        """
        if not self.notifications_enabled:
            return

        try:
            # Choose appropriate icon based on type
            icon_path = self._get_notification_icon(notification_type)

            if self.notification_backend == 'plyer':
                self._show_plyer_notification(title, message, icon_path)
            elif self.notification_backend == 'win10toast':
                self._show_win10toast_notification(title, message, icon_path)
            elif self.notification_backend == 'osascript':
                self._show_osascript_notification(title, message)
            elif self.notification_backend == 'notify-send':
                self._show_notify_send_notification(title, message, notification_type, icon_path)
            else:
                # Fallback methods
                self._show_fallback_notification(title, message, notification_type)

        except Exception as e:
            self.logger.error(f"Error showing notification: {e}")
            # Try fallback
            self._show_fallback_notification(title, message, notification_type)

    def _get_notification_icon(self, notification_type: str) -> Optional[str]:
        """Get appropriate icon for notification type"""
        # For now, use the app icon for all notifications
        # In the future, could have different icons for different types
        return self.app_icon

    def _show_plyer_notification(self, title: str, message: str, icon_path: Optional[str]):
        """Show notification using plyer library"""
        try:
            # Note: plyer doesn't have a direct way to disable sound
            # The system will handle sound based on OS settings
            plyer_notification.notify(
                title=title,
                message=message,
                app_name=self.app_name,
                app_icon=icon_path,
                timeout=self.notification_duration
            )
        except Exception as e:
            self.logger.error(f"Plyer notification error: {e}")
            raise

    def _show_win10toast_notification(self, title: str, message: str, icon_path: Optional[str]):
        """Show notification using win10toast library"""
        try:
            import win10toast
            toaster = win10toast.ToastNotifier()

            # win10toast doesn't have a direct silent option, but we can try to minimize sound
            # by using threaded=True which might reduce OS sound integration
            toaster.show_toast(
                title,
                message,
                icon_path=icon_path,
                duration=self.notification_duration,
                threaded=True
            )
        except Exception as e:
            self.logger.error(f"Win10toast notification error: {e}")
            raise

    def _show_osascript_notification(self, title: str, message: str):
        """Show notification using macOS osascript"""
        try:
            # MODIFIED: Remove sound when silent_notifications is True
            if self.silent_notifications:
                script = f'display notification "{message}" with title "{title}"'
            else:
                script = f'display notification "{message}" with title "{title}" sound name "Default"'

            subprocess.run(['osascript', '-e', script], check=True)
        except Exception as e:
            self.logger.error(f"osascript notification error: {e}")
            raise

    def _show_notify_send_notification(self, title: str, message: str,
                                       notification_type: str, icon_path: Optional[str]):
        """Show notification using Linux notify-send"""
        try:
            cmd = ['notify-send']

            # Add urgency based on type
            if notification_type == 'error':
                cmd.extend(['--urgency', 'critical'])
            elif notification_type == 'warning':
                cmd.extend(['--urgency', 'normal'])
            else:
                cmd.extend(['--urgency', 'low'])

            # Add icon if available
            if icon_path:
                cmd.extend(['--icon', icon_path])

            # Add timeout
            cmd.extend(['--expire-time', str(self.notification_duration * 1000)])

            # MODIFIED: Add hint to suppress sound when silent_notifications is True
            if self.silent_notifications:
                cmd.extend(['--hint', 'string:sound-name:'])  # Empty sound name disables sound

            # Add title and message
            cmd.extend([title, message])

            subprocess.run(cmd, check=True)
        except Exception as e:
            self.logger.error(f"notify-send notification error: {e}")
            raise

    def _show_fallback_notification(self, title: str, message: str, notification_type: str):
        """Fallback notification method using system-specific approaches"""
        try:
            if sys.platform.startswith('win'):
                # Windows fallback using ctypes
                try:
                    import ctypes
                    from ctypes import wintypes

                    # Simple message box as fallback (naturally silent unless user configured otherwise)
                    ctypes.windll.user32.MessageBoxW(
                        0,
                        f"{message}",
                        f"{self.app_name} - {title}",
                        0x40  # MB_ICONINFORMATION
                    )
                except Exception:
                    self.logger.warning(f"Fallback notification: {title} - {message}")

            elif sys.platform.startswith('darwin'):
                # macOS fallback - only use say command if silent notifications is disabled
                if not self.silent_notifications:
                    try:
                        subprocess.run(['say', f"{title}. {message}"], check=True)
                    except Exception:
                        self.logger.warning(f"Fallback notification: {title} - {message}")
                else:
                    self.logger.warning(f"Fallback notification: {title} - {message}")

            else:
                # Linux/Unix fallback - just log
                self.logger.warning(f"Fallback notification: {title} - {message}")

        except Exception as e:
            self.logger.error(f"Fallback notification failed: {e}")

    def test_notification(self, notification_type: str = 'info'):
        """Test a notification of the specified type"""
        test_messages = {
            'success': ("Script Completed", "Your script executed successfully!"),
            'error': ("Script Failed", "Your script encountered an error."),
            'warning': ("Script Warning", "Your script completed with warnings."),
            'info': ("Test Notification", "This is a test notification."),
            'start': ("Script Started", "Your script has begun execution.")
        }

        title, message = test_messages.get(notification_type, test_messages['info'])
        self.show_notification(title, message, notification_type)

    def test_all_notifications(self):
        """Test all notification types with delay between them"""
        import time

        for notif_type in self.get_available_types().keys():
            self.logger.info(f"Testing {notif_type} notification...")
            self.test_notification(notif_type)
            time.sleep(2)  # Brief pause between notifications

    def cleanup(self):
        """Clean up notification resources"""
        # Most notification systems don't require explicit cleanup
        # But this method is here for consistency with other managers
        self.logger.info("Notification manager cleaned up")


# Global instance
_notification_manager = None


def get_notification_manager() -> NotificationManager:
    """Get the global notification manager instance"""
    global _notification_manager
    if _notification_manager is None:
        _notification_manager = NotificationManager()
    return _notification_manager


def reset_notification_manager():
    """Reset the global notification manager (for testing)"""
    global _notification_manager
    if _notification_manager:
        _notification_manager.cleanup()
    _notification_manager = None
