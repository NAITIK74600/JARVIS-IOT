"""
Tools for controlling the robot's movement.
"""
import os
import sys

# Add parent directory to path for standalone execution
if __name__ == "__main__":
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)

try:
    from langchain_core.tools import tool
except ImportError:
    from langchain.tools import tool

from actuators.motor_controller import MotorController

# It's better to have a single instance of the controller
# that the tools can share.
motor_controller = MotorController()

@tool
def move_forward(duration: str = "2") -> str:
    """
    Moves the robot forward for a specified duration in seconds.
    Input: duration as string (e.g., '2' for 2 seconds). Default is 2 seconds.
    Use this when asked to 'move forward', 'go forward', 'aage jao', or similar.
    """
    try:
        dur = float(duration) if duration else 2.0
        speed = 80
        motor_controller.forward(speed=speed, duration=dur)
        return f"Moved forward for {dur} seconds at {speed}% speed."
    except ValueError:
        return "Invalid duration. Please provide a number."

@tool
def move_backward(duration: str = "2") -> str:
    """
    Moves the robot backward for a specified duration in seconds.
    Input: duration as string (e.g., '2' for 2 seconds). Default is 2 seconds.
    Use this when asked to 'move back', 'go back', 'peeche jao', or similar.
    """
    try:
        dur = float(duration) if duration else 2.0
        speed = 80
        motor_controller.backward(speed=speed, duration=dur)
        return f"Moved backward for {dur} seconds at {speed}% speed."
    except ValueError:
        return "Invalid duration. Please provide a number."

@tool
def turn_left(duration: str = "1") -> str:
    """
    Turns the robot left on the spot for a specified duration in seconds.
    Input: duration as string (e.g., '1' for 1 second). Default is 1 second.
    Use this when asked to 'turn left', 'baen mud', 'left side', or similar.
    """
    try:
        dur = float(duration) if duration else 1.0
        speed = 70
        motor_controller.left(speed=speed, duration=dur)
        return f"Turned left for {dur} seconds at {speed}% speed."
    except ValueError:
        return "Invalid duration. Please provide a number."

@tool
def turn_right(duration: str = "1") -> str:
    """
    Turns the robot right on the spot for a specified duration in seconds.
    Input: duration as string (e.g., '1' for 1 second). Default is 1 second.
    Use this when asked to 'turn right', 'daen mud', 'right side', or similar.
    """
    try:
        dur = float(duration) if duration else 1.0
        speed = 70
        motor_controller.right(speed=speed, duration=dur)
        return f"Turned right for {dur} seconds at {speed}% speed."
    except ValueError:
        return "Invalid duration. Please provide a number."

@tool
def stop_moving(_: str = "") -> str:
    """
    Stops all motor movement immediately.
    Use this when asked to 'stop', 'ruko', 'halt', or 'freeze'.
    """
    motor_controller.stop()
    return "Robot has stopped moving."


# Test section when run directly
if __name__ == "__main__":
    import time
    
    print("=" * 60)
    print("MOTOR TOOLS TEST")
    print("=" * 60)
    print(f"\nMotor Controller Status:")
    print(f"  Simulation Mode: {motor_controller.simulation_mode}")
    print(f"  Left Motor:  EN=GPIO{motor_controller.L_EN}, IN1=GPIO{motor_controller.L_IN1}, IN2=GPIO{motor_controller.L_IN2}")
    print(f"  Right Motor: EN=GPIO{motor_controller.R_EN}, IN1=GPIO{motor_controller.R_IN1}, IN2=GPIO{motor_controller.R_IN2}")
    
    print("\n" + "=" * 60)
    print("Testing all motor tool functions...")
    print("=" * 60)
    
    try:
        print("\n[1/5] Testing move_forward(2)...")
        result = move_forward("2")
        print(f"     Result: {result}")
        time.sleep(1)
        
        print("\n[2/5] Testing move_backward(2)...")
        result = move_backward("2")
        print(f"     Result: {result}")
        time.sleep(1)
        
        print("\n[3/5] Testing turn_left(1)...")
        result = turn_left("1")
        print(f"     Result: {result}")
        time.sleep(1)
        
        print("\n[4/5] Testing turn_right(1)...")
        result = turn_right("1")
        print(f"     Result: {result}")
        time.sleep(1)
        
        print("\n[5/5] Testing stop_moving()...")
        result = stop_moving("")
        print(f"     Result: {result}")
        
        print("\n" + "=" * 60)
        print("✓ ALL MOTOR TOOLS TESTED SUCCESSFULLY!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        print("\nCleaning up...")
        try:
            motor_controller.cleanup()
            print("✓ Motor controller cleaned up")
        except Exception as e:
            print(f"⚠ Cleanup warning: {e}")
        
        try:
            from core.hardware_manager import hardware_manager
            hardware_manager.cleanup()
            print("✓ Hardware manager cleaned up")
        except Exception as e:
            print(f"⚠ Hardware cleanup warning: {e}")
