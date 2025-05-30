"""
Sound manager service for playing audio notifications
Save this as: services/sound_manager.py
"""

import os
import threading
import logging
from typing import Dict, Optional, Callable
from pathlib import Path

# Try to import pygame for cross-platform audio support
try:
    import pygame

    pygame.mixer.init()
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

# Fallback to system-specific sound playing
import sys
import subprocess


class SoundManager:
    """Manages audio notifications for the application"""

    def __init__(self):
        """Initialize the sound manager"""
        self.logger = logging.getLogger(__name__)
        self.sounds_enabled = True
        self.volume = 0.7  # Default volume (0.0 to 1.0)

        # Sound file paths
        self.sounds_dir = Path("assets/sounds")
        self.sound_files = {
            'success': 'success.wav',
            'error': 'error.wav',
            'warning': 'warning.wav',
            'notification': 'notification.wav',
            'start': 'start.wav'
        }

        # Ensure sounds directory exists
        self.sounds_dir.mkdir(parents=True, exist_ok=True)

        # Initialize audio system
        self._initialize_audio()

        # Create default sounds if they don't exist
        self._create_default_sounds()

    def _initialize_audio(self):
        """Initialize the audio system"""
        if PYGAME_AVAILABLE:
            try:
                pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
                self.audio_backend = 'pygame'
                self.logger.info("Audio initialized with pygame")
            except Exception as e:
                self.logger.warning(f"Failed to initialize pygame audio: {e}")
                self.audio_backend = 'system'
        else:
            self.audio_backend = 'system'
            self.logger.info("Using system audio backend (pygame not available)")

    def _create_default_sounds(self):
        """Create simple default sounds if sound files don't exist"""
        if not PYGAME_AVAILABLE:
            return

        # Only create sounds if they don't exist
        for sound_type, filename in self.sound_files.items():
            sound_path = self.sounds_dir / filename
            if not sound_path.exists():
                self._generate_simple_tone(sound_path, sound_type)

    def _generate_simple_tone(self, filepath: Path, sound_type: str):
        """Generate a simple tone for the given sound type"""
        if not PYGAME_AVAILABLE:
            return

        try:
            import numpy as np

            # Sound parameters
            sample_rate = 22050
            duration = 0.5  # 0.5 seconds

            # Different frequencies for different sound types
            frequencies = {
                'success': [523, 659, 784],  # C-E-G major chord
                'error': [220, 185],  # Low A, then lower
                'warning': [440, 440, 440],  # A note repeated
                'notification': [523, 659],  # C-E
                'start': [392, 523]  # G-C
            }

            freq_list = frequencies.get(sound_type, [440])

            # Generate the tone
            samples = []
            for i, freq in enumerate(freq_list):
                t = np.linspace(0, duration / len(freq_list), int(sample_rate * duration / len(freq_list)))
                # Create a sine wave with fade in/out
                wave = np.sin(2 * np.pi * freq * t)

                # Apply envelope (fade in/out)
                envelope = np.ones_like(wave)
                fade_samples = int(0.05 * len(wave))  # 5% fade
                envelope[:fade_samples] = np.linspace(0, 1, fade_samples)
                envelope[-fade_samples:] = np.linspace(1, 0, fade_samples)

                wave *= envelope * 0.3  # Reduce volume
                samples.extend(wave)

            # Convert to 16-bit integers
            samples = np.array(samples)
            samples = (samples * 32767).astype(np.int16)

            # Save as WAV file
            from scipy.io import wavfile
            wavfile.write(str(filepath), sample_rate, samples)

            self.logger.debug(f"Generated default sound: {filepath}")

        except ImportError:
            # If numpy/scipy not available, create a very simple beep
            self._create_simple_beep(filepath, sound_type)
        except Exception as e:
            self.logger.warning(f"Could not generate tone for {sound_type}: {e}")

    def _create_simple_beep(self, filepath: Path, sound_type: str):
        """Create a very simple beep sound"""
        try:
            # Create a simple square wave
            import wave
            import struct
            import math

            sample_rate = 22050
            duration = 0.3
            frequency = {'success': 800, 'error': 200, 'warning': 600, 'notification': 700, 'start': 500}[sound_type]

            with wave.open(str(filepath), 'w') as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 2 bytes per sample
                wav_file.setframerate(sample_rate)

                for i in range(int(sample_rate * duration)):
                    value = int(16383 * math.sin(2 * math.pi * frequency * i / sample_rate))
                    wav_file.writeframesraw(struct.pack('<h', value))

            self.logger.debug(f"Generated simple beep: {filepath}")

        except Exception as e:
            self.logger.warning(f"Could not create simple beep for {sound_type}: {e}")

    def set_enabled(self, enabled: bool):
        """Enable or disable sound notifications"""
        self.sounds_enabled = enabled
        self.logger.info(f"Sound notifications {'enabled' if enabled else 'disabled'}")

    def set_volume(self, volume: float):
        """Set the volume for sound notifications (0.0 to 1.0)"""
        self.volume = max(0.0, min(1.0, volume))
        if PYGAME_AVAILABLE and self.audio_backend == 'pygame':
            pygame.mixer.music.set_volume(self.volume)

    def get_available_sounds(self) -> Dict[str, str]:
        """Get a dictionary of available sound types and their descriptions"""
        return {
            'success': 'Script completed successfully',
            'error': 'Script failed or encountered an error',
            'warning': 'Script stopped or warning occurred',
            'notification': 'General notification',
            'start': 'Script execution started'
        }

    def play_sound(self, sound_type: str, blocking: bool = False):
        """Play a sound notification

        Args:
            sound_type: Type of sound to play ('success', 'error', 'warning', etc.)
            blocking: Whether to wait for the sound to finish playing
        """
        if not self.sounds_enabled:
            return

        if blocking:
            self._play_sound_sync(sound_type)
        else:
            # Play sound in a separate thread to avoid blocking UI
            threading.Thread(
                target=self._play_sound_sync,
                args=(sound_type,),
                daemon=True
            ).start()

    def _play_sound_sync(self, sound_type: str):
        """Play sound synchronously"""
        try:
            sound_file = self.sound_files.get(sound_type)
            if not sound_file:
                self.logger.warning(f"Unknown sound type: {sound_type}")
                return

            sound_path = self.sounds_dir / sound_file

            if not sound_path.exists():
                self.logger.warning(f"Sound file not found: {sound_path}")
                # Try to create a system beep as fallback
                self._system_beep(sound_type)
                return

            if self.audio_backend == 'pygame' and PYGAME_AVAILABLE:
                self._play_with_pygame(sound_path)
            else:
                self._play_with_system(sound_path)

        except Exception as e:
            self.logger.error(f"Error playing sound {sound_type}: {e}")
            # Fallback to system beep
            self._system_beep(sound_type)

    def _play_with_pygame(self, sound_path: Path):
        """Play sound using pygame"""
        try:
            sound = pygame.mixer.Sound(str(sound_path))
            sound.set_volume(self.volume)
            sound.play()

            # Wait for sound to finish if needed
            while pygame.mixer.get_busy():
                pygame.time.wait(10)

        except Exception as e:
            self.logger.error(f"Pygame sound error: {e}")
            raise

    def _play_with_system(self, sound_path: Path):
        """Play sound using system commands"""
        try:
            if sys.platform.startswith('win'):
                # Windows
                import winsound
                winsound.PlaySound(str(sound_path), winsound.SND_FILENAME)
            elif sys.platform.startswith('darwin'):
                # macOS
                subprocess.run(['afplay', str(sound_path)], check=True)
            else:
                # Linux and others
                # Try multiple players
                players = ['aplay', 'paplay', 'play', 'ffplay']
                for player in players:
                    try:
                        subprocess.run([player, str(sound_path)],
                                       check=True,
                                       stdout=subprocess.DEVNULL,
                                       stderr=subprocess.DEVNULL)
                        break
                    except (subprocess.CalledProcessError, FileNotFoundError):
                        continue
                else:
                    raise Exception("No suitable audio player found")

        except Exception as e:
            self.logger.error(f"System sound error: {e}")
            raise

    def _system_beep(self, sound_type: str):
        """Create a system beep as fallback"""
        try:
            if sys.platform.startswith('win'):
                import winsound
                # Different beep patterns for different types
                if sound_type == 'success':
                    winsound.Beep(800, 200)
                    winsound.Beep(1000, 200)
                elif sound_type == 'error':
                    winsound.Beep(200, 500)
                else:
                    winsound.Beep(600, 300)
            else:
                # Unix systems - print bell character
                print('\a', end='', flush=True)

        except Exception as e:
            self.logger.error(f"System beep failed: {e}")

    def test_sound(self, sound_type: str):
        """Test a specific sound type"""
        self.play_sound(sound_type, blocking=False)

    def test_all_sounds(self):
        """Test all available sounds with delay between them"""
        import time

        for sound_type in self.sound_files.keys():
            self.logger.info(f"Testing {sound_type} sound...")
            self.play_sound(sound_type, blocking=True)
            time.sleep(0.5)  # Brief pause between sounds

    def cleanup(self):
        """Clean up audio resources"""
        if PYGAME_AVAILABLE and self.audio_backend == 'pygame':
            try:
                pygame.mixer.quit()
            except Exception as e:
                self.logger.error(f"Error cleaning up audio: {e}")


# Global instance
_sound_manager = None


def get_sound_manager() -> SoundManager:
    """Get the global sound manager instance"""
    global _sound_manager
    if _sound_manager is None:
        _sound_manager = SoundManager()
    return _sound_manager


def reset_sound_manager():
    """Reset the global sound manager (for testing)"""
    global _sound_manager
    if _sound_manager:
        _sound_manager.cleanup()
    _sound_manager = None