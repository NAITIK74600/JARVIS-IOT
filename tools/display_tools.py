"""
Tools for controlling the 16x2 LCD character display.
"""
from langchain.tools import tool
from actuators.display import display

@tool("display_text", return_direct=True)
def display_text(text: str) -> str:
    """
    Displays text on the 16x2 LCD screen. The text will automatically wrap if it is too long for one line.
    - text (str): The text to display.
    """
    try:
        display.clear()
        display.write_text(text)
        return f"Displayed on screen: '{text}'"
    except Exception as e:
        return f"Error displaying text: {e}"

@tool("clear_display", return_direct=True)
def clear_display(_) -> str:
    """
    Clears the LCD screen.
    """
    try:
        display.clear()
        return "LCD screen cleared."
    except Exception as e:
        return f"Error clearing display: {e}"

@tool("show_face", return_direct=True)
def show_face(face_name: str) -> str:
    """
    Displays a predefined facial expression on the LCD screen.
    Valid faces are: 'neutral', 'happy', 'sad', 'thinking', 'listening'.
    - face_name (str): The name of the face to display.
    """
    valid_faces = ['neutral', 'happy', 'sad', 'thinking', 'listening']
    if face_name not in valid_faces:
        return f"Invalid face name. Please use one of: {', '.join(valid_faces)}"
    
    try:
        display.show_face(face_name)
        return f"Displaying '{face_name}' face."
    except Exception as e:
        return f"Error showing face: {e}"
