#!/usr/bin/env python3
"""
Neck Servo Control Script
Simple interactive script to control the neck servo by entering angle values.
"""
from actuators.multi_servo_controller import multi_servo_controller
import time

def main():
    print("="*60)
    print("NECK SERVO CONTROL")
    print("="*60)
    
    # Get neck servo
    neck = multi_servo_controller.get_servo('neck')
    
    if not neck:
        print("ERROR: Neck servo not found!")
        return
    
    print(f"Neck Servo: GPIO 18 (BCM)")
    print(f"Valid Range: 0° to 180°")
    print(f"Current Position: {neck.current_angle if neck.current_angle else 'Unknown'}°")
    print()
    print("Commands:")
    print("  - Enter angle (0-180) to move neck")
    print("  - Type 'center' or 'c' for 90°")
    print("  - Type 'left' or 'l' for 0°")
    print("  - Type 'right' or 'r' for 180°")
    print("  - Type 'quit' or 'q' to exit")
    print("="*60)
    print()
    
    while True:
        try:
            user_input = input("Enter angle or command: ").strip().lower()
            
            # Check for quit command
            if user_input in ['quit', 'q', 'exit']:
                print("\nExiting...")
                break
            
            # Check for preset commands
            if user_input in ['center', 'c']:
                angle = 90
                print(f"Moving to CENTER (90°)...")
            elif user_input in ['left', 'l']:
                angle = 0
                print(f"Moving to FULL LEFT (0°)...")
            elif user_input in ['right', 'r']:
                angle = 180
                print(f"Moving to FULL RIGHT (180°)...")
            else:
                # Try to parse as number
                try:
                    angle = int(user_input)
                except ValueError:
                    print("❌ Invalid input. Please enter a number between 0-180 or a valid command.")
                    continue
            
            # Validate angle range
            if angle < 0 or angle > 180:
                print(f"❌ Angle {angle}° is out of range. Must be between 0° and 180°.")
                continue
            
            # Move servo
            neck.set_angle(angle)
            time.sleep(0.5)  # Give servo time to move
            
            print(f"✓ Neck moved to {neck.current_angle}°")
            print()
            
        except KeyboardInterrupt:
            print("\n\nInterrupted by user.")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            continue
    
    # Return to center before exit
    print("\nReturning to center position...")
    neck.set_angle(90)
    time.sleep(0.5)
    print("✓ Done!")
    print("="*60)

if __name__ == '__main__':
    main()
