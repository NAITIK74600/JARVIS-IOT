# In tools/automation_tools.py
from langchain_core.tools import tool
import pyautogui
import time

@tool
def click_on_screen(x: int, y: int) -> str:
    """
    Moves the mouse to the specified (x, y) coordinates on the screen and clicks.
    Args:
        x (int): The x-coordinate.
        y (int): The y-coordinate.
    """
    try:
        pyautogui.click(x, y)
        return f"Successfully clicked at coordinates ({x}, {y})."
    except Exception as e:
        return f"Error clicking on screen: {e}"

@tool
def type_text(text: str) -> str:
    """
    Types the given text at the current cursor position.
    Args:
        text (str): The text to type.
    """
    try:
        pyautogui.write(text, interval=0.05)
        return f"Successfully typed: '{text}'"
    except Exception as e:
        return f"Error typing text: {e}"

@tool
def press_key(key: str) -> str:
    """
    Presses a special key on the keyboard (e.g., 'enter', 'win', 'ctrl', 'shift', 'pagedown').
    For a list of valid key names, see the pyautogui documentation.
    Args:
        key (str): The name of the key to press.
    """
    try:
        pyautogui.press(key)
        return f"Successfully pressed the '{key}' key."
    except Exception as e:
        return f"Error pressing key: {e}"

@tool
def open_application(application_name: str) -> str:
    """
    Opens an application by searching for it in the start menu.
    This is for Windows only.
    Args:
        application_name (str): The name of the application to open (e.g., 'notepad', 'chrome').
    """
    try:
        pyautogui.press('win')
        time.sleep(1)
        pyautogui.write(application_name)
        time.sleep(1)
        pyautogui.press('enter')
        return f"Successfully attempted to open '{application_name}'."
    except Exception as e:
        return f"Error opening application: {e}"

# Aliases for backward compatibility
@tool
def get_installed_apps(_: str = "") -> str:
    """Lists installed applications (placeholder - not fully implemented on this platform)."""
    return "Application listing is not available on this platform. Use launch_app to open known applications."

launch_app = open_application

def get_automation_tools():
    return [click_on_screen, type_text, press_key, open_application, get_installed_apps]