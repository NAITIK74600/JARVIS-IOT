#!/usr/bin/env python3
"""Test script to verify servo cleanup works without segmentation fault."""

import sys
import time

print("Testing servo initialization and cleanup...")

try:
    from actuators.multi_servo_controller import multi_servo_controller
    
    print("Servos initialized successfully:")
    for name in ['neck', 'arm_l', 'arm_r']:
        servo = multi_servo_controller.get_servo(name)
        if servo:
            print(f"  - {name}: OK")
    
    print("\nTesting servo movements...")
    multi_servo_controller.center('neck')
    print("  - Neck centered")
    time.sleep(0.5)
    
    multi_servo_controller.set_angle('neck', 45)
    print("  - Neck set to 45°")
    time.sleep(0.5)
    
    multi_servo_controller.set_angle('neck', 135)
    print("  - Neck set to 135°")
    time.sleep(0.5)
    
    multi_servo_controller.center('neck')
    print("  - Neck centered again")
    time.sleep(0.5)
    
    print("\nCleaning up servos...")
    multi_servo_controller.cleanup()
    print("✓ Cleanup completed successfully!")
    
    print("\nTest PASSED - No segmentation fault!")
    sys.exit(0)
    
except Exception as e:
    print(f"\n✗ Error during test: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
