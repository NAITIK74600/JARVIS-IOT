"""
This module provides tools for controlling the robot's physical movements and gestures.
"""

from langchain.agents import tool
from core.body_language import BodyLanguage
from actuators.multi_servo_controller import multi_servo_controller

# Initialize BodyLanguage module
body_language = BodyLanguage(multi_servo_controller)

@tool
def perform_gesture(gesture_name: str) -> str:
    """
    Performs a pre-programmed body gesture.
    Available gestures: 'nod', 'shake_head', 'wave_right', 'wave_left', 'raise_hands', 'agree', 'disagree', 'think'
    """
    try:
        if hasattr(body_language, gesture_name):
            getattr(body_language, gesture_name)()
            return f"Gesture '{gesture_name}' performed successfully."
        else:
            return f"Error: Gesture '{gesture_name}' not found."
    except Exception as e:
        return f"An error occurred while performing gesture '{gesture_name}': {e}"

@tool
def set_servo_position(params: str) -> str:
    """
    Sets a single servo to a specific angle.
    Input format: "servo_name,angle" (e.g., "neck,90").
    Servo names: 'neck', 'arm_l', 'arm_r'.
    Angle: 0-180.
    """
    try:
        servo_name, angle_str = params.split(',')
        angle = int(angle_str)
        multi_servo_controller.set_angle(servo_name.strip(), angle)
        return f"Servo '{servo_name.strip()}' set to {angle} degrees."
    except Exception as e:
        return f"An error occurred: {e}. Use format 'servo_name,angle'."

@tool
def center_all_servos(_: str = "") -> str:
    """Centers all servos to their default 90-degree position."""
    try:
        body_language.center_all()
        return "All servos have been centered."
    except Exception as e:
        return f"An error occurred while centering servos: {e}"

all_robot_tools = [
    perform_gesture,
    set_servo_position,
    center_all_servos,
]
