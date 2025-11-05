#!/usr/bin/env python3
"""
Test Neck Servo Angle Mapping
Verifies that 0° logical = 90° physical (front-facing)
"""

import time
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from actuators.multi_servo_controller import multi_servo_controller

def test_angle_mapping():
    """Test the new angle mapping for neck servo"""
    print("="*60)
    print("Neck Servo Angle Mapping Test")
    print("="*60)
    
    neck_servo = multi_servo_controller.get_servo('neck')
    
    if not neck_servo:
        print("✗ ERROR: Neck servo not found!")
        return
    
    if not neck_servo.pi:
        print("✗ ERROR: pigpio not connected!")
        print("  Run: sudo systemctl start pigpiod")
        return
    
    neck_lock = multi_servo_controller.get_lock('neck')
    
    if not neck_lock.acquire(blocking=False):
        print("✗ ERROR: Neck servo is busy")
        return
    
    try:
        print(f"\n✓ Neck Servo on GPIO {neck_servo.pin}")
        print(f"  Angle offset: {neck_servo.angle_offset}°")
        print("\nAngle Mapping:")
        print("  Logical → Physical → Position")
        print("  0°      → 90°      → FRONT (forward facing)")
        print("  45°     → 135°     → LEFT")
        print("  -45°    → 45°      → RIGHT")
        print("  90°     → 180°     → FAR LEFT")
        print("  -90°    → 0°       → FAR RIGHT")
        
        print("\n" + "="*60)
        print("Testing Angles...")
        print("="*60)
        
        test_positions = [
            (0, "FRONT (Forward Facing)", 2.0),
            (45, "LEFT", 1.5),
            (0, "FRONT", 1.5),
            (-45, "RIGHT", 1.5),
            (0, "FRONT", 1.5),
            (90, "FAR LEFT", 1.5),
            (0, "FRONT", 1.5),
            (-90, "FAR RIGHT", 1.5),
            (0, "FRONT (Final)", 2.0),
        ]
        
        for logical_angle, description, wait_time in test_positions:
            physical_angle = logical_angle + neck_servo.angle_offset
            print(f"\n→ {description}")
            print(f"  Setting logical {logical_angle}° (physical {physical_angle}°)")
            neck_servo.set_angle(logical_angle)
            time.sleep(wait_time)
        
        print("\n" + "="*60)
        print("✓ Test Complete!")
        print("="*60)
        print("\nNew angle system:")
        print("  • 0° = Front facing (what was 90°)")
        print("  • Positive angles = Turn left")
        print("  • Negative angles = Turn right")
        print("  • Range: -90° to +90°")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        neck_lock.release()
        print("\n→ Servo lock released")

if __name__ == "__main__":
    test_angle_mapping()
