"""
Controls the 16x2 I2C LCD Display for Jarvis.

This module provides a class to interact with a standard 16x2 character LCD
that uses an I2C backpack (like the PCF8574). It allows for displaying text,
clearing the screen, and showing simple, predefined facial expressions.

Facial expressions are created using custom characters.
"""

from RPLCD.i2c import CharLCD
from core.hardware_manager import hardware_manager
import time

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
        
        if self.simulation_mode:
            print("LCD Display initialized (Simulation Mode).")

        self.initialized = True

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
        if self.simulation_mode:
            print(f"[LCD SIM] Write (row={row}, col={col}): '{text}'")
            return
        if not self.lcd: return

        self.lcd.cursor_pos = (row, col)
        # Simple word wrapping
        words = text.split(' ')
        current_col = col
        current_row = row
        for word in words:
            if len(word) > 16: # Word is too long for one line
                if current_col > 0:
                    current_row += 1
                    current_col = 0
                if current_row > 1: break
                self.lcd.cursor_pos = (current_row, current_col)
                self.lcd.write_string(word[:16-current_col])
                current_row += 1
                if current_row > 1: break
                self.lcd.cursor_pos = (current_row, 0)
                self.lcd.write_string(word[16-current_col:])
                current_col = len(word[16-current_col:])
            elif current_col + len(word) > 15: # Word wraps to next line
                current_row += 1
                current_col = 0
                if current_row > 1: break
                self.lcd.cursor_pos = (current_row, current_col)
                self.lcd.write_string(word)
                current_col += len(word) + 1
            else: # Word fits on current line
                self.lcd.cursor_pos = (current_row, current_col)
                self.lcd.write_string(word)
                current_col += len(word) + 1


    def clear(self):
        """Clears the display."""
        if self.simulation_mode:
            print("[LCD SIM] Clear display")
            return
        if self.lcd:
            self.lcd.clear()

    def show_face(self, face_name: str):
        """
        Displays a predefined facial expression.
        Valid names: 'neutral', 'happy', 'sad', 'thinking', 'listening'
        """
        if self.simulation_mode:
            print(f"[LCD SIM] Show face: {face_name}")
            return
        if not self.lcd: return

        self.clear()
        
        # Faces are drawn on the top row, centered.
        # Using custom characters for eyes and mouth.
        #   \x00 = eye_left, \x01 = eye_right
        #   \x02 = eye_narrow_left, \x03 = eye_narrow_right
        #   \x04 = smile_left, \x05 = smile_right
        #   \x06 = frown_left, \x07 = frown_right
        
        if face_name == 'happy':
            # Wide eyes, smiling mouth
            self.lcd.cursor_pos = (0, 5)
            self.lcd.write_string(f"\x00\x01  \x00\x01")
            self.lcd.cursor_pos = (1, 6)
            self.lcd.write_string(f"\x04\x05")
        elif face_name == 'sad':
            # Narrow eyes, frowning mouth
            self.lcd.cursor_pos = (0, 5)
            self.lcd.write_string(f"\x02\x03  \x02\x03")
            self.lcd.cursor_pos = (1, 6)
            self.lcd.write_string(f"\x06\x07")
        elif face_name == 'thinking':
            # One wide eye, one narrow eye, flat mouth
            self.lcd.cursor_pos = (0, 5)
            self.lcd.write_string(f"\x00\x01  \x02\x03")
            self.lcd.cursor_pos = (1, 6)
            self.lcd.write_string("--")
        elif face_name == 'listening':
            # Wide eyes, open mouth (circle)
            self.lcd.cursor_pos = (0, 5)
            self.lcd.write_string(f"\x00\x01  \x00\x01")
            self.lcd.cursor_pos = (1, 7)
            self.lcd.write_string("o")
        else: # neutral
            # Wide eyes, flat mouth
            self.lcd.cursor_pos = (0, 5)
            self.lcd.write_string(f"\x00\x01  \x00\x01")
            self.lcd.cursor_pos = (1, 6)
            self.lcd.write_string("--")

    def cleanup(self):
        if not self.simulation_mode and self.lcd:
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
