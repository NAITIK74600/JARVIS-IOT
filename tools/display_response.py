"""
Enhanced Display Response Handler with Hinglish Support
Shows AI responses on I2C LCD display with smart text formatting
"""

import time
import re
from actuators.display import display
from typing import Optional

class DisplayResponseHandler:
    """Handles displaying AI responses on the LCD with smart formatting"""
    
    def __init__(self):
        self.display = display
        self.max_cols = 16
        self.max_rows = 2
        self.scroll_delay = 0.4  # Delay between scroll updates in seconds
        
    def transliterate_hinglish(self, text: str) -> str:
        """
        Convert common Hinglish words to English transliteration for display
        """
        hinglish_map = {
            # Common Hindi/Hinglish words
            'हाँ': 'Haan', 'नहीं': 'Nahi', 'क्या': 'Kya',
            'कैसे': 'Kaise', 'कहाँ': 'Kahan', 'कब': 'Kab',
            'क्यों': 'Kyu', 'कौन': 'Kaun', 'जी': 'Ji',
            'ठीक': 'Theek', 'अच्छा': 'Achha', 'बहुत': 'Bahut',
            'सर': 'Sir', 'जी हाँ': 'Ji Haan',
            # Common responses
            'धन्यवाद': 'Dhanyavaad', 'शुक्रिया': 'Shukriya',
            'नमस्ते': 'Namaste', 'नमस्कार': 'Namaskar',
        }
        
        result = text
        for hindi, english in hinglish_map.items():
            result = result.replace(hindi, english)
        
        return result
    
    def clean_text(self, text: str) -> str:
        """Clean text for LCD display - remove special chars, extra spaces"""
        # Remove markdown formatting
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # Bold
        text = re.sub(r'\*([^*]+)\*', r'\1', text)      # Italic
        text = re.sub(r'`([^`]+)`', r'\1', text)        # Code
        
        # Remove URLs
        text = re.sub(r'http[s]?://\S+', '', text)
        
        # Clean up extra whitespace
        text = ' '.join(text.split())
        
        # Transliterate Hinglish
        text = self.transliterate_hinglish(text)
        
        return text.strip()
    
    def truncate_text(self, text: str, max_length: int) -> str:
        """Truncate text to fit display with ellipsis"""
        if len(text) <= max_length:
            return text
        return text[:max_length-2] + '..'
    
    def split_text_smart(self, text: str) -> tuple:
        """
        Split text into two lines smartly at word boundaries
        Returns (line1, line2, has_more)
        """
        words = text.split()
        line1 = ""
        line2 = ""
        has_more = False
        
        # Build line 1
        for word in words:
            if len(line1) + len(word) + 1 <= self.max_cols:
                line1 += (word + " ")
            else:
                break
        
        # Get remaining text
        remaining = text[len(line1):].strip()
        
        if remaining:
            # Build line 2 from remaining
            for word in remaining.split():
                if len(line2) + len(word) + 1 <= self.max_cols:
                    line2 += (word + " ")
                else:
                    has_more = True
                    break
        
        return (line1.strip(), line2.strip(), has_more)
    
    def show_response(self, text: str, duration: float = 5.0, scroll: bool = True):
        """
        Display AI response on LCD
        - text: Response text to display
        - duration: How long to show (seconds)
        - scroll: Whether to scroll long text
        """
        if not text:
            return
        
        # Clean the text
        cleaned = self.clean_text(text)
        
        if len(cleaned) <= self.max_cols * self.max_rows:
            # Short text - fits on display
            self._show_static(cleaned, duration)
        elif scroll:
            # Long text - scroll it
            self._show_scrolling(cleaned, duration)
        else:
            # Long text - show truncated
            self._show_static(cleaned, duration)
    
    def _show_static(self, text: str, duration: float):
        """Display static text (no scrolling)"""
        line1, line2, has_more = self.split_text_smart(text)
        
        self.display.clear()
        
        # Center short text
        if len(line1) < self.max_cols:
            col1 = (self.max_cols - len(line1)) // 2
        else:
            col1 = 0
            
        if len(line2) < self.max_cols:
            col2 = (self.max_cols - len(line2)) // 2
        else:
            col2 = 0
        
        self.display.write_text(line1, row=0, col=col1)
        if line2:
            display_line2 = line2 + ".." if has_more else line2
            self.display.write_text(display_line2, row=1, col=col2)
        
        time.sleep(duration)
    
    def _show_scrolling(self, text: str, duration: float):
        """Display long text with scrolling"""
        # Split into words
        words = text.split()
        
        # Calculate how many screens we need
        start_time = time.time()
        word_index = 0
        
        while (time.time() - start_time) < duration and word_index < len(words):
            line1 = ""
            line2 = ""
            
            # Fill line 1
            while word_index < len(words) and len(line1) + len(words[word_index]) + 1 <= self.max_cols:
                line1 += words[word_index] + " "
                word_index += 1
            
            # Fill line 2
            while word_index < len(words) and len(line2) + len(words[word_index]) + 1 <= self.max_cols:
                line2 += words[word_index] + " "
                word_index += 1
            
            # Display current screen
            self.display.clear()
            self.display.write_text(line1.strip(), row=0, col=0)
            if line2.strip():
                self.display.write_text(line2.strip(), row=1, col=0)
            
            # Show indicator if more text
            if word_index < len(words):
                # Add >> indicator on line 2
                if len(line2.strip()) < self.max_cols - 2:
                    self.display.write_text(">>", row=1, col=self.max_cols-2)
            
            time.sleep(self.scroll_delay)
        
        # Show completion indicator briefly
        if word_index >= len(words):
            time.sleep(0.3)
    
    def show_result(self, command: str, result: str, duration: float = 4.0):
        """
        Show command result in a formatted way
        Line 1: Command name (centered)
        Line 2: Result (scrolling if needed)
        """
        # Clean texts
        cmd_clean = self.clean_text(command)[:self.max_cols]
        result_clean = self.clean_text(result)
        
        # Show command
        self.display.clear()
        cmd_col = max(0, (self.max_cols - len(cmd_clean)) // 2)
        self.display.write_text(cmd_clean, row=0, col=cmd_col)
        time.sleep(0.8)
        
        # Show result
        if len(result_clean) <= self.max_cols:
            result_col = max(0, (self.max_cols - len(result_clean)) // 2)
            self.display.write_text(result_clean, row=1, col=result_col)
            time.sleep(duration)
        else:
            # Scroll result on line 2
            self._scroll_line2(result_clean, duration)
    
    def _scroll_line2(self, text: str, duration: float):
        """Scroll text on line 2 only"""
        start_time = time.time()
        pos = 0
        
        while (time.time() - start_time) < duration:
            if pos + self.max_cols <= len(text):
                segment = text[pos:pos + self.max_cols]
            else:
                # Wrap around
                segment = text[pos:] + " | " + text[:self.max_cols - len(text[pos:]) - 3]
            
            self.display.write_text(segment, row=1, col=0)
            time.sleep(self.scroll_delay)
            pos += 1
            
            # Reset position for continuous scrolling
            if pos >= len(text) + 3:
                pos = 0
    
    def show_thinking(self):
        """Show thinking indicator"""
        self.display.clear()
        self.display.write_text("Processing...", row=0, col=2)
        self.display.show_face('thinking')
    
    def show_listening(self):
        """Show listening indicator"""
        self.display.clear()
        self.display.write_text("Listening...", row=0, col=3)
        self.display.show_face('listening')
    
    def show_speaking(self):
        """Show speaking indicator"""
        self.display.clear()
        self.display.write_text("Speaking...", row=0, col=3)
        self.display.show_face('happy')
    
    def show_error(self, error: str):
        """Show error message"""
        self.display.clear()
        self.display.write_text("Error!", row=0, col=5)
        self.display.show_face('sad')
        time.sleep(0.5)
        
        # Show error details
        error_clean = self.clean_text(error)
        self.show_response(error_clean, duration=3.0)

# Create singleton instance
display_handler = DisplayResponseHandler()

# Convenience functions
def show_response(text: str, duration: float = 5.0, scroll: bool = True):
    """Show AI response on display"""
    display_handler.show_response(text, duration, scroll)

def show_result(command: str, result: str, duration: float = 4.0):
    """Show command result"""
    display_handler.show_result(command, result, duration)

def show_thinking():
    """Show thinking indicator"""
    display_handler.show_thinking()

def show_listening():
    """Show listening indicator"""
    display_handler.show_listening()

def show_speaking():
    """Show speaking indicator"""
    display_handler.show_speaking()

def show_error(error: str):
    """Show error message"""
    display_handler.show_error(error)
