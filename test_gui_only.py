#!/usr/bin/env python3
"""
Test if JARVIS GUI opens and stays open
"""
import tkinter as tk
from tkinter import font, scrolledtext
import queue
import time

class TestJarvisGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("JARVIS GUI Test")
        
        # Window config
        w, h = 500, 650
        sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
        px, py = (sw // 2) - (w // 2), (sh // 2) - (h // 2)
        self.root.geometry(f"{w}x{h}+{px}+{py}")
        
        # Styling
        self.bg_color = "#2E2E2E"
        self.text_area_bg = "#1E1E1E"
        self.entry_bg = "#3C3C3C"
        self.text_fg = "#E0E0E0"
        self.button_bg = "#007ACC"
        self.root.configure(bg=self.bg_color)
        
        # Main frame
        self.main_frame = tk.Frame(root, bg=self.bg_color)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Log area
        self.main_font = font.Font(family="Monospace", size=10)
        self.log_area = scrolledtext.ScrolledText(
            self.main_frame,
            wrap=tk.WORD,
            bg=self.text_area_bg,
            fg=self.text_fg,
            font=self.main_font,
            state='disabled'
        )
        self.log_area.pack(pady=5, fill=tk.BOTH, expand=True)
        
        # Input frame
        self.input_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        self.input_frame.pack(fill=tk.X, pady=5)
        
        self.entry = tk.Entry(
            self.input_frame,
            bg=self.entry_bg,
            fg=self.text_fg,
            font=self.main_font,
            insertbackground=self.text_fg
        )
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5)
        self.entry.bind("<Return>", self.on_send)
        
        self.send_button = tk.Button(
            self.input_frame,
            text="Send",
            command=self.on_send,
            bg=self.button_bg,
            fg=self.text_fg
        )
        self.send_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Status bar
        self.status_bar = tk.Label(
            self.main_frame,
            text="GUI Test - Ready",
            font=self.main_font,
            bg=self.bg_color,
            fg=self.text_fg,
            anchor='w'
        )
        self.status_bar.pack(fill=tk.X)
        
        # Log test messages
        self.log_message("✅ GUI initialized successfully!")
        self.log_message("✅ Window is displaying properly")
        self.log_message("✅ Text input is ready")
        self.log_message("")
        self.log_message("Type something and press Enter to test input...")
    
    def log_message(self, msg):
        """Add message to log area"""
        self.log_area.configure(state='normal')
        self.log_area.insert(tk.END, msg + "\n")
        self.log_area.configure(state='disabled')
        self.log_area.see(tk.END)
    
    def on_send(self, event=None):
        """Handle send button/enter key"""
        text = self.entry.get()
        if text:
            self.log_message(f"You typed: {text}")
            self.entry.delete(0, tk.END)
            
            if text.lower() in ['exit', 'quit', 'bye']:
                self.log_message("Closing GUI...")
                self.root.after(1000, self.root.destroy)

def main():
    print("Creating Tkinter window...")
    root = tk.Tk()
    print("Initializing GUI...")
    app = TestJarvisGUI(root)
    print("Starting main loop...")
    print("Window should be visible now!")
    root.mainloop()
    print("GUI closed.")

if __name__ == "__main__":
    main()
