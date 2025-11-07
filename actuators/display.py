"""LCD controller with optional idle-face animation loop."""

import os
import threading
import time
from typing import List, Tuple

from RPLCD.i2c import CharLCD
from core.hardware_manager import hardware_manager

class Display:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Display, cls).__new__(cls)
        return cls._instance

    def __init__(self, i2c_expander='PCF8574', address=0x27, port=1):
        if hasattr(self, 'initialized') and self.initialized:
            return

        self.simulation_mode = hardware_manager.simulation_mode
        self.lcd = None
        self._display_lock = threading.Lock()
        self._animation_thread: threading.Thread | None = None
        self._animation_stop = threading.Event()
        self._last_manual_update = time.time()
        self._idle_delay = float(os.getenv("DISPLAY_IDLE_ANIMATION_DELAY", "15"))
        self._animation_frames: List[Tuple[str, float]] = [
            ("neutral", 3.0),
            ("happy", 1.8),
            ("neutral", 2.5),
            ("thinking", 1.8),
            ("listening", 1.6),
        ]

        if not self.simulation_mode:
            try:
                self.lcd = CharLCD(i2c_expander, address, port=port, charmap='A00',
                                   cols=16, rows=2)
                self.lcd.clear()
                self._define_custom_chars()
                self.show_face('neutral')
                print("LCD Display initialized.")
            except Exception as e:
                print(f"Error: Could not initialize LCD display: {e}")
                print("Display will run in simulation mode.")
                self.simulation_mode = True
                self.lcd = None
        
        if self.simulation_mode:
            print("LCD Display initialized (Simulation Mode).")

        self.initialized = True

        # ------------------------------------------------------------------
        def _handle_display_error(self, error: Exception) -> None:
            """Log hardware errors and fall back to simulation mode."""
            if self.simulation_mode:
                return
            print(f"[Display] Hardware error: {error}. Switching to simulation mode.")
            self.simulation_mode = True
            if self.lcd:
                try:
                    self.lcd.close(clear=False)
                except Exception:
                    pass
                finally:
                    self.lcd = None

    def _define_custom_chars(self):
        """Defines custom characters for facial expressions."""
        if self.simulation_mode or not self.lcd:
            return

        # Custom characters for eyes and mouth parts
        # Each is a tuple of 8 bytes (8 rows of 5 pixels)
        
        # 0: Left part of a wide eye
        eye_left = (
            0b01110,
            0b10001,
            0b10001,
            0b10001,
            0b10001,
            0b10001,
            0b01110,
            0b00000
        )
        # 1: Right part of a wide eye
        eye_right = (
            0b01110,
            0b10001,
            0b10001,
            0b10001,
            0b10001,
            0b10001,
            0b01110,
            0b00000
        )
        # 2: Left part of a narrow/squint eye
        eye_narrow_left = (
            0b00000,
            0b00000,
            0b01110,
            0b10001,
            0b10001,
            0b01110,
            0b00000,
            0b00000
        )
        # 3: Right part of a narrow/squint eye
        eye_narrow_right = (
            0b00000,
            0b00000,
            0b01110,
            0b10001,
            0b10001,
            0b01110,
            0b00000,
            0b00000
        )
        # 4: Smile left
        smile_left = (
            0b00000,
            0b00000,
            0b00000,
            0b00000,
            0b10000,
            0b01000,
            0b00110,
            0b00000
        )
        # 5: Smile right
        smile_right = (
            0b00000,
            0b00000,
            0b00000,
            0b00000,
            0b00001,
            0b00010,
            0b01100,
            0b00000
        )
        # 6: Frown left
        frown_left = (
            0b00000,
            0b00110,
            0b01000,
            0b10000,
            0b00000,
            0b00000,
            0b00000,
            0b00000
        )
        # 7: Frown right
        frown_right = (
            0b00000,
            0b01100,
            0b00010,
            0b00001,
            0b00000,
            0b00000,
            0b00000,
            0b00000
        )

        self.lcd.create_char(0, eye_left)
        self.lcd.create_char(1, eye_right)
        self.lcd.create_char(2, eye_narrow_left)
        self.lcd.create_char(3, eye_narrow_right)
        self.lcd.create_char(4, smile_left)
        self.lcd.create_char(5, smile_right)
        self.lcd.create_char(6, frown_left)
        self.lcd.create_char(7, frown_right)

    def write_text(self, text, row=0, col=0):
        """
        Writes text to the display at a specific position.
        Automatically handles line wrapping for long text.
        """
        with self._display_lock:
            if self.simulation_mode or not self.lcd:
                print(f"[LCD SIM] Write (row={row}, col={col}): '{text}'")
                self._last_manual_update = time.time()
                return

            try:
                self.lcd.cursor_pos = (row, col)
                # Simple word wrapping
                words = text.split(' ')
                current_col = col
                current_row = row
                for word in words:
                    if len(word) > 16:  # Word is too long for one line
                        if current_col > 0:
                            current_row += 1
                            current_col = 0
                        if current_row > 1:
                            break
                        self.lcd.cursor_pos = (current_row, current_col)
                        self.lcd.write_string(word[:16-current_col])
                        current_row += 1
                        if current_row > 1:
                            break
                        self.lcd.cursor_pos = (current_row, 0)
                        self.lcd.write_string(word[16-current_col:])
                        current_col = len(word[16-current_col:])
                    elif current_col + len(word) > 15:  # Word wraps to next line
                        current_row += 1
                        current_col = 0
                        if current_row > 1:
                            break
                        self.lcd.cursor_pos = (current_row, current_col)
                        self.lcd.write_string(word)
                        current_col += len(word) + 1
                    else:  # Word fits on current line
                        self.lcd.cursor_pos = (current_row, current_col)
                        self.lcd.write_string(word)
                        current_col += len(word) + 1
            except Exception as exc:
                self._handle_display_error(exc)
            finally:
                self._last_manual_update = time.time()


    def clear(self):
        """Clears the display."""
        with self._display_lock:
            if self.simulation_mode or not self.lcd:
                print("[LCD SIM] Clear display")
                self._last_manual_update = time.time()
                return
            try:
                self.lcd.clear()
            except Exception as exc:
                self._handle_display_error(exc)
            finally:
                self._last_manual_update = time.time()

    def show_face(self, face_name: str):
        """
        Displays a predefined facial expression.
        Valid names: 'neutral', 'happy', 'sad', 'thinking', 'listening'
        """
        self._render_face(face_name, from_animation=False)

    def _render_face(self, face_name: str, *, from_animation: bool) -> None:
        with self._display_lock:
            if self.simulation_mode or not self.lcd:
                print(f"[LCD SIM] Show face: {face_name}")
                if not from_animation:
                    self._last_manual_update = time.time()
                return

            try:
                self.lcd.clear()

                if face_name == 'happy':
                    self.lcd.cursor_pos = (0, 5)
                    self.lcd.write_string(f"\x00\x01  \x00\x01")
                    self.lcd.cursor_pos = (1, 6)
                    self.lcd.write_string(f"\x04\x05")
                elif face_name == 'sad':
                    self.lcd.cursor_pos = (0, 5)
                    self.lcd.write_string(f"\x02\x03  \x02\x03")
                    self.lcd.cursor_pos = (1, 6)
                    self.lcd.write_string(f"\x06\x07")
                elif face_name == 'thinking':
                    self.lcd.cursor_pos = (0, 5)
                    self.lcd.write_string(f"\x00\x01  \x02\x03")
                    self.lcd.cursor_pos = (1, 6)
                    self.lcd.write_string("--")
                elif face_name == 'listening':
                    self.lcd.cursor_pos = (0, 5)
                    self.lcd.write_string(f"\x00\x01  \x00\x01")
                    self.lcd.cursor_pos = (1, 7)
                    self.lcd.write_string("o")
                else:  # neutral
                    self.lcd.cursor_pos = (0, 5)
                    self.lcd.write_string(f"\x00\x01  \x00\x01")
                    self.lcd.cursor_pos = (1, 6)
                    self.lcd.write_string("--")
            except Exception as exc:
                self._handle_display_error(exc)
            finally:
                if not from_animation:
                    self._last_manual_update = time.time()

    def start_idle_animation(self) -> None:
        """Start looping through faces when the display has been idle."""
        if self.simulation_mode:
            return
        if self._animation_thread and self._animation_thread.is_alive():
            return
        self._animation_stop.clear()
        self._animation_thread = threading.Thread(target=self._animation_loop, daemon=True)
        self._animation_thread.start()

    def stop_idle_animation(self) -> None:
        """Stop the idle animation loop if running."""
        if not self._animation_thread:
            return
        self._animation_stop.set()
        self._animation_thread.join(timeout=1.0)
        self._animation_thread = None

    def _animation_loop(self) -> None:
        while not self._animation_stop.is_set():
            idle_for = time.time() - self._last_manual_update
            if idle_for < self._idle_delay:
                remaining = self._idle_delay - idle_for
                self._animation_stop.wait(remaining)
                continue

            for face, duration in self._animation_frames:
                if self._animation_stop.is_set():
                    break
                if time.time() - self._last_manual_update < self._idle_delay:
                    break
                try:
                    self._render_face(face, from_animation=True)
                except Exception as exc:
                    self._handle_display_error(exc)
                    break
                if self._animation_stop.wait(duration):
                    break

    def cleanup(self):
        self.stop_idle_animation()
        if not self.simulation_mode and self.lcd:
            with self._display_lock:
                self.lcd.clear()
                self.lcd.close(clear=True)
            print("LCD Display cleaned up.")

# Singleton instance
display = Display()

if __name__ == '__main__':
    print("Running LCD Display test...")
    try:
        display.show_face('neutral')
        time.sleep(2)
        display.show_face('happy')
        time.sleep(2)
        display.show_face('sad')
        time.sleep(2)
        display.show_face('thinking')
        time.sleep(2)
        display.show_face('listening')
        time.sleep(2)
        
        display.clear()
        display.write_text("Hello, Jarvis!", row=0, col=2)
        display.write_text("System Online", row=1, col=2)
        time.sleep(3)

        display.clear()
        display.write_text("This is a very long line of text that should wrap correctly to the next line.", row=0, col=0)
        time.sleep(4)

    except KeyboardInterrupt:
        print("Test interrupted.")
    finally:
        display.cleanup()
        print("Test finished.")
