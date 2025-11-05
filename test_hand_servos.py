#!/usr/bin/env python3
"""
Test Hand Servos - Left and Right
Checks smooth movement for both hand servos
"""

import time
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from actuators.multi_servo_controller import multi_servo_controller

def smooth_move(servo, start, end, duration=1.0, steps=50):
    """Move servo smoothly"""
    angle_diff = end - start
    delay = duration / steps
    
    for i in range(steps + 1):
        angle = start + (angle_diff * i / steps)
        servo.set_angle(int(angle))
        time.sleep(delay)

def test_hand_servo(name, display_name):
    """Test a single hand servo"""
    print("\n" + "="*60)
    print(f"Testing {display_name}")
    print("="*60)
    
    servo = multi_servo_controller.get_servo(name)
    lock = multi_servo_controller.get_lock(name)
    
    if not servo:
        print(f"✗ ERROR: Servo '{name}' not found!")
        return False
    
    if not servo.pi:
        print(f"✗ ERROR: pigpio not connected!")
        print("  Run: sudo systemctl start pigpiod")
        return False
    
    if not lock.acquire(blocking=False):
        print(f"✗ ERROR: Servo '{name}' is busy")
        return False
    
    try:
        print(f"✓ Servo on GPIO {servo.pin}")
        print(f"  Pulse range: {servo.min_pulse}µs - {servo.max_pulse}µs")
        print(f"  Angle offset: {servo.angle_offset}°")
        
        # Test 1: Center position
        print("\n→ Test 1: Centering (90°)")
        servo.set_angle(90)
        time.sleep(1.5)
        
        # Test 2: Full range sweep
        print("\n→ Test 2: Full Range Sweep")
        print("  0° → 180° (smooth)")
        smooth_move(servo, 0, 180, duration=2.0, steps=100)
        time.sleep(0.5)
        
        print("  180° → 0° (smooth)")
        smooth_move(servo, 180, 0, duration=2.0, steps=100)
        time.sleep(0.5)
        
        # Test 3: Mid-range positions
        print("\n→ Test 3: Mid-Range Positions")
        positions = [90, 45, 90, 135, 90]
        for i, pos in enumerate(positions):
            desc = {0: "Center", 45: "Down/Closed", 135: "Up/Open", 90: "Center"}
            print(f"  Position {i+1}: {pos}° ({desc.get(pos, 'Position')})")
            smooth_move(servo, servo.current_angle or 90, pos, duration=1.0, steps=50)
            time.sleep(0.8)
        
        # Test 4: Quick movements
        print("\n→ Test 4: Quick Movements")
        for i in range(3):
            print(f"  Quick test {i+1}/3")
            smooth_move(servo, 90, 60, duration=0.3, steps=15)
            smooth_move(servo, 60, 120, duration=0.3, steps=15)
            smooth_move(servo, 120, 90, duration=0.3, steps=15)
            time.sleep(0.2)
        
        # Test 5: Micro adjustments
        print("\n→ Test 5: Micro Adjustments")
        base = 90
        for offset in [10, -10, 15, -15, 5, -5]:
            target = base + offset
            print(f"  {base}° → {target}° (offset: {offset:+d}°)")
            smooth_move(servo, base, target, duration=0.5, steps=25)
            time.sleep(0.3)
            base = target
        
        # Return to center
        print("\n→ Returning to center (90°)")
        smooth_move(servo, servo.current_angle or 90, 90, duration=1.0, steps=50)
        time.sleep(0.5)
        
        print(f"\n✓ {display_name} - ALL TESTS PASSED!")
        return True
        
    except Exception as e:
        print(f"\n✗ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        lock.release()

def test_both_hands_together():
    """Test both hands moving together"""
    print("\n" + "="*60)
    print("Testing Both Hands Together")
    print("="*60)
    
    left_servo = multi_servo_controller.get_servo('arm_l')
    right_servo = multi_servo_controller.get_servo('arm_r')
    left_lock = multi_servo_controller.get_lock('arm_l')
    right_lock = multi_servo_controller.get_lock('arm_r')
    
    if not (left_servo and right_servo):
        print("✗ ERROR: One or both hand servos not found!")
        return False
    
    if not (left_lock.acquire(blocking=False) and right_lock.acquire(blocking=False)):
        print("✗ ERROR: One or both servos are busy")
        left_lock.release()
        right_lock.release()
        return False
    
    try:
        print("\n→ Test 1: Synchronized Movement (both hands same angle)")
        for angle in [90, 0, 180, 90]:
            print(f"  Both hands → {angle}°")
            left_servo.set_angle(angle)
            right_servo.set_angle(angle)
            time.sleep(1.5)
        
        print("\n→ Test 2: Mirror Movement (opposite angles)")
        mirror_pairs = [(45, 135), (135, 45), (90, 90), (60, 120), (120, 60), (90, 90)]
        for left_angle, right_angle in mirror_pairs:
            print(f"  Left: {left_angle}° | Right: {right_angle}°")
            left_servo.set_angle(left_angle)
            right_servo.set_angle(right_angle)
            time.sleep(1.2)
        
        print("\n→ Test 3: Wave Gesture")
        for i in range(3):
            print(f"  Wave {i+1}/3")
            # Both hands up
            left_servo.set_angle(135)
            right_servo.set_angle(135)
            time.sleep(0.4)
            # Both hands down
            left_servo.set_angle(45)
            right_servo.set_angle(45)
            time.sleep(0.4)
        
        # Center both
        print("\n→ Centering both hands")
        left_servo.set_angle(90)
        right_servo.set_angle(90)
        time.sleep(1)
        
        print("\n✓ Both Hands Test - PASSED!")
        return True
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        left_lock.release()
        right_lock.release()

def interactive_hand_control():
    """Interactive mode to test hand positions"""
    print("\n" + "="*60)
    print("Interactive Hand Control")
    print("="*60)
    print("Commands:")
    print("  left <angle>     - Move left hand to angle")
    print("  right <angle>    - Move right hand to angle")
    print("  both <angle>     - Move both hands to angle")
    print("  mirror <l> <r>   - Left to <l>°, Right to <r>°")
    print("  center           - Center both hands (90°)")
    print("  wave             - Wave gesture")
    print("  q                - Quit")
    print("="*60)
    
    left_servo = multi_servo_controller.get_servo('arm_l')
    right_servo = multi_servo_controller.get_servo('arm_r')
    left_lock = multi_servo_controller.get_lock('arm_l')
    right_lock = multi_servo_controller.get_lock('arm_r')
    
    if not (left_servo and right_servo):
        print("✗ ERROR: Hand servos not available")
        return
    
    if not (left_lock.acquire(blocking=False) and right_lock.acquire(blocking=False)):
        print("✗ ERROR: Servos are busy")
        return
    
    try:
        while True:
            user_input = input("\nCommand: ").strip().lower()
            
            if user_input == 'q':
                break
            
            if user_input == 'center':
                print("→ Centering both hands...")
                smooth_move(left_servo, left_servo.current_angle or 90, 90, 0.8, 40)
                smooth_move(right_servo, right_servo.current_angle or 90, 90, 0.8, 40)
                continue
            
            if user_input == 'wave':
                print("→ Waving...")
                for i in range(3):
                    left_servo.set_angle(135)
                    right_servo.set_angle(135)
                    time.sleep(0.3)
                    left_servo.set_angle(45)
                    right_servo.set_angle(45)
                    time.sleep(0.3)
                left_servo.set_angle(90)
                right_servo.set_angle(90)
                continue
            
            parts = user_input.split()
            
            if len(parts) == 2 and parts[0] in ['left', 'right', 'both']:
                try:
                    angle = int(parts[1])
                    if not (0 <= angle <= 180):
                        print("✗ Angle must be 0-180")
                        continue
                    
                    if parts[0] == 'left':
                        print(f"→ Left hand → {angle}°")
                        smooth_move(left_servo, left_servo.current_angle or 90, angle, 1.0, 50)
                    elif parts[0] == 'right':
                        print(f"→ Right hand → {angle}°")
                        smooth_move(right_servo, right_servo.current_angle or 90, angle, 1.0, 50)
                    elif parts[0] == 'both':
                        print(f"→ Both hands → {angle}°")
                        left_servo.set_angle(angle)
                        right_servo.set_angle(angle)
                except ValueError:
                    print("✗ Invalid angle")
            
            elif len(parts) == 3 and parts[0] == 'mirror':
                try:
                    left_angle = int(parts[1])
                    right_angle = int(parts[2])
                    if (0 <= left_angle <= 180) and (0 <= right_angle <= 180):
                        print(f"→ Left: {left_angle}° | Right: {right_angle}°")
                        left_servo.set_angle(left_angle)
                        right_servo.set_angle(right_angle)
                    else:
                        print("✗ Angles must be 0-180")
                except ValueError:
                    print("✗ Invalid angles")
            else:
                print("✗ Invalid command")
    
    except KeyboardInterrupt:
        print("\n→ Exiting...")
    
    finally:
        left_lock.release()
        right_lock.release()

def main():
    """Main function"""
    print("="*60)
    print("JARVIS Hand Servos Test")
    print("="*60)
    
    print("\nTest Menu:")
    print("1. Test Left Hand Only")
    print("2. Test Right Hand Only")
    print("3. Test Both Hands (individual)")
    print("4. Test Both Hands Together (synchronized)")
    print("5. Interactive Control")
    print("0. Run All Tests")
    
    choice = input("\nSelect test (0-5): ").strip()
    
    results = {}
    
    if choice == '1':
        results['left'] = test_hand_servo('arm_l', 'Left Hand')
    elif choice == '2':
        results['right'] = test_hand_servo('arm_r', 'Right Hand')
    elif choice == '3':
        results['left'] = test_hand_servo('arm_l', 'Left Hand')
        time.sleep(1)
        results['right'] = test_hand_servo('arm_r', 'Right Hand')
    elif choice == '4':
        results['both'] = test_both_hands_together()
    elif choice == '5':
        interactive_hand_control()
        return
    elif choice == '0':
        print("\n→ Running all tests...\n")
        results['left'] = test_hand_servo('arm_l', 'Left Hand')
        time.sleep(1)
        results['right'] = test_hand_servo('arm_r', 'Right Hand')
        time.sleep(1)
        results['both'] = test_both_hands_together()
    else:
        print("✗ Invalid choice")
        return
    
    # Summary
    if results:
        print("\n" + "="*60)
        print("Test Summary")
        print("="*60)
        for test_name, success in results.items():
            status = "✓ PASS" if success else "✗ FAIL"
            print(f"  {test_name.upper():12s} - {status}")
        print("="*60)
    
    print("\n✓ All tests complete!")

if __name__ == "__main__":
    main()
