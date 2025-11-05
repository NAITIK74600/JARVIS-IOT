# H:/jarvis/tools/system_tools.py (CORRECTED)

import os
import platform
import subprocess
import json
import psutil
from langchain_core.tools import tool

try:
    with open("app_index.json", "r") as f:
        APP_INDEX = json.load(f)
except FileNotFoundError:
    APP_INDEX = {}

@tool
def open_application(app_name: str) -> str:
    """Opens a specified desktop application by its common name.""" # <<< DOCSTRING RESTORED
    name = (app_name or "").strip().lower()
    if not name: return "Error: Please specify an application name."
    if name in APP_INDEX:
        try:
            subprocess.Popen(APP_INDEX[name])
            return f"Successfully launched {app_name} from the index."
        except Exception as e: return f"Found '{app_name}' in the index, but failed to launch it: {e}"
    try:
        subprocess.run(f"start {name}", shell=True, check=True)
        return f"Successfully started {app_name}."
    except Exception as e: return f"Error opening '{app_name}': {e}"

@tool
def execute_terminal_command(command: str, confirm: bool) -> str:
    """
    Executes any command in the Windows PowerShell terminal.
    THIS IS A POWERFUL AND POTENTIALLY DANGEROUS TOOL.
    For any command that modifies or deletes files or changes system settings,
    you MUST ask the user for confirmation by setting the 'confirm' parameter to True.
    Args:
        command (str): The exact command to execute.
        confirm (bool): Whether the user has confirmed the action. Must be True for dangerous commands.
    """
    if not confirm:
        return "CRITICAL: This action requires user confirmation. Ask the user to confirm before proceeding."
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        output = result.stdout or "Command executed successfully with no output."
        return f"Execution successful.\nOutput:\n---\n{output}\n---"
    except subprocess.CalledProcessError as e:
        return f"Command failed with error:\n---\n{e.stderr}\n---"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

@tool
def get_os_version() -> str:
    """Returns the operating system version."""
    return f"OS: {platform.system()} {platform.release()}"

@tool
def get_cpu_usage() -> str:
    """Returns the current CPU usage as a percentage."""
    return f"CPU Usage: {psutil.cpu_percent()}%"

@tool
def get_ram_usage() -> str:
    """Returns the current RAM usage."""
    ram = psutil.virtual_memory()
    return f"RAM Usage: {ram.percent}% (Used: {ram.used / (1024**3):.2f} GB, Total: {ram.total / (1024**3):.2f} GB)"

def get_system_tools():
    return [open_application, execute_terminal_command, get_os_version, get_cpu_usage, get_ram_usage]