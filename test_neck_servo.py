#!/usr/bin/env python3
"""Quick test script to check neck servo"""

import sys
import time

# Add parent directory to path
sys.path.insert(0, '/home/naitik/JARVIS-IOT')

from actuators.multi_servo_controller import multi_servo_controller

print("=" * 60)
print("NECK SERVO TEST")
print("=" * 60)

# Check if controller is initialized
if multi_servo_controller is None:
    print("❌ ERROR: multi_servo_controller is None")
    print("   Servo controller failed to initialize")
    sys.exit(1)

# Check if neck servo exists
neck = multi_servo_controller.get_servo('neck')
if neck is None:
    print("❌ ERROR: Neck servo not found")
    print("   Available servos:", multi_servo_controller.list_servos())
    sys.exit(1)

print(f"✅ Neck servo found: {neck}")
print(f"   Current angle: {neck.get_current_angle()}°")
print(f"   Range: {neck.min_angle}° - {neck.max_angle}°")
print()

# Test movements
print("Testing neck servo movements...")
print()

test_positions = [
    (90, "Center"),
    (45, "Left"),
    (135, "Right"),
    (90, "Center (return)")
]

for angle, label in test_positions:
    print(f"→ Moving to {angle}° ({label})...")
    try:
        multi_servo_controller.set_angle('neck', angle)
        time.sleep(1)
        current = neck.get_current_angle()
        print(f"  ✅ Moved to {current}°")
    except Exception as e:
        print(f"  ❌ Error: {e}")

print()
print("=" * 60)
print("✅ NECK SERVO TEST COMPLETE")
print("=" * 60)
