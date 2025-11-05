"""
Infrared (IR) Emitter for Jarvis.

This module uses the `irsend` command-line tool, which is part of the LIRC
package, to send (emit) IR codes. This allows Jarvis to control other
devices like TVs, stereos, etc.

It can learn new remote commands and save them to a LIRC configuration file.
"""

import os
import subprocess
import json
import time

class IREmitter:
    def __init__(self, lircd_conf_path="/etc/lirc/lircd.conf.d/jarvis_remotes.conf"):
        self.lircd_conf_path = lircd_conf_path
        self.remotes = self._load_remotes_from_conf()

    def _load_remotes_from_conf(self):
        """
        Parses the LIRC configuration file to find defined remotes and their commands.
        This is a simplified parser and might not handle all lircd.conf complexities.
        """
        remotes = {}
        if not os.path.exists(self.lircd_conf_path):
            return remotes

        with open(self.lircd_conf_path, 'r') as f:
            current_remote = None
            for line in f:
                line = line.strip()
                if "begin remote" in line:
                    current_remote = None
                elif "name" in line and current_remote is None:
                    parts = line.split()
                    if len(parts) > 1:
                        remote_name = parts[1]
                        remotes[remote_name] = []
                        current_remote = remote_name
                elif "begin codes" in line:
                    continue
                elif "end codes" in line:
                    continue
                elif "end remote" in line:
                    current_remote = None
                elif current_remote and len(line.split()) > 1:
                    # Assuming the first word on the line is the key name
                    key_name = line.split()[0]
                    if key_name.startswith("0x"): continue # Skip raw codes
                    remotes[current_remote].append(key_name)
        return remotes

    def list_remotes(self):
        """Returns a list of configured remote names."""
        return list(self.remotes.keys())

    def list_commands(self, remote_name):
        """Returns a list of commands for a given remote."""
        return self.remotes.get(remote_name, [])

    def send_once(self, remote_name, command_name):
        """
        Sends an IR command once.

        Args:
            remote_name (str): The name of the remote (e.g., 'TV').
            command_name (str): The name of the command (e.g., 'KEY_POWER').

        Returns:
            tuple(bool, str): (success, message)
        """
        if remote_name not in self.remotes:
            return False, f"Error: Remote '{remote_name}' not found."
        if command_name not in self.remotes[remote_name]:
            return False, f"Error: Command '{command_name}' not found for remote '{remote_name}'."

        try:
            cmd = ["irsend", "SEND_ONCE", remote_name, command_name]
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            return True, f"Successfully sent {command_name} for {remote_name}."
        except FileNotFoundError:
            return False, "Error: 'irsend' command not found. Is LIRC installed and in the system's PATH?"
        except subprocess.CalledProcessError as e:
            return False, f"Error sending command: {e.stderr}"

    def learn_command(self, remote_name, command_name):
        """
        Puts the system in learning mode to record a new command.
        This is an interactive process that requires user intervention.

        Returns:
            tuple(bool, str): (success, message)
        """
        print(f"\n--- Interactive IR Command Learning ---")
        print(f"Remote: {remote_name}, Command: {command_name}")
        print("Please point your remote at the IR receiver and press the button for '{command_name}'.")
        print("This will block for up to 30 seconds...")

        try:
            # Stop lircd to allow irrecord to access the hardware
            subprocess.run(["sudo", "systemctl", "stop", "lircd"], check=True)
            time.sleep(1)

            # Use irrecord to learn the command.
            # We create a temporary config file for the new key.
            temp_conf_file = f"/tmp/{remote_name}.lircd.conf"
            
            # The --disable-namespace is important to get clean key names
            irrecord_cmd = [
                "irrecord",
                "--device", "/dev/lirc0",
                "--disable-namespace",
                temp_conf_file
            ]

            # This is a simplified interaction. `irrecord` is a complex interactive tool.
            # A more robust solution might use pexpect.
            # For now, we rely on the user to follow the prompts in the main terminal.
            print("\nStarting `irrecord`. Please follow the instructions in your terminal.")
            print("You will be asked to press buttons. When prompted for a name, enter EXACTLY:")
            print(f"    {command_name}")
            print("Then, press the button on the remote again.")
            print("When you are done, just press Enter to get to the save & exit prompt.")
            
            # We can't fully automate irrecord easily, so we just launch it.
            # The user must interact with it in the terminal where Jarvis is running.
            process = subprocess.run(irrecord_cmd, text=True)

            if process.returncode != 0:
                return False, "irrecord process failed. Please check the terminal for errors."

            # Now, append the newly created config to the main one.
            if os.path.exists(temp_conf_file):
                with open(temp_conf_file, 'r') as f:
                    new_conf_data = f.read()
                
                # We need to append this to our main config file
                with open(self.lircd_conf_path, 'a') as f:
                    f.write("\n")
                    f.write(new_conf_data)
                
                os.remove(temp_conf_file)
                
                # Reload remotes and restart lircd
                self.remotes = self._load_remotes_from_conf()
                subprocess.run(["sudo", "systemctl", "start", "lircd"], check=True)
                
                return True, f"Successfully learned and saved '{command_name}' for '{remote_name}'. LIRC has been restarted."
            else:
                subprocess.run(["sudo", "systemctl", "start", "lircd"], check=True)
                return False, "Learning process did not create a config file. Aborted."

        except Exception as e:
            # Make sure lircd is restarted even if something fails
            subprocess.run(["sudo", "systemctl", "start", "lircd"])
            return False, f"An error occurred during learning: {e}"

if __name__ == '__main__':
    emitter = IREmitter()
    print("Available remotes:", emitter.list_remotes())
    
    # Example: send a command
    # success, message = emitter.send_once('TV', 'KEY_POWER')
    # print(message)

    # Example: learn a new command
    # This is interactive and will require you to follow prompts in the terminal.
    # success, message = emitter.learn_command('MyNewRemote', 'KEY_MUTE')
    # print(message)
