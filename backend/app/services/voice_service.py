"""
Voice Service for JARVIS AI
Handles speech recognition and text-to-speech functionality
"""

import threading
import time
import speech_recognition as sr
import pyttsx3
from typing import Optional, Callable, Dict, Any
from ..core.config import config
from ..core.logging import get_logger
from ..core.exceptions import VoiceError

logger = get_logger(__name__)


class VoiceService:
    """Service for voice recognition and text-to-speech"""

    def __init__(self):
        self.voice_config = config.voice
        self.is_enabled = self.voice_config.enabled
        self.is_listening = False
        self.is_speaking = False

        # Initialize TTS engine if enabled
        self.tts_engine = None
        self.recognizer = None

        if self.is_enabled:
            self._initialize_tts()
            self._initialize_stt()

        logger.info(f"Voice service initialized (enabled: {self.is_enabled})")

    def _initialize_tts(self):
        """Initialize text-to-speech engine"""
        try:
            self.tts_engine = pyttsx3.init()
            self.tts_engine.setProperty('rate', self.voice_config.rate)
            self.tts_engine.setProperty('volume', self.voice_config.volume)
            self.tts_engine.setProperty('pitch', self.voice_config.pitch)

            # Set male voice - specifically David if available
            voices = self.tts_engine.getProperty('voices')
            male_voice_set = False

            # Try to find David voice specifically
            for voice in voices:
                if 'david' in voice.name.lower():
                    self.tts_engine.setProperty('voice', voice.id)
                    logger.info(f"Selected voice: {voice.name}")
                    male_voice_set = True
                    break

            # Fallback: try any male voice
            if not male_voice_set:
                for voice in voices:
                    if 'male' in voice.name.lower() or (hasattr(voice, 'gender') and voice.gender == 'male'):
                        self.tts_engine.setProperty('voice', voice.id)
                        logger.info(f"Selected voice: {voice.name}")
                        male_voice_set = True
                        break

            # Final fallback: use first voice
            if not male_voice_set and voices:
                self.tts_engine.setProperty('voice', voices[0].id)
                logger.info(f"Selected default voice: {voices[0].name}")

        except Exception as e:
            logger.error(f"Failed to initialize TTS engine: {e}")
            self.is_enabled = False

    def _initialize_stt(self):
        """Initialize speech-to-text recognizer"""
        try:
            self.recognizer = sr.Recognizer()
            self.recognizer.energy_threshold = self.voice_config.energy_threshold
            self.recognizer.dynamic_energy_threshold = self.voice_config.dynamic_energy_threshold
        except Exception as e:
            logger.error(f"Failed to initialize STT recognizer: {e}")
            self.is_enabled = False

    def speak(self, text: str, blocking: bool = True) -> bool:
        """Convert text to speech"""
        if not self.is_enabled or not self.tts_engine:
            logger.warning("TTS not available, text not spoken")
            print(f"Jarvis: {text}")  # Still print text
            return False

        try:
            logger.info(f"Speaking: {text[:100]}...")
            print(f"Jarvis: {text}")

            def speak_thread():
                self.is_speaking = True
                try:
                    self.tts_engine.say(text)
                    self.tts_engine.runAndWait()
                except Exception as e:
                    logger.error(f"TTS error: {e}")
                finally:
                    self.is_speaking = False

            if blocking:
                speak_thread()
            else:
                thread = threading.Thread(target=speak_thread)
                thread.daemon = True
                thread.start()

            return True

        except Exception as e:
            logger.error(f"Speech synthesis failed: {e}")
            raise VoiceError(f"Speech synthesis failed: {str(e)}", operation="tts")

    def listen_for_command(self, timeout: float = 5.0,
                          phrase_time_limit: float = None,
                          callback: Optional[Callable[[str], None]] = None) -> Optional[str]:
        """Listen for voice command"""
        if not self.is_enabled or not self.recognizer:
            logger.warning("STT not available, cannot listen")
            return None

        try:
            with sr.Microphone() as source:
                logger.info(f"Listening for command (timeout: {timeout}s)...")
                self.is_listening = True

                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)

                try:
                    audio = self.recognizer.listen(
                        source,
                        timeout=timeout,
                        phrase_time_limit=phrase_time_limit
                    )

                    logger.info("Processing speech...")
                    command = self.recognizer.recognize_google(audio)
                    command = command.strip().lower()

                    logger.info(f"Recognized: {command}")

                    if callback:
                        callback(command)

                    return command

                except sr.WaitTimeoutError:
                    logger.debug("Listening timeout")
                    return None
                except sr.UnknownValueError:
                    logger.debug("Could not understand audio")
                    return None
                except sr.RequestError as e:
                    logger.error(f"Speech recognition service error: {e}")
                    raise VoiceError(f"Speech recognition service error: {str(e)}",
                                   operation="stt")
                finally:
                    self.is_listening = False

        except Exception as e:
            self.is_listening = False
            logger.error(f"Voice recognition failed: {e}")
            raise VoiceError(f"Voice recognition failed: {str(e)}", operation="stt")

    def start_continuous_listening(self, command_callback: Callable[[str], None],
                                 wake_word: str = "jarvis") -> threading.Thread:
        """Start continuous listening with wake word detection"""
        if not self.is_enabled or not self.recognizer:
            raise VoiceError("Voice service not available", operation="continuous_listening")

        def listening_loop():
            logger.info(f"Starting continuous listening (wake word: {wake_word})")
            self.is_listening = True

            try:
                while self.is_listening:
                    with sr.Microphone() as source:
                        try:
                            # Listen for wake word
                            logger.debug("Listening for wake word...")
                            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                            audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=3)

                            # Try to recognize speech
                            try:
                                text = self.recognizer.recognize_google(audio).lower()
                                logger.debug(f"Heard: {text}")

                                # Check for wake word
                                if wake_word.lower() in text:
                                    self.speak("Yes?", blocking=False)
                                    logger.info("Wake word detected, listening for command...")

                                    # Listen for actual command
                                    command_audio = self.recognizer.listen(
                                        source,
                                        timeout=5,
                                        phrase_time_limit=10
                                    )

                                    try:
                                        command = self.recognizer.recognize_google(command_audio)
                                        command = command.strip()
                                        logger.info(f"Command received: {command}")

                                        # Execute callback in separate thread
                                        callback_thread = threading.Thread(
                                            target=command_callback,
                                            args=(command,)
                                        )
                                        callback_thread.daemon = True
                                        callback_thread.start()

                                    except sr.UnknownValueError:
                                        self.speak("Sorry, I didn't catch that.", blocking=False)
                                    except sr.WaitTimeoutError:
                                        logger.debug("Command listening timeout")

                            except sr.UnknownValueError:
                                continue  # No speech detected, continue listening
                            except sr.RequestError as e:
                                logger.error(f"Speech recognition error: {e}")
                                time.sleep(1)

                        except sr.WaitTimeoutError:
                            continue  # Timeout, continue listening

            except Exception as e:
                logger.error(f"Continuous listening error: {e}")
            finally:
                self.is_listening = False

        # Start listening in background thread
        thread = threading.Thread(target=listening_loop)
        thread.daemon = True
        thread.start()

        return thread

    def stop_listening(self):
        """Stop continuous listening"""
        self.is_listening = False
        logger.info("Stopping voice listening")

    def get_available_voices(self) -> list:
        """Get list of available TTS voices"""
        if not self.tts_engine:
            return []

        try:
            voices = []
            for voice in self.tts_engine.getProperty('voices'):
                voices.append({
                    'id': voice.id,
                    'name': voice.name,
                    'languages': voice.languages if hasattr(voice, 'languages') else [],
                    'gender': getattr(voice, 'gender', 'unknown'),
                    'age': getattr(voice, 'age', 'unknown')
                })
            return voices
        except Exception as e:
            logger.error(f"Failed to get voices: {e}")
            return []

    def set_voice(self, voice_id: str) -> bool:
        """Set TTS voice by ID"""
        if not self.tts_engine:
            return False

        try:
            self.tts_engine.setProperty('voice', voice_id)
            logger.info(f"Voice changed to: {voice_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to set voice: {e}")
            return False

    def set_speech_rate(self, rate: int) -> bool:
        """Set speech rate (words per minute)"""
        if not self.tts_engine:
            return False

        try:
            self.tts_engine.setProperty('rate', rate)
            logger.info(f"Speech rate set to: {rate}")
            return True
        except Exception as e:
            logger.error(f"Failed to set speech rate: {e}")
            return False

    def set_volume(self, volume: float) -> bool:
        """Set speech volume (0.0 to 1.0)"""
        if not self.tts_engine:
            return False

        try:
            volume = max(0.0, min(1.0, volume))
            self.tts_engine.setProperty('volume', volume)
            logger.info(f"Volume set to: {volume}")
            return True
        except Exception as e:
            logger.error(f"Failed to set volume: {e}")
            return False

    def get_status(self) -> Dict[str, Any]:
        """Get current voice service status"""
        return {
            "enabled": self.is_enabled,
            "listening": self.is_listening,
            "speaking": self.is_speaking,
            "tts_available": self.tts_engine is not None,
            "stt_available": self.recognizer is not None,
            "current_voice": self._get_current_voice_info(),
            "speech_rate": self.voice_config.rate,
            "volume": self.voice_config.volume,
            "energy_threshold": self.voice_config.energy_threshold
        }

    def _get_current_voice_info(self) -> Dict[str, Any]:
        """Get information about current voice"""
        if not self.tts_engine:
            return {"available": False}

        try:
            current_voice_id = self.tts_engine.getProperty('voice')
            voices = self.get_available_voices()

            for voice in voices:
                if voice['id'] == current_voice_id:
                    return {"available": True, **voice}

            return {"available": True, "id": current_voice_id, "name": "Unknown"}
        except Exception as e:
            logger.error(f"Failed to get current voice info: {e}")
            return {"available": False}

    def test_microphone(self) -> Dict[str, Any]:
        """Test microphone availability and audio levels"""
        if not self.recognizer:
            return {"available": False, "error": "STT not initialized"}

        try:
            with sr.Microphone() as source:
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=1.0)

                # Get energy threshold
                threshold = self.recognizer.energy_threshold
                dynamic_threshold = self.recognizer.dynamic_energy_threshold

                # Test with a short recording
                logger.info("Testing microphone...")
                audio = self.recognizer.listen(source, timeout=2, phrase_time_limit=2)

                return {
                    "available": True,
                    "energy_threshold": threshold,
                    "dynamic_threshold": dynamic_threshold,
                    "audio_duration": len(audio.get_raw_data()) / (audio.sample_rate * 2),
                    "success": True
                }

        except sr.WaitTimeoutError:
            return {
                "available": True,
                "error": "No audio detected within timeout",
                "success": False
            }
        except Exception as e:
            return {
                "available": False,
                "error": str(e),
                "success": False
            }


# Global voice service instance
voice_service = VoiceService()