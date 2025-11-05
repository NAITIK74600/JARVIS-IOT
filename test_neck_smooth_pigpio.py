#!/usr/bin/env python3
"""
JARVIS Neck Servo - Smooth Movement Test using pigpio
Tests various smooth movement patterns using the existing servo infrastructure
"""

import time
import sys
import os

# Add the project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from actuators.multi_servo_controller import multi_servo_controller

def smooth_move(servo, start_angle, end_angle, duration=1.0, steps=50):
    """
    Move servo smoothly from start to end angle
    
    Args:
        servo: Servo object
        start_angle: Starting angle (0-180)
        end_angle: Ending angle (0-180)
        duration: Time to complete movement (seconds)
        steps: Number of intermediate steps (more = smoother)
    """
    if not servo or not servo.pi:
        print("Servo not available")
        return
    
    angle_diff = end_angle - start_angle
    delay = duration / steps
    
    print(f"  Moving from {start_angle}° to {end_angle}° over {duration}s ({steps} steps)")
    
    for i in range(steps + 1):
        angle = start_angle + (angle_diff * i / steps)
        servo.set_angle(int(angle))
        time.sleep(delay)
    
    # Brief hold at final position
    time.sleep(0.1)

def test_basic_movement(servo):
    """Test basic left-right movement"""
    print("\n" + "="*60)
    print("Test 1: Basic Movement")
    print("="*60)
    print("Moving neck left to right with pauses...")
    
    positions = [
        (90, "Center"),
        (45, "Left"),
        (135, "Right"),
        (90, "Center")
    ]
    
    for pos, name in positions:
        print(f"→ {name} ({pos}°)")
        servo.set_angle(pos)
        time.sleep(1)

def test_smooth_sweep(servo):
    """Test smooth sweeping motion at different speeds"""
    print("\n" + "="*60)
    print("Test 2: Smooth Sweep (Different Speeds)")
    print("="*60)
    
    tests = [
        (2.0, 100, "VERY SLOW"),
        (1.5, 75, "SLOW"),
        (1.0, 50, "MEDIUM"),
        (0.5, 30, "FAST"),
    ]
    
    for duration, steps, speed in tests:
        print(f"\nSpeed: {speed}")
        smooth_move(servo, 45, 135, duration=duration, steps=steps)
        time.sleep(0.3)
        smooth_move(servo, 135, 45, duration=duration, steps=steps)
        time.sleep(0.5)
    
    print("\n→ Returning to center")
    smooth_move(servo, 45, 90, duration=1.0, steps=50)

def test_scanning_motion(servo):
    """Test scanning motion (like looking around)"""
    print("\n" + "="*60)
    print("Test 3: Scanning Motion")
    print("="*60)
    print("Simulating natural head scanning...")
    
    scan_sequence = [
        (90, 60),   # Center to left
        (60, 90),   # Back to center
        (90, 120),  # Center to right
        (120, 90),  # Back to center
        (90, 45),   # Center to far left
        (45, 90),   # Back to center
        (90, 135),  # Center to far right
        (135, 90),  # Back to center
    ]
    
    for i, (start, end) in enumerate(scan_sequence, 1):
        print(f"Scan {i}: {start}° → {end}°")
        smooth_move(servo, start, end, duration=0.8, steps=40)
        time.sleep(0.2)

def test_nod_gesture(servo):
    """Test nodding motion (yes gesture)"""
    print("\n" + "="*60)
    print("Test 4: Nod Gesture (Yes)")
    print("="*60)
    print("Simulating 'yes' nodding motion...")
    
    for i in range(3):
        print(f"Nod {i+1}/3")
        smooth_move(servo, 90, 70, duration=0.4, steps=20)
        time.sleep(0.05)
        smooth_move(servo, 70, 100, duration=0.4, steps=20)
        time.sleep(0.05)
    
    smooth_move(servo, 100, 90, duration=0.5, steps=25)

def test_shake_gesture(servo):
    """Test shaking motion (no gesture)"""
    print("\n" + "="*60)
    print("Test 5: Shake Gesture (No)")
    print("="*60)
    print("Simulating 'no' shaking motion...")
    
    for i in range(3):
        print(f"Shake {i+1}/3")
        smooth_move(servo, 90, 60, duration=0.3, steps=15)
        time.sleep(0.05)
        smooth_move(servo, 60, 120, duration=0.3, steps=15)
        time.sleep(0.05)
    
    smooth_move(servo, 120, 90, duration=0.4, steps=20)

def test_attention_mode(servo):
    """Test attention-getting motion"""
    print("\n" + "="*60)
    print("Test 6: Attention Mode")
    print("="*60)
    print("Quick alert movements...")
    
    for i in range(2):
        print(f"Alert sequence {i+1}/2")
        smooth_move(servo, 90, 70, duration=0.2, steps=10)
        smooth_move(servo, 70, 110, duration=0.2, steps=10)
        smooth_move(servo, 110, 90, duration=0.2, steps=10)
        time.sleep(0.2)

def test_tracking_simulation(servo):
    """Test smooth tracking motion"""
    print("\n" + "="*60)
    print("Test 7: Tracking Simulation")
    print("="*60)
    
    print("→ Tracking: Object moving left to right (slow)")
    smooth_move(servo, 90, 45, duration=3.0, steps=150)
    time.sleep(0.5)
    
    print("→ Tracking: Object moving right to left (slow)")
    smooth_move(servo, 45, 135, duration=3.0, steps=150)
    time.sleep(0.5)
    
    print("→ Returning to center")
    smooth_move(servo, 135, 90, duration=1.5, steps=75)

def test_micro_adjustments(servo):
    """Test small precise movements"""
    print("\n" + "="*60)
    print("Test 8: Micro Adjustments")
    print("="*60)
    print("Testing small, precise movements...")
    
    base_angle = 90
    adjustments = [5, -5, 10, -10, 15, -15]
    
    for i, offset in enumerate(adjustments, 1):
        target = base_angle + offset
        print(f"Adjustment {i}: {base_angle}° → {target}° (offset: {offset:+d}°)")
        smooth_move(servo, base_angle, target, duration=0.5, steps=25)
        time.sleep(0.3)
        base_angle = target
    
    print("→ Returning to center")
    smooth_move(servo, base_angle, 90, duration=0.5, steps=25)

def interactive_smooth_control(servo):
    """Interactive mode for testing custom movements"""
    print("\n" + "="*60)
    print("Interactive Smooth Control")
    print("="*60)
    print("Commands:")
    print("  <angle>          - Move smoothly to angle (0-180)")
    print("  s <start> <end>  - Smooth move from start to end")
    print("  fast <angle>     - Quick move to angle")
    print("  slow <angle>     - Very slow move to angle")
    print("  center           - Return to center (90°)")
    print("  q                - Quit")
    print("="*60)
    
    current_angle = 90
    
    while True:
        try:
            user_input = input(f"\nCurrent: {current_angle}° | Command: ").strip().lower()
            
            if user_input == 'q':
                break
            
            if user_input == 'center':
                print("→ Returning to center...")
                smooth_move(servo, current_angle, 90, duration=1.0, steps=50)
                current_angle = 90
                continue
            
            parts = user_input.split()
            
            if len(parts) == 1:
                # Simple angle command
                try:
                    angle = int(parts[0])
                    if 0 <= angle <= 180:
                        print(f"→ Moving {current_angle}° → {angle}°")
                        smooth_move(servo, current_angle, angle, duration=1.0, steps=50)
                        current_angle = angle
                    else:
                        print("✗ Angle must be between 0 and 180")
                except ValueError:
                    print("✗ Invalid angle")
            
            elif len(parts) == 2:
                command, angle_str = parts
                try:
                    angle = int(angle_str)
                    
                    if not (0 <= angle <= 180):
                        print("✗ Angle must be between 0 and 180")
                        continue
                    
                    if command == 'fast':
                        print(f"→ Quick move to {angle}°")
                        smooth_move(servo, current_angle, angle, duration=0.3, steps=15)
                        current_angle = angle
                    elif command == 'slow':
                        print(f"→ Slow move to {angle}°")
                        smooth_move(servo, current_angle, angle, duration=3.0, steps=150)
                        current_angle = angle
                    else:
                        print("✗ Unknown command")
                except ValueError:
                    print("✗ Invalid angle")
            
            elif len(parts) == 3 and parts[0] == 's':
                try:
                    start = int(parts[1])
                    end = int(parts[2])
                    
                    if 0 <= start <= 180 and 0 <= end <= 180:
                        print(f"→ Smooth move: {start}° → {end}°")
                        smooth_move(servo, start, end, duration=2.0, steps=100)
                        current_angle = end
                    else:
                        print("✗ Angles must be between 0 and 180")
                except ValueError:
                    print("✗ Invalid angles")
            else:
                print("✗ Invalid command")
                
        except KeyboardInterrupt:
            print("\n\n→ Exiting interactive mode...")
            break

def main():
    """Main function"""
    print("="*60)
    print("JARVIS Neck Servo - Smooth Movement Test")
    print("="*60)
    
    # Get neck servo from multi_servo_controller
    neck_servo = multi_servo_controller.get_servo('neck')
    
    if not neck_servo:
        print("\n✗ ERROR: Neck servo not found!")
        print("  Check that the servo is properly initialized in multi_servo_controller")
        return
    
    if not neck_servo.pi:
        print("\n✗ ERROR: pigpio not connected!")
        print("  Make sure pigpiod daemon is running:")
        print("    sudo systemctl start pigpiod")
        return
    
    neck_lock = multi_servo_controller.get_lock('neck')
    
    print(f"\n✓ Neck Servo initialized on GPIO pin {neck_servo.pin}")
    print(f"  Pulse range: {neck_servo.min_pulse}µs - {neck_servo.max_pulse}µs")
    print("\nWiring:")
    print("  Servo Red/VCC    → External 5V power supply (+)")
    print("  Servo Brown/GND  → Raspberry Pi GND + Power supply (-)")
    print(f"  Servo Orange     → GPIO {neck_servo.pin}")
    print("="*60)
    
    try:
        # Acquire lock for exclusive access
        if not neck_lock.acquire(blocking=False):
            print("\n✗ ERROR: Neck servo is busy (locked by another process)")
            return
        
        # Initialize - center the servo
        print("\n→ Initializing - centering servo...")
        smooth_move(neck_servo, 90, 90, duration=0.5, steps=1)
        time.sleep(1)
        
        # Menu
        print("\n" + "="*60)
        print("Test Menu")
        print("="*60)
        print("1. Basic Movement")
        print("2. Smooth Sweep (different speeds)")
        print("3. Scanning Motion")
        print("4. Nod Gesture (yes)")
        print("5. Shake Gesture (no)")
        print("6. Attention Mode")
        print("7. Tracking Simulation")
        print("8. Micro Adjustments")
        print("9. Interactive Control")
        print("0. Run All Tests")
        print("="*60)
        
        choice = input("\nSelect test (0-9): ").strip()
        
        if choice == '1':
            test_basic_movement(neck_servo)
        elif choice == '2':
            test_smooth_sweep(neck_servo)
        elif choice == '3':
            test_scanning_motion(neck_servo)
        elif choice == '4':
            test_nod_gesture(neck_servo)
        elif choice == '5':
            test_shake_gesture(neck_servo)
        elif choice == '6':
            test_attention_mode(neck_servo)
        elif choice == '7':
            test_tracking_simulation(neck_servo)
        elif choice == '8':
            test_micro_adjustments(neck_servo)
        elif choice == '9':
            interactive_smooth_control(neck_servo)
        elif choice == '0':
            print("\n→ Running all tests...")
            test_basic_movement(neck_servo)
            time.sleep(1)
            test_smooth_sweep(neck_servo)
            time.sleep(1)
            test_scanning_motion(neck_servo)
            time.sleep(1)
            test_nod_gesture(neck_servo)
            time.sleep(1)
            test_shake_gesture(neck_servo)
            time.sleep(1)
            test_attention_mode(neck_servo)
            time.sleep(1)
            test_tracking_simulation(neck_servo)
            time.sleep(1)
            test_micro_adjustments(neck_servo)
        else:
            print("✗ Invalid choice")
        
        # Return to center
        print("\n\n→ Returning to center position...")
        smooth_move(neck_servo, neck_servo.current_angle or 90, 90, duration=1.0, steps=50)
        time.sleep(0.5)
        
        print("\n✓ Test complete!")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Release lock
        try:
            neck_lock.release()
            print("\n→ Released servo lock")
        except:
            pass
        
        print("→ Cleanup handled by multi_servo_controller")

if __name__ == "__main__":
    main()
