#!/usr/bin/env python3
"""
Minimal test to verify cleanup order without Tkinter GUI.
This simulates the same cleanup sequence as main.py.
"""

import time
import sys

print("=== MINIMAL CLEANUP ORDER TEST ===\n")

# Import in same order as main.py
print("1. Importing servos...")
from actuators.multi_servo_controller import multi_servo_controller

print("2. Importing sensors...")
try:
    from sensors.sensor_manager import SensorManager
    sensor_manager = SensorManager()
    sensor_manager.start()
    print("   Sensors started")
except Exception as e:
    print(f"   Sensors failed: {e}")
    sensor_manager = None

print("3. Importing motor tools...")
from tools.motor_tools import move_forward, move_backward, turn_left, turn_right, stop_moving

print("4. Importing hardware manager...")
from core.hardware_manager import hardware_manager

print("5. Importing display...")
try:
    from actuators.display import display
    print("   Display loaded")
except Exception as e:
    print(f"   Display failed: {e}")
    display = None

print("\n=== INITIALIZATION COMPLETE ===")
print("Waiting 2 seconds...\n")
time.sleep(2)

print("=== STARTING CLEANUP SEQUENCE ===\n")

# Same cleanup order as main.py
try:
    print("Step 1: Stopping sensors...")
    if sensor_manager:
        sensor_manager.stop()
        print("   ✓ Sensors stopped")
except Exception as e:
    print(f"   ERROR: {e}")

try:
    print("\nStep 2: Cleaning up motor controller...")
    import sys as _sys
    if 'tools.motor_tools' in _sys.modules:
        _motor_tools = _sys.modules.get('tools.motor_tools')
        if _motor_tools and hasattr(_motor_tools, 'motor_controller'):
            _motor_tools.motor_controller.cleanup()
            print("   ✓ Motor controller cleaned up")
except Exception as e:
    print(f"   ERROR: {e}")

try:
    print("\nStep 3: Cleaning up display...")
    if display:
        display.cleanup()
        print("   ✓ Display cleaned up")
except Exception as e:
    print(f"   ERROR: {e}")

try:
    print("\nStep 4: Cleaning up servos...")
    multi_servo_controller.cleanup()
    print("   ✓ Servos cleaned up")
except Exception as e:
    print(f"   ERROR: {e}")

try:
    print("\nStep 5: Cleaning up hardware manager (GPIO)...")
    hardware_manager.cleanup()
    print("   ✓ Hardware manager cleaned up")
except Exception as e:
    print(f"   ERROR: {e}")

print("\n=== CLEANUP COMPLETE ===")
print("Exiting...")
sys.exit(0)
