"""
Tools for controlling the robot's movement.
"""
from langchain.tools import tool
from actuators.motor_controller import MotorController

# It's better to have a single instance of the controller
# that the tools can share.
motor_controller = MotorController()

@tool("move_forward", return_direct=True)
def move_forward(duration: float, speed: int = 80) -> str:
    """
    Moves the robot forward for a specified duration in seconds.
    - duration (float): How long to move forward in seconds.
    - speed (int): The speed of the motors, from 0 to 100. Default is 80.
    """
    motor_controller.forward(speed=speed, duration=duration)
    return f"Moved forward for {duration} seconds at {speed}% speed."

@tool("move_backward", return_direct=True)
def move_backward(duration: float, speed: int = 80) -> str:
    """
    Moves the robot backward for a specified duration in seconds.
    - duration (float): How long to move backward in seconds.
    - speed (int): The speed of the motors, from 0 to 100. Default is 80.
    """
    motor_controller.backward(speed=speed, duration=duration)
    return f"Moved backward for {duration} seconds at {speed}% speed."

@tool("turn_left", return_direct=True)
def turn_left(duration: float, speed: int = 70) -> str:
    """
    Turns the robot left on the spot for a specified duration in seconds.
    - duration (float): How long to turn in seconds.
    - speed (int): The speed of the motors, from 0 to 100. Default is 70.
    """
    motor_controller.left(speed=speed, duration=duration)
    return f"Turned left for {duration} seconds at {speed}% speed."

@tool("turn_right", return_direct=True)
def turn_right(duration: float, speed: int = 70) -> str:
    """
    Turns the robot right on the spot for a specified duration in seconds.
    - duration (float): How long to turn in seconds.
    - speed (int): The speed of the motors, from 0 to 100. Default is 70.
    """
    motor_controller.right(speed=speed, duration=duration)
    return f"Turned right for {duration} seconds at {speed}% speed."

@tool("stop_moving", return_direct=True)
def stop_moving() -> str:
    """
    Stops all motor movement immediately.
    """
    motor_controller.stop()
    return "Robot has stopped moving."
