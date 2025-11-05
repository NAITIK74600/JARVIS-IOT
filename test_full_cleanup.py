#!/usr/bin/env python3
"""Test full hardware cleanup sequence like main.py does."""

import sys
import time

print("Testing full hardware cleanup sequence...\n")

# Initialize all hardware components
try:
    # Servo Controller
    print("1. Initializing servos...")
    from actuators.multi_servo_controller import multi_servo_controller
    print("   ✓ Servos initialized\n")
    
    # Sensor Manager
    print("2. Initializing sensors...")
    try:
        from sensors.sensor_manager import SensorManager
        sensor_manager = SensorManager()
        sensor_manager.start()
        print("   ✓ Sensors initialized\n")
    except Exception as e:
        print(f"   ⚠ Sensors skipped: {e}\n")
        sensor_manager = None
    
    # Hardware Manager
    print("3. Initializing hardware manager...")
    from core.hardware_manager import hardware_manager
    print("   ✓ Hardware manager initialized\n")
    
    # Display
    print("4. Initializing display...")
    try:
        from actuators.display import display
        print("   ✓ Display initialized\n")
    except Exception as e:
        print(f"   ⚠ Display skipped: {e}\n")
        display = None
    
    print("=" * 50)
    print("All hardware initialized successfully!")
    print("=" * 50)
    print("\nWaiting 2 seconds before cleanup...\n")
    time.sleep(2)
    
    # Now cleanup in the same order as main.py
    print("=" * 50)
    print("Starting cleanup sequence...")
    print("=" * 50)
    
    print("\n1. Stopping sensors...")
    if sensor_manager:
        sensor_manager.stop()
        print("   ✓ Sensors stopped")
    
    print("\n2. Cleaning up servos...")
    multi_servo_controller.cleanup()
    print("   ✓ Servos cleaned up")
    
    print("\n3. Cleaning up display...")
    if display:
        display.cleanup()
        print("   ✓ Display cleaned up")
    
    print("\n4. Cleaning up hardware manager...")
    hardware_manager.cleanup()
    print("   ✓ Hardware manager cleaned up")
    
    print("\n" + "=" * 50)
    print("✓ ALL CLEANUP COMPLETED SUCCESSFULLY!")
    print("✓ NO SEGMENTATION FAULT!")
    print("=" * 50)
    
    sys.exit(0)
    
except Exception as e:
    print(f"\n✗ Error during test: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
