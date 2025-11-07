#!/usr/bin/env python3
"""
L298N Motor Driver Test Script
Tests all motor functions: forward, backward, left, right, stop
"""

import time
import sys

print("=" * 60)
print("L298N MOTOR DRIVER TEST")
print("=" * 60)

try:
    from actuators.motor_controller import MotorController
    print("✓ MotorController imported successfully")
except ImportError as e:
    print(f"✗ Failed to import MotorController: {e}")
    sys.exit(1)

# Initialize motor controller
try:
    motors = MotorController()
    print("✓ MotorController initialized")
    print(f"  Left Motor:  EN=GPIO{motors.L_EN}, IN1=GPIO{motors.L_IN1}, IN2=GPIO{motors.L_IN2}")
    print(f"  Right Motor: EN=GPIO{motors.R_EN}, IN1=GPIO{motors.R_IN1}, IN2=GPIO{motors.R_IN2}")
except Exception as e:
    print(f"✗ Failed to initialize MotorController: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("MOTOR TEST SEQUENCE - 80% Speed")
print("=" * 60)

speed = 80  # 80% speed

try:
    # Test 1: Forward
    print("\n[1/5] Testing FORWARD...")
    motors.forward(speed)
    time.sleep(2)
    motors.stop()
    print("✓ Forward complete")
    time.sleep(1)
    
    # Test 2: Backward
    print("\n[2/5] Testing BACKWARD...")
    motors.backward(speed)
    time.sleep(2)
    motors.stop()
    print("✓ Backward complete")
    time.sleep(1)
    
    # Test 3: Turn Left (left motor backward, right forward)
    print("\n[3/5] Testing TURN LEFT...")
    motors.left(speed)
    time.sleep(1.5)
    motors.stop()
    print("✓ Turn left complete")
    time.sleep(1)
    
    # Test 4: Turn Right (left motor forward, right backward)
    print("\n[4/5] Testing TURN RIGHT...")
    motors.right(speed)
    time.sleep(1.5)
    motors.stop()
    print("✓ Turn right complete")
    time.sleep(1)
    
    # Test 5: Speed ramp test
    print("\n[5/5] Testing SPEED RAMP (0-100%)...")
    for s in range(0, 101, 20):
        print(f"  Speed: {s}%")
        motors.forward(s)
        time.sleep(0.5)
    motors.stop()
    print("✓ Speed ramp complete")
    
    print("\n" + "=" * 60)
    print("✓ ALL TESTS PASSED!")
    print("=" * 60)
    
except KeyboardInterrupt:
    print("\n\n⚠ Test interrupted by user")
    motors.stop()
    
except Exception as e:
    print(f"\n✗ Test failed: {e}")
    import traceback
    traceback.print_exc()
    motors.stop()
    
finally:
    # Cleanup
    print("\nCleaning up...")
    try:
        motors.cleanup()
        print("✓ Motor controller cleaned up")
    except Exception as e:
        print(f"⚠ Cleanup warning: {e}")

print("\n" + "=" * 60)
print("L298N Motor Test Complete")
print("=" * 60)
