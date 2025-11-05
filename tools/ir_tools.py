"""
Tools for interacting with Infrared (IR) devices.
"""
from langchain.tools import tool
from actuators.ir_emitter import IREmitter
from actuators.ir_receiver import IRReceiver
import threading
import time

# Singleton instances
ir_emitter = IREmitter()

# --- IR Emitter Tools ---

@tool("ir_list_remotes", return_direct=True)
def ir_list_remotes(_) -> str:
    """
    Lists all configured IR remote controls that Jarvis can use to send commands.
    """
    remotes = ir_emitter.list_remotes()
    if not remotes:
        return "No IR remotes are configured yet. Use `ir_learn_command` to add one."
    return "Available remotes: " + ", ".join(remotes)

@tool("ir_list_commands", return_direct=True)
def ir_list_commands(remote_name: str) -> str:
    """
    Lists the available commands for a specific IR remote.
    - remote_name (str): The name of the remote to query.
    """
    commands = ir_emitter.list_commands(remote_name)
    if not commands:
        return f"No commands found for remote '{remote_name}', or the remote does not exist."
    return f"Available commands for {remote_name}: " + ", ".join(commands)

@tool("ir_send_command", return_direct=True)
def ir_send_command(command_str: str) -> str:
    """
    Sends an IR command. The input must be a string with the remote name and the command name, separated by a comma.
    For example: 'TV, KEY_POWER'.
    """
    parts = command_str.split(',')
    if len(parts) != 2:
        return "Invalid format. Please provide the remote name and command, separated by a comma (e.g., 'TV, KEY_POWER')."
    
    remote_name = parts[0].strip()
    command_name = parts[1].strip()
    
    success, message = ir_emitter.send_once(remote_name, command_name)
    return message

@tool("ir_learn_command", return_direct=True)
def ir_learn_command(command_str: str) -> str:
    """
    Starts the interactive process to learn a new IR command. The input must be a string with the new remote name and command name, separated by a comma.
    For example: 'Stereo, KEY_MUTE'.
    This requires the user to be physically present to press the remote button.
    """
    parts = command_str.split(',')
    if len(parts) != 2:
        return "Invalid format. Please provide the remote name and command, separated by a comma (e.g., 'Stereo, KEY_MUTE')."

    remote_name = parts[0].strip()
    command_name = parts[1].strip()

    # This tool returns a message to the user to guide them, as the actual learning
    # happens interactively in the terminal.
    
    # We can't run the learning in a separate thread easily because it's interactive.
    # So we just return the instructions. The user must see the terminal output.
    
    print("\n" + "="*50)
    print("  Starting IR Learning Mode via `irrecord`")
    print("  You must follow the prompts in this terminal.")
    print(f"  Learning command '{command_name}' for remote '{remote_name}'.")
    print("="*50 + "\n")

    success, message = ir_emitter.learn_command(remote_name, command_name)
    
    print("\n" + "="*50)
    print("  Exited IR Learning Mode")
    print(f"  Result: {message}")
    print("="*50 + "\n")

    return f"Learning process finished. Result: {message}"
