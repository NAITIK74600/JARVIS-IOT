import os
import time
import threading
import json
import queue
import shutil
import subprocess
import tempfile
import traceback
try:
    import pyttsx3
except ImportError:
    pyttsx3 = None  # Optional - fallback TTS engine
from dotenv import load_dotenv
from vosk import Model, KaldiRecognizer
import pyaudio
from gtts import gTTS
from playsound import playsound
import re
import uuid

load_dotenv()

class VoiceEngine:
    def __init__(self, wake_word=None, wake_word_activation_callback=None, transcript_callback=None):
        self.wake_word = wake_word.lower() if wake_word else None  # None = no wake word needed
        self.wake_word_activation_callback = wake_word_activation_callback
        self.transcript_callback = transcript_callback
        self.tts_backend = None  # 'piper', 'pyttsx3', or 'gtts'
        self.piper_model_path = None
        self.piper_config_path = None
        self.piper_speaker_id = None
        self.tts_engine = self._init_tts()
        
        # Keep reference for pyttsx3 if available for fast local TTS
        self.pyttsx3_engine = self.tts_engine if self.tts_backend == 'pyttsx3' else None
        
        # Speech synchronization
        self._speech_lock = threading.Lock()
        self._is_speaking = False
        
        # Continuous listening mode (no wake word required)
        self.continuous_mode = (wake_word is None)

        # --- Audio & Recognition defaults ---
        self.audio_interface = None
        self.stream = None
        self.CHUNK = 8192  # Increased for better noise handling and recognition
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 16000
        self.voice_available = False
        
        # Microphone gain/sensitivity settings - OPTIMIZED FOR BETTER RECOGNITION
        self.INPUT_GAIN = 2.0  # Increased to 2x boost for better pickup
        self.NOISE_THRESHOLD = 200  # Reduced threshold for better voice detection (was 500)
        self.SILENCE_LIMIT = 2  # Seconds of silence before processing
        self.MIN_PHRASE_LENGTH = 0.3  # Minimum phrase duration in seconds
        
        # --- Vosk Initialization ---
        self.microphone_index = None

        self.vosk_model = self._load_vosk_model("vosk-model-small-en-us-0.15")
        if not self.vosk_model:
            print("Error: English Vosk model not found. Voice input is disabled.")
        else:
            try:
                self.audio_interface = pyaudio.PyAudio()
                self.microphone_index = self._resolve_microphone_index(self.audio_interface)
                if self.microphone_index is None:
                    print("No microphone input device detected. Voice input is disabled.")
                else:
                    print(f"Using microphone index {self.microphone_index} for wake word detection.")
                self.voice_available = self.microphone_index is not None
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
        
        # Audio cache for common phrases (instant playback)
        self.audio_cache_dir = os.path.join(self.temp_audio_dir, "cache")
        os.makedirs(self.audio_cache_dir, exist_ok=True)
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

    def _resolve_microphone_index(self, audio_interface: pyaudio.PyAudio):
        """
        Determines which microphone index to use for listening.
        Prioritizes Bluetooth devices (like Mini Boost 4) and PulseAudio.
        """
        env_index = os.getenv("MICROPHONE_INDEX")
        if env_index is not None:
            try:
                candidate = int(env_index)
                info = audio_interface.get_device_info_by_index(candidate)
                print(f"[VOICE] Using microphone from .env: {info.get('name')}")
                return candidate
            except Exception:
                print(f"Invalid MICROPHONE_INDEX '{env_index}' in .env. Falling back to auto-detection.")

        # Priority order: Bluetooth > PulseAudio > Others
        bluetooth_index = None
        pulse_index = None
        fallback_index = None
        
        try:
            device_count = audio_interface.get_device_count()
            print(f"[VOICE] Scanning {device_count} audio devices for microphone...")
            
            for i in range(device_count):
                info = audio_interface.get_device_info_by_index(i)
                name = info.get('name', '').lower()
                max_input = info.get('maxInputChannels', 0)
                
                if max_input > 0:
                    print(f"[VOICE] Found input device {i}: {info.get('name')} ({max_input} channels)")
                    
                    # Priority 1: Bluetooth devices (Mini Boost 4)
                    if 'bluez' in name or 'bluetooth' in name:
                        bluetooth_index = i
                        print(f"[VOICE] ✓ Bluetooth microphone detected: {info.get('name')}")
                    
                    # Priority 2: PulseAudio
                    elif 'pulse' in name:
                        if pulse_index is None:
                            pulse_index = i
                            print(f"[VOICE] ✓ PulseAudio microphone detected: {info.get('name')}")
                    
                    # Priority 3: Any other input device
                    elif fallback_index is None:
                        fallback_index = i
                        
        except Exception as e:
            print(f"[VOICE] Error enumerating microphone devices: {e}")
            return None

        # Select microphone in priority order
        if bluetooth_index is not None:
            selected = bluetooth_index
            print(f"[VOICE] 🎤 Selected: Bluetooth microphone (index {selected})")
        elif pulse_index is not None:
            selected = pulse_index
            print(f"[VOICE] 🎤 Selected: PulseAudio microphone (index {selected})")
        elif fallback_index is not None:
            selected = fallback_index
            print(f"[VOICE] 🎤 Selected: Default microphone (index {selected})")
        else:
            print("[VOICE] ✗ No microphone-capable audio devices found!")
            return None
            
        return selected

    def _init_tts(self):
        """Initializes available TTS backends (Google TTS preferred for quality)."""

        # Piper CLI support (requires piper-tts package and downloaded model files)
        self.piper_model_path = os.getenv('PIPER_MODEL_PATH')
        self.piper_config_path = os.getenv('PIPER_CONFIG_PATH')
        self.piper_speaker_id = os.getenv('PIPER_SPEAKER_ID')
        piper_exec = shutil.which('piper')
        if (
            piper_exec
            and self.piper_model_path
            and self.piper_config_path
            and os.path.exists(self.piper_model_path)
            and os.path.exists(self.piper_config_path)
        ):
            self.tts_backend = 'piper'
            print('Piper TTS enabled (CLI mode).')
            return piper_exec  # placeholder marker that Piper is available

        # Prefer Google TTS (gTTS) for best quality - requires internet
        # This provides natural, smooth voice for both English and Hinglish
        try:
            # Test if gTTS is available and internet is accessible
            from gtts import gTTS
            self.tts_backend = 'gtts'
            print('Google TTS (gTTS) enabled - High quality natural voice.')
            return 'gtts'  # placeholder marker
        except Exception as e:
            print(f"gTTS not available: {e}")

        # Check for espeak-ng (fallback for offline mode)
        espeak_ng = shutil.which('espeak-ng')
        if espeak_ng:
            self.tts_backend = 'espeak-ng'
            print('eSpeak-NG TTS enabled (CLI mode) - Offline fallback.')
            return espeak_ng

        # Fallback to local pyttsx3 (requires eSpeak/eSpeak-NG on Linux)
        if pyttsx3 is not None:
            try:
                engine = pyttsx3.init(driverName='espeak')
                rate = int(os.getenv('SPEECH_RATE', '180'))
                engine.setProperty('rate', rate)
                engine.setProperty('volume', 0.9)
                self.tts_backend = 'pyttsx3'
                print('pyttsx3 TTS enabled.')
                return engine
            except Exception as e:
                print(f"Failed to initialize pyttsx3: {e}")
        
        self.tts_backend = None
        print("No TTS backend available - speech disabled")
        return None

    def speak(self, text: str, lang: str = 'en'):
        """
        Public interface to speak text with specified language.
        Thread-safe via _speech_lock to avoid overlapping audio.
        OPTIMIZED: Cached phrases > Fast local TTS > Google TTS
        """
        with self._speech_lock:
            try:
                if not text:
                    return
                
                text_lower = text.lower().strip()
                
                # 1. Check cache for common phrases (INSTANT playback)
                cache_file = self._get_cached_audio(text_lower)
                if cache_file and os.path.exists(cache_file):
                    print(f"[VOICE] Using CACHED audio for: {text[:50]}")
                    try:
                        subprocess.run(['mpg123', '--quiet', cache_file], timeout=5, check=False)
                        print(f"[VOICE] ✓ Cached audio played instantly")
                        return
                    except:
                        pass  # Cache failed, continue to TTS
                
                # 2. For very short responses, use FAST local TTS (instant)
                # For longer responses, use Google TTS (better quality)
                use_fast_local = len(text.split()) <= 10  # 10 words or less = instant response
                
                if use_fast_local and self.pyttsx3_engine:
                    print(f"[VOICE] Using FAST local TTS for short response: {text[:50]}")
                    try:
                        self.pyttsx3_engine.say(text)
                        self.pyttsx3_engine.runAndWait()
                        print(f"[VOICE] ✓ Fast local TTS completed instantly")
                        return
                    except Exception as e:
                        print(f"[VOICE] Fast TTS failed: {e}, falling back to Google TTS")
                
                # 3. Use Google TTS for longer responses (better quality)
                self._speak_gtts(text, lang)
                
                # Cache this response if short enough for future instant playback
                if len(text.split()) <= 5:
                    self._cache_audio(text_lower, lang)
                    
            except Exception as e:
                print(f"[VOICE] Speech error: {e}")
                traceback.print_exc()
    
    def _detect_language(self, text: str) -> str:
        """
        Detect if text is English, Hindi, or Hinglish.
        Returns 'en' for English, 'hi' for Hindi.
        """
        # Check for Devanagari characters (Hindi script)
        has_devanagari = any('\u0900' <= c <= '\u097F' for c in text)
        
        # Check for non-ASCII characters (could be Hindi in Roman script or other)
        has_non_ascii = not all(ord(c) < 128 for c in text)
        
        if has_devanagari:
            return 'hi'
        elif has_non_ascii or self._is_hinglish(text):
            return 'hi'  # Treat Hinglish as Hindi for better TTS
        else:
            return 'en'
    
    def _is_hinglish(self, text: str) -> bool:
        """
        Detect if text contains common Hinglish patterns.
        Hinglish = Hindi words written in English (Roman) script mixed with English.
        """
        # Common Hinglish words and patterns
        hinglish_patterns = [
            # Common Hindi words in Roman script
            r'\b(kya|hai|hain|ho|hoon|karo|kro|nahi|nhi|accha|thik|theek|bahut|abhi|'
            r'jarvis|bolo|batao|btao|dikha|dikhao|chalo|karo|kya|kaise|kaun|kab|kaha|'
            r'mujhe|tumhe|aap|tum|main|hum|yeh|ye|woh|wo|iska|uska|inka|unka|'
            r'bhai|yaar|dost|dekho|dekh|suno|sun|samjhe|samjha|theek|thoda|'
            r'bohot|kuch|sab|sabhi|koi|kisi|aise|waise|vaise|matlab|kyunki|kyuki|'
            r'lekin|par|aur|ya|bhi|bhe|toh|to|ki|ke|ka|se|me|mein|pe|tak|'
            r'chalo|chal|ruko|ruk|rakh|rakho|lao|de|do|lo|le|aa|aao|ja|jao)\b',
            
            # Common transliterated Hindi verbs
            r'\b(karna|karna|karna|karte|karti|karta|kiye|kiya|'
            r'hona|hota|hoti|hote|hua|hui|hue|'
            r'jana|jata|jati|jate|gaya|gayi|gaye|'
            r'aana|aata|aati|aate|aaya|aayi|aaye|'
            r'dena|deta|deti|dete|diya|diyi|diye|'
            r'lena|leta|leti|lete|liya|liyi|liye)\b',
        ]
        
        import re
        text_lower = text.lower()
        
        for pattern in hinglish_patterns:
            if re.search(pattern, text_lower):
                return True
        
        return False

    def _speak_pyttsx3(self, text: str):
        """Handles speaking with the local pyttsx3 engine."""
        try:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except Exception as e:
            print(f"pyttsx3 error: {e}")

    def _speak_espeak(self, text: str):
        """Speak using espeak-ng CLI via PulseAudio (supports Bluetooth devices)."""
        try:
            print(f"[VOICE] _speak_espeak called with: {text[:50]}...")
            # Optimized for smooth, natural speech
            rate = int(os.getenv('SPEECH_RATE', '160'))  # Slightly slower for clarity
            pitch = int(os.getenv('SPEECH_PITCH', '50'))  # Normal pitch
            
            # Generate WAV file with better quality settings
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_audio:
                tmp_path = tmp_audio.name
            
            # Generate WAV file with improved voice quality
            result = subprocess.run(
                ['espeak-ng', 
                 '-v', 'en-us',  # US English voice
                 '-s', str(rate),  # Speed (words per minute)
                 '-p', str(pitch),  # Pitch (0-99)
                 '-a', '200',  # Amplitude (volume)
                 '-w', tmp_path,  # Write to file
                 text],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                check=False,
                text=True
            )
            
            if result.returncode != 0:
                print(f"[VOICE] espeak-ng WAV generation error (code {result.returncode}): {result.stderr}")
                os.unlink(tmp_path)
                return
            
            # Check if WAV file was created and has content
            if not os.path.exists(tmp_path):
                print(f"[VOICE] WAV file was not created: {tmp_path}")
                return
            
            wav_size = os.path.getsize(tmp_path)
            print(f"[VOICE] Generated WAV file: {wav_size} bytes")
            
            # Play WAV file with paplay (PulseAudio - works with Bluetooth)
            # --volume sets output volume (65536 = 100%)
            play_result = subprocess.run(
                ['paplay', '--volume=65536', tmp_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
                text=True
            )
            
            # Clean up
            try:
                os.unlink(tmp_path)
            except:
                pass
                
            if play_result.returncode == 0:
                print(f"[VOICE] Speech played successfully via Bluetooth/PulseAudio")
            else:
                print(f"[VOICE] paplay failed with code {play_result.returncode}")
                print(f"[VOICE] stderr: {play_result.stderr}")
                
        except Exception as e:
            print(f"[VOICE] espeak-ng exception: {e}")

    def _speak_piper(self, text: str):
        """Synthesize speech using Piper CLI for high-quality offline audio."""
        if not self.piper_model_path or not self.piper_config_path:
            print(f"Piper configuration missing, cannot speak: {text}")
            return

        try:
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_audio:
                tmp_path = tmp_audio.name

            cmd = [
                'piper',
                '--model', self.piper_model_path,
                '--config', self.piper_config_path,
                '--output_file', tmp_path,
            ]
            if self.piper_speaker_id:
                cmd.extend(['--speaker', self.piper_speaker_id])

            proc = subprocess.run(
                cmd,
                input=text.encode('utf-8'),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            if proc.returncode != 0:
                print(f"Piper synthesis failed: {proc.stderr.decode('utf-8', errors='ignore')}")
                os.unlink(tmp_path)
                return

            playsound(tmp_path)
        except Exception as e:
            print(f"Piper TTS error: {e}")
        finally:
            try:
                if 'tmp_path' in locals() and os.path.exists(tmp_path):
                    os.unlink(tmp_path)
            except Exception:
                pass

    def _speak_gtts(self, text: str, lang: str):
        """
        Handles speaking with Google Text-to-Speech via PulseAudio (supports Bluetooth).
        Provides natural, human-like voice quality for both English and Hinglish.
        ULTRA-OPTIMIZED for fastest response.
        """
        try:
            print(f"[VOICE] TTS start - {len(text)} chars")
            
            # Auto-detect if Hinglish and use English for better mixed language support
            if self._is_hinglish(text) and lang == 'en':
                print(f"[VOICE] Hinglish mode")
            
            # Create TTS with aggressive optimization
            tts = gTTS(
                text=text, 
                lang=lang, 
                slow=False,
                tld='co.in' if lang == 'hi' else 'com',
                timeout=2  # Reduced from 3 to 2 seconds
            )
            
            temp_file = os.path.join(self.temp_audio_dir, f"gtts_{uuid.uuid4()}.mp3")
            tts.save(temp_file)
            
            print(f"[VOICE] TTS generated - {os.path.getsize(temp_file)} bytes")
            
            # Speed up audio with sox - FASTER processing
            speedup_file = temp_file
            try:
                speedup_file = os.path.join(self.temp_audio_dir, f"fast_{uuid.uuid4()}.mp3")
                # Use tempo 1.35 for 35% speedup (faster than before)
                sox_result = subprocess.run(
                    ['sox', temp_file, speedup_file, 'tempo', '1.35'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=False,
                    timeout=1.5  # Reduced from 2s to 1.5s
                )
                if sox_result.returncode == 0:
                    print(f"[VOICE] ✓ 35% faster")
                    os.remove(temp_file)
                else:
                    speedup_file = temp_file
                    try:
                        if os.path.exists(speedup_file) and speedup_file != temp_file:
                            os.remove(speedup_file)
                    except:
                        pass
                    speedup_file = temp_file
            except subprocess.TimeoutExpired:
                print(f"[VOICE] Sox timeout")
                speedup_file = temp_file
            except (FileNotFoundError, Exception):
                speedup_file = temp_file
            
            # Play with aggressive buffering for instant start
            play_process = None
            try:
                play_process = subprocess.Popen(
                    ['mpg123', '--quiet', '-b', '256', speedup_file],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                # Wait for completion with timeout
                play_process.wait(timeout=15)
                
                if play_process.returncode == 0:
                    print(f"[VOICE] ✓ Played")
                else:
                    print(f"[VOICE] ✗ Play failed (code {play_process.returncode})")
                    
            except subprocess.TimeoutExpired:
                print(f"[VOICE] ✗ mpg123 timeout - killing process")
                if play_process:
                    play_process.kill()
                    play_process.wait()  # Ensure process is dead
                raise  # Re-raise to trigger fallback
            
            # Fast cleanup
            try:
                if os.path.exists(speedup_file):
                    os.remove(speedup_file)
                if speedup_file != temp_file and os.path.exists(temp_file):
                    os.remove(temp_file)
            except:
                pass
                
        except subprocess.TimeoutExpired:
            # Timeout occurred - ensure process is killed before fallback
            print(f"[VOICE] ✗ Google TTS timeout - switching to offline TTS")
            # Cleanup files before fallback
            try:
                if 'speedup_file' in locals() and os.path.exists(speedup_file):
                    os.remove(speedup_file)
                if 'temp_file' in locals() and speedup_file != temp_file and os.path.exists(temp_file):
                    os.remove(temp_file)
            except:
                pass
            # Now fallback to espeak
            if hasattr(self, '_speak_espeak'):
                self._speak_espeak(text)
            else:
                print(f"[VOICE] No fallback available. Text: {text}")
                
        except Exception as e:
            print(f"[VOICE] ✗ Google TTS error: {e}")
            print(f"[VOICE] Falling back to offline TTS...")
            # Cleanup files before fallback
            try:
                if 'speedup_file' in locals() and os.path.exists(speedup_file):
                    os.remove(speedup_file)
                if 'temp_file' in locals() and speedup_file != temp_file and os.path.exists(temp_file):
                    os.remove(temp_file)
            except:
                pass
            # Fallback to espeak if gTTS fails (network issue, etc.)
            if hasattr(self, '_speak_espeak'):
                self._speak_espeak(text)
            else:
                print(f"[VOICE] No fallback available. Text: {text}")
    
    def _get_cached_audio(self, text: str) -> str:
        """Get cached audio file path if it exists"""
        import hashlib
        # Create hash of text for filename
        text_hash = hashlib.md5(text.encode()).hexdigest()[:16]
        cache_file = os.path.join(self.audio_cache_dir, f"{text_hash}.mp3")
        if os.path.exists(cache_file):
            return cache_file
        return None
    
    def _cache_audio(self, text: str, lang: str):
        """Cache audio for short common phrases (async to not slow down response)"""
        try:
            import hashlib
            text_hash = hashlib.md5(text.encode()).hexdigest()[:16]
            cache_file = os.path.join(self.audio_cache_dir, f"{text_hash}.mp3")
            
            # Only cache if not already cached
            if not os.path.exists(cache_file):
                # Generate and save to cache in background
                threading.Thread(target=self._generate_cache, args=(text, lang, cache_file), daemon=True).start()
        except Exception as e:
            # Caching is optional, don't break if it fails
            pass
    
    def _generate_cache(self, text: str, lang: str, cache_file: str):
        """Generate cached audio file in background"""
        try:
            from gtts import gTTS
            tts = gTTS(text=text, lang=lang, slow=False, timeout=3)
            tts.save(cache_file)
        except:
            pass  # Silent fail for background caching

    def _listening_loop(self):
        """
        The core loop that continuously listens to the microphone stream.
        Optimized for Bluetooth microphone (Mini Boost 4) via PulseAudio.
        """
        if not self.audio_interface:
            print("[VOICE] Audio interface unavailable; listening loop aborted.")
            return
        
        try:
            # Configure stream for Bluetooth microphone compatibility
            open_kwargs = dict(
                format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.RATE,
                input=True,
                frames_per_buffer=self.CHUNK,
                stream_callback=None,  # Use blocking mode for reliability
            )
            
            if self.microphone_index is not None:
                open_kwargs['input_device_index'] = self.microphone_index
                device_info = self.audio_interface.get_device_info_by_index(self.microphone_index)
                print(f"[VOICE] Opening microphone: {device_info.get('name')}")
                print(f"[VOICE] Settings: {self.RATE}Hz, {self.CHANNELS}ch, chunk={self.CHUNK}")

            self.stream = self.audio_interface.open(**open_kwargs)
            print("[VOICE] ✓ Microphone stream opened successfully via PulseAudio")
            
        except Exception as e:
            print(f"[VOICE] ✗ Failed to open microphone stream: {e}")
            print(f"[VOICE] Trying to list available devices...")
            list_audio_devices()
            return

        recognizer = KaldiRecognizer(self.vosk_model, self.RATE)
        recognizer.SetWords(True)  # Enable word-level timing for better accuracy
        
        # Import numpy for audio processing
        import numpy as np
        
        # Track audio levels for debugging
        last_status_time = time.time()
        speech_detected_count = 0
        
        if self.continuous_mode:
            print(f"🎤 Continuous listening mode - Speak directly (no wake word needed)")
            print(f"🎤 Microphone gain: {self.INPUT_GAIN}x | Noise threshold: {self.NOISE_THRESHOLD}")
            print(f"🎤 Listening... (speak clearly and close to mic)")
            self.is_awake = True  # Always awake in continuous mode
        else:
            print(f"🎤 Listening for wake word: '{self.wake_word}'...")
        
        while not self._stop_listening.is_set():
            try:
                data = self.stream.read(self.CHUNK, exception_on_overflow=False)
                
                # Apply noise cancellation and gain boost
                # Convert bytes to numpy array for processing
                audio_data = np.frombuffer(data, dtype=np.int16)
                
                # Apply input gain (boost microphone volume)
                audio_data = np.clip(audio_data * self.INPUT_GAIN, -32768, 32767).astype(np.int16)
                
                # Simple noise gate - only process if audio level is above threshold
                audio_level = np.abs(audio_data).mean()
                
                # Show audio level every 3 seconds for debugging
                if time.time() - last_status_time > 3:
                    print(f"[MIC] Audio level: {int(audio_level)} | Threshold: {self.NOISE_THRESHOLD} | Detected: {speech_detected_count}")
                    last_status_time = time.time()
                    speech_detected_count = 0
                
                if audio_level < self.NOISE_THRESHOLD:
                    # Too quiet - likely background noise, skip processing
                    continue
                
                # Audio is loud enough, increment counter
                speech_detected_count += 1
                
                # Convert back to bytes
                data = audio_data.tobytes()
                
                if recognizer.AcceptWaveform(data):
                    result_json = json.loads(recognizer.Result())
                    text = result_json.get('text', '').lower().strip()
                    
                    # Hinglish word mapping - convert common Hinglish to English for better recognition
                    hinglish_map = {
                        'karo': 'do it',
                        'batao': 'tell me',
                        'dikha': 'show',
                        'dikho': 'show',
                        'chalo': 'go',
                        'ruko': 'wait',
                        'theek': 'okay',
                        'haan': 'yes',
                        'nahi': 'no',
                        'kya': 'what',
                        'kaise': 'how',
                        'kyun': 'why',
                    }
                    
                    # Replace Hinglish words but keep original text too
                    original_text = text
                    for hindi, english in hinglish_map.items():
                        if hindi in text:
                            text = text.replace(hindi, english)
                    
                    if self.continuous_mode:
                        # Continuous mode - process every recognized speech
                        # Use original_text if it has content
                        if original_text and self.transcript_callback:
                            # Show both original and processed if different
                            if text != original_text:
                                print(f"🎤 Recognized: {original_text} → {text}")
                            else:
                                print(f"🎤 Recognized: {original_text}")
                            
                            # Always call callback with the recognized text
                            print(f"[VOICE] Sending to callback: '{original_text}'")
                            try:
                                self.transcript_callback(original_text)  # Send original for natural processing
                            except Exception as callback_err:
                                print(f"[VOICE] ✗ Callback error: {callback_err}")
                                import traceback
                                traceback.print_exc()
                                
                    elif self.is_awake:
                        # Wake word mode - process command after wake word
                        if text and self.transcript_callback:
                            print(f"🎤 Command recognized: {text}")
                            self.transcript_callback(text)
                            self.go_to_sleep()
                    elif self.wake_word and self.wake_word in text:
                        # Wake word detected
                        print(f"✓ Wake word '{self.wake_word}' detected!")
                        self.activate_listening()
                else:
                    # Check partial results for faster wake word detection (only if wake word mode)
                    if not self.continuous_mode:
                        partial_result_json = json.loads(recognizer.PartialResult())
                        partial_text = partial_result_json.get('partial', '').lower().strip()
                        if not self.is_awake and self.wake_word and self.wake_word in partial_text:
                            print(f"✓ Wake word '{self.wake_word}' detected (partial)!")
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
        print("🎤 J.A.R.V.I.S. activated! Listening for command...")
        
        # Provide audio feedback (brief beep or acknowledgment)
        if self.wake_word_activation_callback:
            self.wake_word_activation_callback()

        # Cancel any existing timeout thread
        if self.command_timeout_thread and self.command_timeout_thread.is_alive():
            self.command_timeout_thread.cancel()

        # Set a timeout to go back to sleep if no command is heard
        self.command_timeout_thread = threading.Timer(10.0, self.go_to_sleep)  # Increased to 10s
        self.command_timeout_thread.start()

    def go_to_sleep(self):
        """Puts Jarvis back into standby (wake-word-only) mode."""
        if not self.is_awake:
            return
            
        self.is_awake = False
        print("💤 Returning to wake word detection mode...")
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
    
if __name__ == "__main__":
    print("Testing VoiceEngine with enhanced features...")
    print("Press Ctrl+C to stop.\n")
    
    def on_speech(text):
        print(f"\n🎤 Heard: '{text}'")
        if "exit" in text.lower() or "stop" in text.lower():
            print("Exit command detected!")
            engine.stop()
    
    # Initialize engine with continuous listening (no wake word)
    engine = VoiceEngine(wake_word=None, transcript_callback=on_speech)
    
    # Test speaking
    engine.speak("Voice engine test. Enhanced microphone and faster speech active.")
    
    # Start listening
    print("\n🎤 Listening... (say 'exit' or 'stop' to quit)")
    engine.start()
    
    try:
        # Keep running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nStopping...")
    finally:
        engine.stop()
        print("Voice engine stopped.")
        print("Test finished.")

