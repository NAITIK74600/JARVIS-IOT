#!/usr/bin/env python3
"""
JARVIS Neck Servo - Smooth Movement Test
Tests various smooth movement patterns for the neck servo
"""

import RPi.GPIO as GPIO
import time

# Configuration
NECK_PIN = 18  # GPIO pin for neck servo
SERVO_FREQUENCY = 50  # 50Hz for standard servos

def setup_servo(pin):
    """Initialize GPIO and setup PWM for servo"""
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin, GPIO.OUT)
    pwm = GPIO.PWM(pin, SERVO_FREQUENCY)
    pwm.start(0)
    return pwm

def set_angle(pwm, angle):
    """
    Set servo to specific angle
    
    Args:
        pwm: PWM object
        angle: Angle in degrees (0-180)
    """
    duty_cycle = 2 + (angle / 18)
    pwm.ChangeDutyCycle(duty_cycle)

def smooth_move(pwm, start_angle, end_angle, duration=1.0, steps=50):
    """
    Move servo smoothly from start to end angle
    
    Args:
        pwm: PWM object
        start_angle: Starting angle
        end_angle: Ending angle
        duration: Time to complete movement (seconds)
        steps: Number of intermediate steps (more = smoother)
    """
    angle_diff = end_angle - start_angle
    delay = duration / steps
    
    for i in range(steps + 1):
        angle = start_angle + (angle_diff * i / steps)
        set_angle(pwm, angle)
        time.sleep(delay)
    
    # Hold final position briefly
    time.sleep(0.1)
    pwm.ChangeDutyCycle(0)  # Stop signal to reduce jitter

def test_basic_movement(pwm):
    """Test basic left-right movement"""
    print("\n=== Test 1: Basic Movement ===")
    print("Moving neck left to right...")
    
    positions = [90, 45, 135, 90]  # Center, left, right, center
    
    for pos in positions:
        print(f"Moving to {pos}°...")
        set_angle(pwm, pos)
        time.sleep(1)
        pwm.ChangeDutyCycle(0)
        time.sleep(0.5)

def test_smooth_sweep(pwm):
    """Test smooth sweeping motion"""
    print("\n=== Test 2: Smooth Sweep ===")
    print("Smoothly sweeping from left to right...")
    
    # Slow smooth sweep
    print("Speed: SLOW")
    smooth_move(pwm, 45, 135, duration=2.0, steps=100)
    time.sleep(0.5)
    
    print("Returning...")
    smooth_move(pwm, 135, 45, duration=2.0, steps=100)
    time.sleep(0.5)
    
    # Medium speed
    print("Speed: MEDIUM")
    smooth_move(pwm, 45, 135, duration=1.0, steps=50)
    time.sleep(0.5)
    
    print("Returning...")
    smooth_move(pwm, 135, 45, duration=1.0, steps=50)
    time.sleep(0.5)
    
    # Fast speed
    print("Speed: FAST")
    smooth_move(pwm, 45, 135, duration=0.5, steps=30)
    time.sleep(0.5)
    
    print("Returning to center...")
    smooth_move(pwm, 135, 90, duration=1.0, steps=50)

def test_scanning_motion(pwm):
    """Test scanning motion (like looking around)"""
    print("\n=== Test 3: Scanning Motion ===")
    print("Simulating head scanning motion...")
    
    scan_positions = [90, 60, 90, 120, 90, 45, 90, 135, 90]
    
    for i, pos in enumerate(scan_positions):
        print(f"Scan position {i+1}: {pos}°")
        current_angle = 90 if i == 0 else scan_positions[i-1]
        smooth_move(pwm, current_angle, pos, duration=0.8, steps=40)
        time.sleep(0.3)

def test_nod_yes(pwm):
    """Test nodding motion (yes gesture)"""
    print("\n=== Test 4: Nod Yes (Vertical) ===")
    print("Simulating 'yes' nod...")
    
    # Note: For actual nodding, you'd need a servo on a different axis
    # This simulates the motion pattern
    for i in range(3):
        print(f"Nod {i+1}")
        smooth_move(pwm, 90, 60, duration=0.4, steps=20)
        time.sleep(0.1)
        smooth_move(pwm, 60, 100, duration=0.4, steps=20)
        time.sleep(0.1)
    
    smooth_move(pwm, 100, 90, duration=0.5, steps=25)

def test_shake_no(pwm):
    """Test shaking motion (no gesture)"""
    print("\n=== Test 5: Shake No (Horizontal) ===")
    print("Simulating 'no' shake...")
    
    for i in range(3):
        print(f"Shake {i+1}")
        smooth_move(pwm, 90, 60, duration=0.3, steps=15)
        time.sleep(0.05)
        smooth_move(pwm, 60, 120, duration=0.3, steps=15)
        time.sleep(0.05)
    
    smooth_move(pwm, 120, 90, duration=0.4, steps=20)

def test_attention_mode(pwm):
    """Test attention-getting motion"""
    print("\n=== Test 6: Attention Mode ===")
    print("Quick alert movements...")
    
    for i in range(2):
        smooth_move(pwm, 90, 70, duration=0.2, steps=10)
        smooth_move(pwm, 70, 110, duration=0.2, steps=10)
        smooth_move(pwm, 110, 90, duration=0.2, steps=10)
        time.sleep(0.2)

def test_tracking_simulation(pwm):
    """Test smooth tracking motion (like following a person)"""
    print("\n=== Test 7: Tracking Simulation ===")
    print("Simulating smooth object tracking...")
    
    # Simulate tracking someone walking left to right
    print("Tracking: Person walking left to right")
    smooth_move(pwm, 90, 45, duration=3.0, steps=150)
    time.sleep(0.5)
    
    print("Tracking: Person walking right to left")
    smooth_move(pwm, 45, 135, duration=3.0, steps=150)
    time.sleep(0.5)
    
    print("Returning to center")
    smooth_move(pwm, 135, 90, duration=1.5, steps=75)

def test_micro_adjustments(pwm):
    """Test small precise movements"""
    print("\n=== Test 8: Micro Adjustments ===")
    print("Testing small, precise movements...")
    
    base_angle = 90
    
    for i in range(5):
        offset = 5 * (1 if i % 2 == 0 else -1)
        target = base_angle + offset
        print(f"Micro adjustment: {base_angle}° -> {target}°")
        smooth_move(pwm, base_angle, target, duration=0.5, steps=25)
        time.sleep(0.3)
        base_angle = target
    
    print("Returning to center")
    smooth_move(pwm, base_angle, 90, duration=0.5, steps=25)

def interactive_smooth_control(pwm):
    """Interactive mode for testing custom movements"""
    print("\n=== Interactive Smooth Control ===")
    print("Commands:")
    print("  <angle>          - Move smoothly to angle (0-180)")
    print("  s <start> <end>  - Smooth move from start to end")
    print("  fast <angle>     - Quick move to angle")
    print("  slow <angle>     - Very slow move to angle")
    print("  center           - Return to center (90°)")
    print("  q                - Quit")
    
    current_angle = 90
    
    while True:
        try:
            user_input = input(f"\nCurrent: {current_angle}° | Command: ").strip().lower()
            
            if user_input == 'q':
                break
            
            if user_input == 'center':
                print("Returning to center...")
                smooth_move(pwm, current_angle, 90, duration=1.0, steps=50)
                current_angle = 90
                continue
            
            parts = user_input.split()
            
            if len(parts) == 1:
                # Simple angle command
                angle = int(parts[0])
                if 0 <= angle <= 180:
                    print(f"Moving {current_angle}° -> {angle}°")
                    smooth_move(pwm, current_angle, angle, duration=1.0, steps=50)
                    current_angle = angle
                else:
                    print("Angle must be between 0 and 180")
            
            elif len(parts) == 2:
                command, angle_str = parts
                angle = int(angle_str)
                
                if not (0 <= angle <= 180):
                    print("Angle must be between 0 and 180")
                    continue
                
                if command == 'fast':
                    print(f"Quick move to {angle}°")
                    smooth_move(pwm, current_angle, angle, duration=0.3, steps=15)
                    current_angle = angle
                elif command == 'slow':
                    print(f"Slow move to {angle}°")
                    smooth_move(pwm, current_angle, angle, duration=3.0, steps=150)
                    current_angle = angle
                else:
                    print("Unknown command")
            
            elif len(parts) == 3 and parts[0] == 's':
                start = int(parts[1])
                end = int(parts[2])
                
                if 0 <= start <= 180 and 0 <= end <= 180:
                    print(f"Smooth move: {start}° -> {end}°")
                    smooth_move(pwm, start, end, duration=2.0, steps=100)
                    current_angle = end
                else:
                    print("Angles must be between 0 and 180")
            else:
                print("Invalid command")
                
        except ValueError:
            print("Invalid input")
        except KeyboardInterrupt:
            print("\nExiting...")
            break

def cleanup(pwm):
    """Clean up GPIO"""
    pwm.ChangeDutyCycle(0)
    pwm.stop()
    GPIO.cleanup()
    print("\nGPIO cleanup complete")

def main():
    """Main function"""
    print("=" * 60)
    print("JARVIS Neck Servo - Smooth Movement Test")
    print("=" * 60)
    print(f"\nNeck Servo Pin: GPIO {NECK_PIN} (BCM mode)")
    print("\nWiring:")
    print("  Servo Red/VCC    -> External 5V power supply (+)")
    print("  Servo Brown/GND  -> Raspberry Pi GND + Power supply (-)")
    print(f"  Servo Orange     -> GPIO {NECK_PIN}")
    print("=" * 60)
    
    try:
        # Setup servo
        pwm = setup_servo(NECK_PIN)
        
        # Center the servo
        print("\nInitializing - centering servo...")
        smooth_move(pwm, 90, 90, duration=0.5, steps=1)
        time.sleep(1)
        
        # Menu
        print("\n=== Test Menu ===")
        print("1. Basic Movement")
        print("2. Smooth Sweep (different speeds)")
        print("3. Scanning Motion")
        print("4. Nod Yes")
        print("5. Shake No")
        print("6. Attention Mode")
        print("7. Tracking Simulation")
        print("8. Micro Adjustments")
        print("9. Interactive Control")
        print("0. Run All Tests")
        
        choice = input("\nSelect test (0-9): ").strip()
        
        if choice == '1':
            test_basic_movement(pwm)
        elif choice == '2':
            test_smooth_sweep(pwm)
        elif choice == '3':
            test_scanning_motion(pwm)
        elif choice == '4':
            test_nod_yes(pwm)
        elif choice == '5':
            test_shake_no(pwm)
        elif choice == '6':
            test_attention_mode(pwm)
        elif choice == '7':
            test_tracking_simulation(pwm)
        elif choice == '8':
            test_micro_adjustments(pwm)
        elif choice == '9':
            interactive_smooth_control(pwm)
        elif choice == '0':
            print("\nRunning all tests...\n")
            test_basic_movement(pwm)
            time.sleep(1)
            test_smooth_sweep(pwm)
            time.sleep(1)
            test_scanning_motion(pwm)
            time.sleep(1)
            test_nod_yes(pwm)
            time.sleep(1)
            test_shake_no(pwm)
            time.sleep(1)
            test_attention_mode(pwm)
            time.sleep(1)
            test_tracking_simulation(pwm)
            time.sleep(1)
            test_micro_adjustments(pwm)
        else:
            print("Invalid choice")
        
        # Return to center
        print("\n\nReturning to center position...")
        smooth_move(pwm, 90, 90, duration=1.0, steps=50)
        time.sleep(0.5)
        
        print("\n✓ Test complete!")
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        cleanup(pwm)

if __name__ == "__main__":
    main()
