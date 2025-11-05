import sys
import os
import time

# Add the project root to the Python path to allow for absolute imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from actuators.servo import Servo
from core.hardware_manager import hardware_manager

def test_servo_functionality():
    """
    This function tests the servo motor by sweeping it from 0 to 180 degrees
    and then returning it to the center position.
    """
    # The servo is connected to BCM pin 12
    servo_pin = 12 
    
    print("Initializing servo for testing...")
    # The HardwareManager will handle simulation mode automatically.
    servo = Servo(pin=servo_pin)

    try:
        print("\n--- Starting Servo Sweep Test ---")
        
        print("Moving to 0 degrees...")
        servo.set_angle(0)
        time.sleep(1.5)

        print("Moving to 90 degrees (center)...")
        servo.set_angle(90)
        time.sleep(1.5)

        print("Moving to 180 degrees...")
        servo.set_angle(180)
        time.sleep(1.5)
        
        print("Returning to 90 degrees (center)...")
        servo.set_angle(90)
        time.sleep(1)
        
        print("\n--- Servo Sweep Test Complete ---")

    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
    except Exception as e:
        print(f"\nAn error occurred during the test: {e}")
    finally:
        # The HardwareManager handles the final GPIO cleanup automatically
        # when the script exits. We don't need to call servo.cleanup() here.
        print("Test script finished. HardwareManager will handle cleanup.")

if __name__ == "__main__":
    test_servo_functionality()
