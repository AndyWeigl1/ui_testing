"""
Sound integration service - connects sound manager to application events
Save this as: services/sound_integration.py
"""

import logging
from typing import Dict, Any, Optional
from utils.event_bus import get_event_bus, Events
from utils.state_manager import get_state_manager
from services.sound_manager import get_sound_manager


class SoundIntegration:
    """Integrates sound notifications with application events"""

    def __init__(self):
        """Initialize the sound integration service"""
        self.logger = logging.getLogger(__name__)

        # Get managers
        self.event_bus = get_event_bus()
        self.state_manager = get_state_manager()
        self.sound_manager = get_sound_manager()

        # Setup event subscriptions
        self.setup_event_subscriptions()

        # Load initial settings
        self.load_sound_settings()

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

    def load_sound_settings(self):
        """Load sound settings from state manager"""
        try:
            # Get sound preferences
            sounds_enabled = self.state_manager.get('sounds_enabled', True)
            sound_volume = self.state_manager.get('sound_volume', 0.7)

            # Apply to sound manager
            self.sound_manager.set_enabled(sounds_enabled)
            self.sound_manager.set_volume(sound_volume)

            self.logger.info(f"Sound settings loaded: enabled={sounds_enabled}, volume={sound_volume}")

        except Exception as e:
            self.logger.error(f"Error loading sound settings: {e}")

    def should_play_sound(self, sound_type: str) -> bool:
        """Check if a specific sound type should be played"""
        # Check if sounds are globally enabled
        if not self.state_manager.get('sounds_enabled', True):
            return False

        # Check if this specific sound type is enabled
        setting_key = f'sound_{sound_type}'
        return self.state_manager.get(setting_key, True)

    def on_script_started(self, data: Dict[str, Any]):
        """Handle script started event"""
        try:
            if self.should_play_sound('script_start'):
                self.sound_manager.play_sound('start')
                self.logger.debug("Played script start sound")

        except Exception as e:
            self.logger.error(f"Error playing script start sound: {e}")

    def on_script_completed(self, data: Dict[str, Any]):
        """Handle script completed event"""
        try:
            # Determine if it was successful or not
            status = data.get('status', 'unknown')
            exit_code = data.get('exit_code', 0)

            if status == 'success' or exit_code == 0:
                if self.should_play_sound('script_success'):
                    self.sound_manager.play_sound('success')
                    self.logger.debug("Played script success sound")
            else:
                if self.should_play_sound('script_error'):
                    self.sound_manager.play_sound('error')
                    self.logger.debug("Played script error sound")

        except Exception as e:
            self.logger.error(f"Error playing script completion sound: {e}")

    def on_script_error(self, data: Dict[str, Any]):
        """Handle script error event"""
        try:
            if self.should_play_sound('script_error'):
                self.sound_manager.play_sound('error')
                self.logger.debug("Played script error sound")

        except Exception as e:
            self.logger.error(f"Error playing script error sound: {e}")

    def on_script_stopped(self, data: Dict[str, Any]):
        """Handle script stopped event"""
        try:
            # For user-stopped scripts, we might want a different sound or no sound
            reason = data.get('reason', 'unknown')

            if reason == 'user_request':
                # User manually stopped - could play a neutral sound
                if self.should_play_sound('script_error'):  # Reuse error sound for now
                    self.sound_manager.play_sound('warning')
                    self.logger.debug("Played script stopped sound")
            else:
                # Script stopped due to error
                if self.should_play_sound('script_error'):
                    self.sound_manager.play_sound('error')
                    self.logger.debug("Played script error sound")

        except Exception as e:
            self.logger.error(f"Error playing script stopped sound: {e}")

    def on_settings_changed(self, data: Dict[str, Any]):
        """Handle settings change event"""
        try:
            settings = data.get('settings', {})

            # Update sound manager settings
            if 'sounds_enabled' in settings:
                self.sound_manager.set_enabled(settings['sounds_enabled'])

            if 'sound_volume' in settings:
                self.sound_manager.set_volume(settings['sound_volume'])

            self.logger.debug("Updated sound settings from settings change")

        except Exception as e:
            self.logger.error(f"Error updating sound settings: {e}")

    def on_state_changed(self, data: Dict[str, Any]):
        """Handle individual state changes"""
        try:
            key = data.get('key')
            value = data.get('value')

            if key == 'sounds_enabled':
                self.sound_manager.set_enabled(value)
            elif key == 'sound_volume':
                self.sound_manager.set_volume(value)

        except Exception as e:
            self.logger.error(f"Error handling state change for sound: {e}")

    def test_integration(self):
        """Test the sound integration by simulating events"""
        self.logger.info("Testing sound integration...")

        # Test script start
        self.on_script_started({'script_name': 'test_script'})

        # Wait a bit then test success
        import time
        time.sleep(1)
        self.on_script_completed({'status': 'success', 'exit_code': 0})

        # Wait a bit then test error
        time.sleep(1)
        self.on_script_error({'exit_code': 1, 'error': 'Test error'})

        self.logger.info("Sound integration test complete")

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

            self.logger.info("Sound integration cleaned up")

        except Exception as e:
            self.logger.error(f"Error during sound integration cleanup: {e}")


# Global instance
_sound_integration = None


def get_sound_integration() -> SoundIntegration:
    """Get the global sound integration instance"""
    global _sound_integration
    if _sound_integration is None:
        _sound_integration = SoundIntegration()
    return _sound_integration


def initialize_sound_integration():
    """Initialize the sound integration service"""
    get_sound_integration()


def cleanup_sound_integration():
    """Clean up the sound integration service"""
    global _sound_integration
    if _sound_integration:
        _sound_integration.cleanup()
        _sound_integration = None