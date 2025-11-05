import os
import time
import threading
import json
import queue
import pyttsx3
from dotenv import load_dotenv
from vosk import Model, KaldiRecognizer
import pyaudio
from gtts import gTTS
from playsound import playsound
import re
import uuid

load_dotenv()

class VoiceEngine:
    def __init__(self, wake_word="jarvis", wake_word_activation_callback=None, transcript_callback=None):
        self.wake_word = wake_word.lower()
        self.wake_word_activation_callback = wake_word_activation_callback
        self.transcript_callback = transcript_callback
        self.tts_engine = self._init_tts()

        # --- Audio & Recognition defaults ---
        self.audio_interface = None
        self.stream = None
        self.CHUNK = 8192
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 16000
        self.voice_available = False
        
        # --- Vosk Initialization ---
        self.vosk_model = self._load_vosk_model("vosk-model-small-en-us-0.15")
        if not self.vosk_model:
            print("Error: English Vosk model not found. Voice input is disabled.")
        else:
            try:
                self.audio_interface = pyaudio.PyAudio()
                self.voice_available = True
            except Exception as e:
                print(f"Failed to initialise audio interface: {e}")
                self.audio_interface = None
                self.voice_available = False

        # --- Threading and State ---
        self._stop_listening = threading.Event()
        self.voice_thread = None
        self.is_awake = False
        self.command_timeout_thread = None
        self.temp_audio_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "temp_audio")
        os.makedirs(self.temp_audio_dir, exist_ok=True)

    def _load_vosk_model(self, model_name: str):
        """Loads a Vosk model from the project directory."""
        model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), model_name)
        if not os.path.exists(model_path):
            print(f"Model path does not exist: {model_path}")
            return None
        try:
            return Model(model_path)
        except Exception as e:
            print(f"Failed to load Vosk model {model_name}: {e}")
            return None

    def _init_tts(self):
        """Initializes the pyttsx3 engine."""
        try:
            engine = pyttsx3.init()
            rate = int(os.getenv('SPEECH_RATE', '180'))
            engine.setProperty('rate', rate)
            engine.setProperty('volume', 0.9)
            return engine
        except Exception as e:
            print(f"Failed to initialize TTS engine: {e}")
            return None

    def speak(self, text: str):
        """
        Speaks the given text. Uses local TTS for English and gTTS for other languages if needed.
        This now runs in a thread to avoid blocking the main application.
        """
        # Update display to show "Speaking..."
        try:
            from actuators.display import display
            display.clear()
            display.write_text("Speaking...", row=0, col=3)
        except:
            pass
        
        if not self.tts_engine:
            print(f"TTS UNAVAILABLE: {text}")
            return
        
        # Simple check for non-ASCII to decide on gTTS, can be improved.
        is_complex_text = not all(ord(c) < 128 for c in text)

        if is_complex_text:
            threading.Thread(target=self._speak_gtts, args=(text, 'en'), daemon=True).start()
        else:
            threading.Thread(target=self._speak_pyttsx3, args=(text,), daemon=True).start()

    def _speak_pyttsx3(self, text: str):
        """Handles speaking with the local pyttsx3 engine."""
        try:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except Exception as e:
            print(f"pyttsx3 error: {e}")

    def _speak_gtts(self, text: str, lang: str):
        """Handles speaking with Google Text-to-Speech by saving to a temp file."""
        try:
            tts = gTTS(text=text, lang=lang, slow=False)
            temp_file = os.path.join(self.temp_audio_dir, f"temp_{uuid.uuid4()}.mp3")
            tts.save(temp_file)
            playsound(temp_file)
            os.remove(temp_file)
        except Exception as e:
            print(f"gTTS error: {e}")
            self._speak_pyttsx3("I am having trouble with my voice synthesis module.")

    def _listening_loop(self):
        """
        The core loop that continuously listens to the microphone stream.
        It switches between wake word detection and command recognition.
        """
        if not self.audio_interface:
            print("Audio interface unavailable; listening loop aborted.")
            return
        try:
            self.stream = self.audio_interface.open(
                format=self.FORMAT, channels=self.CHANNELS, rate=self.RATE,
                input=True, frames_per_buffer=self.CHUNK
            )
            print("Microphone stream opened. Listening...")
        except Exception as e:
            print(f"Failed to open microphone stream: {e}")
            # In a real UI app, you'd send this error to the UI queue.
            return

        recognizer = KaldiRecognizer(self.vosk_model, self.RATE)
        
        while not self._stop_listening.is_set():
            try:
                data = self.stream.read(self.CHUNK, exception_on_overflow=False)
                
                if recognizer.AcceptWaveform(data):
                    result_json = json.loads(recognizer.Result())
                    text = result_json.get('text', '').lower()

                    if self.is_awake:
                        if text and self.transcript_callback:
                            # We have a command, process it.
                            self.transcript_callback(text)
                            self.go_to_sleep()
                    elif self.wake_word in text:
                        # Wake word detected.
                        self.activate_listening()
                else:
                    partial_result_json = json.loads(recognizer.PartialResult())
                    partial_text = partial_result_json.get('partial', '').lower()
                    if not self.is_awake and self.wake_word in partial_text:
                        self.activate_listening()

            except Exception as e:
                print(f"Error in listening loop: {e}")
                break

        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        print("Microphone stream closed.")

    def activate_listening(self):
        """Called when the wake word is detected or when manually activated."""
        if self.is_awake:
            return # Already awake
            
        self.is_awake = True
        if self.wake_word_activation_callback:
            self.wake_word_activation_callback()

        # Cancel any existing timeout thread
        if self.command_timeout_thread and self.command_timeout_thread.is_alive():
            self.command_timeout_thread.cancel()

        # Set a timeout to go back to sleep if no command is heard
        self.command_timeout_thread = threading.Timer(8.0, self.go_to_sleep)
        self.command_timeout_thread.start()

    def go_to_sleep(self):
        """Puts Jarvis back into standby (wake-word-only) mode."""
        if not self.is_awake:
            return
            
        self.is_awake = False
        print("Going back to sleep mode.")
        # Optionally, provide feedback to the user.
        # self.speak("Going back to sleep.")

    def start(self):
        """Starts the voice engine in a background thread."""
        if not self.voice_available:
            print("Voice engine unavailable; start() ignored.")
            return
        if self.voice_thread is None or not self.voice_thread.is_alive():
            self._stop_listening.clear()
            self.voice_thread = threading.Thread(target=self._listening_loop, daemon=True)
            self.voice_thread.start()
            print("Vosk Voice Engine started.")

    def stop(self):
        """Stops the voice engine."""
        self._stop_listening.set()
        if self.command_timeout_thread:
            self.command_timeout_thread.cancel()
        if self.voice_thread and self.voice_thread.is_alive():
            self.voice_thread.join(timeout=2)
        if self.stream:
            try:
                self.stream.stop_stream()
                self.stream.close()
            except Exception:
                pass
            finally:
                self.stream = None
        if self.audio_interface:
            try:
                self.audio_interface.terminate()
            except Exception:
                pass
            finally:
                self.audio_interface = None
        print("Vosk Voice Engine stopped.")

def list_audio_devices():
    """Prints all available audio input devices to the console."""
    print("="*30)
    print("Available Microphone Devices (for reference, not used by Vosk directly):")
    try:
        p = pyaudio.PyAudio()
        for i in range(p.get_device_count()):
            dev = p.get_device_info_by_index(i)
            if dev['maxInputChannels'] > 0:
                print(f'Device Index {i}: "{dev["name"]}"')
        p.terminate()
    except Exception as e:
        print(f"Could not list microphones: {e}")
    print("="*30)
    print("To use a specific microphone, set MICROPHONE_INDEX in your .env file.")
    print("="*30)

if __name__ == '__main__':
    # A simple test to demonstrate the VoiceEngine
    list_audio_devices()
    
    def handle_wake_word():
        """Callback function for when the wake word is detected."""
        print("\nWake word detected!")
        engine = VoiceEngine()
        command = engine.listen_for_command()
        if command:
            print(f"Command captured: '{command}'")
            if "stop" in command:
                engine.speak("Shutting down test.")
                engine.stop()
            else:
                engine.speak(f"I heard you say: {command}")
        else:
            print("No command was captured.")

    # Initialize and start the engine
    try:
        mic_index = int(os.getenv("MICROPHONE_INDEX"))
    except (ValueError, TypeError):
        mic_index = None

    main_engine = VoiceEngine(mic_index=mic_index)
    main_engine.start(on_wake_word=handle_wake_word)

    try:
        # Keep the main thread alive to let the background thread listen
        while main_engine.voice_thread.is_alive():
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping engine via keyboard interrupt.")
    finally:
        main_engine.stop()
        print("Test finished.")

