#!/usr/bin/env python3
"""
JARVIS Servo Motor Control for Raspberry Pi
This script controls servo motors for Jarvis's neck and hands
"""

import RPi.GPIO as GPIO
import time

# Configuration - JARVIS Servo Motors
SERVO_PINS = {
    'neck': 18,        # GPIO pin for Neck (head rotation)
    'left_hand': 23,   # GPIO pin for Left Hand
    'right_hand': 24   # GPIO pin for Right Hand
}
SERVO_FREQUENCY = 50  # 50Hz for standard servos

def setup_servos(pins):
    """
    Initialize GPIO and setup PWM for multiple servos
    
    Args:
        pins: Dictionary of servo names and their GPIO pins
    
    Returns:
        Dictionary of PWM objects
    """
    GPIO.setmode(GPIO.BCM)
    pwm_servos = {}
    
    for name, pin in pins.items():
        GPIO.setup(pin, GPIO.OUT)
        pwm = GPIO.PWM(pin, SERVO_FREQUENCY)
        pwm.start(0)  # Start with 0% duty cycle
        pwm_servos[name] = pwm
        print(f"Initialized {name} on GPIO {pin}")
    
    return pwm_servos

def set_angle(pwm, angle):
    """
    Set servo to specific angle
    
    Args:
        pwm: PWM object
        angle: Angle in degrees (0-180)
    """
    # Convert angle to duty cycle
    # For most servos:
    # 0 degrees = 2% duty cycle (1ms pulse)
    # 90 degrees = 7% duty cycle (1.5ms pulse)
    # 180 degrees = 12% duty cycle (2ms pulse)
    duty_cycle = 2 + (angle / 18)
    pwm.ChangeDutyCycle(duty_cycle)
    time.sleep(0.3)  # Give servo time to reach position
    pwm.ChangeDutyCycle(0)  # Stop sending signal to prevent jitter

def demo_sweep(pwm_servos):
    """
    Demonstrate servo movement by sweeping all servos from 0 to 180 degrees
    
    Args:
        pwm_servos: Dictionary of PWM objects
    """
    print("\n=== Demo: Sweeping all servos together ===")
    print("Sweeping from 0 to 180 degrees...")
    for angle in range(0, 181, 10):
        print(f"Moving all servos to {angle} degrees")
        for name, pwm in pwm_servos.items():
            set_angle(pwm, angle)
        time.sleep(0.5)
    
    print("\nSweeping back from 180 to 0 degrees...")
    for angle in range(180, -1, -10):
        print(f"Moving all servos to {angle} degrees")
        for name, pwm in pwm_servos.items():
            set_angle(pwm, angle)
        time.sleep(0.5)

def demo_individual(pwm_servos):
    """
    Demonstrate individual servo control
    
    Args:
        pwm_servos: Dictionary of PWM objects
    """
    print("\n=== Demo: Individual servo control ===")
    
    for name, pwm in pwm_servos.items():
        print(f"\nMoving {name} independently...")
        for angle in [0, 90, 180, 90]:
            print(f"  {name} -> {angle} degrees")
            set_angle(pwm, angle)
            time.sleep(0.8)

def demo_pattern(pwm_servos):
    """
    Demonstrate a wave pattern across servos
    
    Args:
        pwm_servos: Dictionary of PWM objects
    """
    print("\n=== Demo: Wave pattern ===")
    
    servo_list = list(pwm_servos.items())
    
    for i in range(3):
        print(f"\nWave cycle {i+1}...")
        # Wave forward
        for name, pwm in servo_list:
            set_angle(pwm, 180)
            time.sleep(0.3)
        
        time.sleep(0.3)
        
        # Wave backward
        for name, pwm in reversed(servo_list):
            set_angle(pwm, 0)
            time.sleep(0.3)
        
        time.sleep(0.3)

def interactive_mode(pwm_servos):
    """
    Interactive mode to control servos manually
    
    Args:
        pwm_servos: Dictionary of PWM objects
    """
    print("\n=== Interactive Servo Control ===")
    print("Commands:")
    print("  all <angle>        - Move all servos to angle (0-180)")
    print("  neck <angle>       - Move neck/head to angle")
    print("  left_hand <angle>  - Move left hand to angle")
    print("  right_hand <angle> - Move right hand to angle")
    print("  center             - Center all servos (90 degrees)")
    print("  wave               - Wave both hands")
    print("  nod                - Nod head (yes)")
    print("  shake              - Shake head (no)")
    print("  q                  - Quit")
    
    while True:
        try:
            user_input = input("\nCommand: ").strip().lower()
            
            if user_input == 'q':
                break
            
            if user_input == 'center':
                print("Centering all servos...")
                for name, pwm in pwm_servos.items():
                    set_angle(pwm, 90)
                continue
            
            if user_input == 'wave':
                print("Waving hands...")
                for i in range(3):
                    set_angle(pwm_servos['left_hand'], 45)
                    set_angle(pwm_servos['right_hand'], 135)
                    time.sleep(0.3)
                    set_angle(pwm_servos['left_hand'], 135)
                    set_angle(pwm_servos['right_hand'], 45)
                    time.sleep(0.3)
                # Return to center
                set_angle(pwm_servos['left_hand'], 90)
                set_angle(pwm_servos['right_hand'], 90)
                continue
            
            if user_input == 'nod':
                print("Nodding head (yes)...")
                original_pos = 90
                for i in range(3):
                    set_angle(pwm_servos['neck'], 60)
                    time.sleep(0.3)
                    set_angle(pwm_servos['neck'], 120)
                    time.sleep(0.3)
                set_angle(pwm_servos['neck'], original_pos)
                continue
            
            if user_input == 'shake':
                print("Shaking head (no)...")
                original_pos = 90
                for i in range(3):
                    set_angle(pwm_servos['neck'], 60)
                    time.sleep(0.3)
                    set_angle(pwm_servos['neck'], 120)
                    time.sleep(0.3)
                set_angle(pwm_servos['neck'], original_pos)
                continue
            
            parts = user_input.split()
            if len(parts) != 2:
                print("Invalid command. Use format: <servo_name> <angle> or 'all <angle>'")
                continue
            
            servo_name, angle_str = parts
            angle = int(angle_str)
            
            if not (0 <= angle <= 180):
                print("Angle must be between 0 and 180")
                continue
            
            if servo_name == 'all':
                print(f"Moving all servos to {angle} degrees")
                for name, pwm in pwm_servos.items():
                    set_angle(pwm, angle)
            elif servo_name in pwm_servos:
                print(f"Moving {servo_name} to {angle} degrees")
                set_angle(pwm_servos[servo_name], angle)
            else:
                print(f"Unknown servo: {servo_name}")
                print(f"Available servos: {', '.join(pwm_servos.keys())}, all")
                
        except ValueError:
            print("Invalid input. Please enter a valid command")
        except KeyboardInterrupt:
            print("\nExiting...")
            break

def cleanup(pwm_servos):
    """
    Clean up GPIO and PWM
    
    Args:
        pwm_servos: Dictionary of PWM objects
    """
    for name, pwm in pwm_servos.items():
        pwm.stop()
    GPIO.cleanup()
    print("\nGPIO cleanup complete")

def main():
    """Main function"""
    print("=" * 50)
    print("JARVIS Servo Motor Control System")
    print("=" * 50)
    print(f"\nServo Configuration (BCM mode):")
    for name, pin in SERVO_PINS.items():
        print(f"  {name.replace('_', ' ').title()}: GPIO {pin}")
    
    print("\nWiring for each servo:")
    print("  Servo Red/VCC    -> External 5V power supply (+)")
    print("  Servo Brown/GND  -> Raspberry Pi GND + Power supply (-)")
    print("  Servo Orange/Signal -> Respective GPIO pin")
    print("\nNOTE: Connect servo power to external 5V supply,")
    print("      NOT directly to Raspberry Pi 5V pin!")
    print("=" * 50)
    
    try:
        # Setup servos
        pwm_servos = setup_servos(SERVO_PINS)
        
        # Center all servos first
        print("\nCentering all servos (90 degrees)...")
        for name, pwm in pwm_servos.items():
            set_angle(pwm, 90)
        time.sleep(1)
        
        # Choose mode
        print("\nSelect mode:")
        print("1. Demo - Sweep all servos together")
        print("2. Demo - Individual servo control")
        print("3. Demo - Wave pattern")
        print("4. Interactive control (manual + gestures)")
        
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == '1':
            demo_sweep(pwm_servos)
        elif choice == '2':
            demo_individual(pwm_servos)
        elif choice == '3':
            demo_pattern(pwm_servos)
        elif choice == '4':
            interactive_mode(pwm_servos)
        else:
            print("Invalid choice. Running sweep demo...")
            demo_sweep(pwm_servos)
        
        # Return to center before exit
        print("\nReturning all servos to center position...")
        for name, pwm in pwm_servos.items():
            set_angle(pwm, 90)
        time.sleep(1)
        
    except Exception as e:
        print(f"\nError: {e}")
    
    finally:
        cleanup(pwm_servos)

if __name__ == "__main__":
    main()
