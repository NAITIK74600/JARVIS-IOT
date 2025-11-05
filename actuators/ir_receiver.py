"""
Infrared (IR) Receiver for Jarvis.

This module uses the LIRC (Linux Infrared Remote Control) library to listen
for IR commands. It runs in a background thread and can invoke callbacks
when specific buttons are pressed.

Requires:
- LIRC installed and configured (`sudo apt-get install lirc`).
- A lircrc file (default ~/.lircrc) mapping remote buttons to actions.
- An IR receiver connected to the configured GPIO pin (see /boot/config.txt).
"""

import lirc
import threading
import time
import os

class IRReceiver:
    def __init__(self, lircrc_path="~/.lircrc"):
        self.lircrc_path = os.path.expanduser(lircrc_path)
        self.thread = None
        self.is_running = False
        self.callback = None

        # The blocking parameter in lirc.init is crucial.
        # We set it to False and manage our own loop to allow for graceful shutdown.
        try:
            self.sock = lirc.init("jarvis_ir", self.lircrc_path, blocking=False)
            print(f"IR Receiver initialized using config: {self.lircrc_path}")
        except Exception as e:
            self.sock = None
            print(f"Error: Could not initialize LIRC. IR receiver will be disabled. Error: {e}")
            print("Ensure LIRC is running and you have permission to access /var/run/lirc/lircd.")

    def start(self, callback):
        """
        Starts the IR listener thread.

        Args:
            callback (function): A function to call when an IR code is received.
                                 It will be called with the received code (list of strings).
        """
        if not self.sock:
            print("Cannot start IR receiver: LIRC not initialized.")
            return

        if self.is_running:
            print("IR receiver thread is already running.")
            return

        self.callback = callback
        self.is_running = True
        self.thread = threading.Thread(target=self._listen, daemon=True)
        self.thread.start()
        print("IR receiver thread started.")

    def _listen(self):
        """The main listening loop that runs in a separate thread."""
        while self.is_running:
            try:
                codes = lirc.nextcode()  # This is non-blocking
                if codes and self.callback:
                    # codes is a list of strings, e.g., ['KEY_POWER']
                    self.callback(codes)
            except lirc.LircdConnectionError as e:
                print(f"LIRC connection error: {e}. Retrying in 5 seconds...")
                time.sleep(5)
                # Attempt to re-initialize
                try:
                    self.sock = lirc.init("jarvis_ir", self.lircrc_path, blocking=False)
                except Exception as re_e:
                    print(f"Failed to re-initialize LIRC: {re_e}")
                    self.is_running = False # Stop trying
            except Exception as e:
                print(f"An unexpected error occurred in IR listener: {e}")
                self.is_running = False
            
            time.sleep(0.1) # Prevent busy-waiting

    def stop(self):
        """Stops the IR listener thread."""
        if not self.is_running:
            return
            
        print("Stopping IR receiver thread...")
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=2)
        
        if self.sock:
            lirc.deinit()
        
        print("IR receiver thread stopped.")

if __name__ == '__main__':
    # Example usage
    
    # Create a dummy .lircrc file for testing
    lircrc_content = """
    begin
        prog = jarvis_ir
        button = KEY_POWER
        config = Power button pressed
    end
    begin
        prog = jarvis_ir
        button = KEY_VOLUMEUP
        config = Volume Up
    end
    """
    with open(".lircrc_test", "w") as f:
        f.write(lircrc_content)

    def my_ir_callback(codes):
        print(f"Received IR command: {codes[0]}")

    print("Starting IR receiver example. Press buttons on your remote.")
    print("This test requires a remote configured with LIRC and a .lircrc file.")
    print("A dummy .lircrc_test file has been created.")
    
    # Point to the test file
    receiver = IRReceiver(lircrc_path=".lircrc_test")
    
    if receiver.sock:
        receiver.start(my_ir_callback)
        try:
            # Keep the main thread alive
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down...")
        finally:
            receiver.stop()
            os.remove(".lircrc_test")
    else:
        print("Exiting because LIRC could not be initialized.")
