#!/usr/bin/env python3
"""
Quick Servo Movement Test
Fast script to test all three servos with smooth movements
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

def test_servo(name):
    """Test a single servo with smooth movements"""
    servo = multi_servo_controller.get_servo(name)
    lock = multi_servo_controller.get_lock(name)
    
    if not servo:
        print(f"✗ Servo '{name}' not found")
        return False
    
    if not servo.pi:
        print(f"✗ Servo '{name}' - pigpio not connected")
        return False
    
    if not lock.acquire(blocking=False):
        print(f"✗ Servo '{name}' is busy")
        return False
    
    try:
        print(f"\n→ Testing {name.upper()} servo (GPIO {servo.pin})")
        
        # Center
        print("  Centering...")
        smooth_move(servo, 90, 90, duration=0.3, steps=1)
        time.sleep(0.5)
        
        # Sweep test
        print("  Smooth sweep...")
        smooth_move(servo, 90, 45, duration=1.0, steps=50)
        time.sleep(0.2)
        smooth_move(servo, 45, 135, duration=1.5, steps=75)
        time.sleep(0.2)
        smooth_move(servo, 135, 90, duration=1.0, steps=50)
        time.sleep(0.5)
        
        print(f"  ✓ {name.upper()} servo working smoothly!")
        return True
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False
    finally:
        lock.release()

def main():
    print("="*60)
    print("JARVIS Multi-Servo Smooth Movement Test")
    print("="*60)
    
    servos_to_test = ['neck', 'arm_l', 'arm_r']
    results = {}
    
    for servo_name in servos_to_test:
        results[servo_name] = test_servo(servo_name)
        time.sleep(0.5)
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    for name, success in results.items():
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"  {name.upper():10s} - {status}")
    
    print("="*60)
    print("\nAll tests complete!")

if __name__ == "__main__":
    main()
