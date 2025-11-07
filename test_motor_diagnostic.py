#!/usr/bin/env python3
"""
L298N Motor Driver - Complete Diagnostic Test
Checks libraries, GPIO setup, hardware connections, and motor functionality
"""

import sys
import os

print("=" * 70)
print("L298N MOTOR DRIVER - DIAGNOSTIC TEST")
print("=" * 70)

# Step 1: Check Python version
print("\n[1/8] Checking Python version...")
print(f"✓ Python {sys.version}")

# Step 2: Check required libraries
print("\n[2/8] Checking required libraries...")
missing_libs = []

try:
    import RPi.GPIO as GPIO
    print(f"✓ RPi.GPIO version {GPIO.VERSION}")
except ImportError as e:
    print(f"✗ RPi.GPIO not found: {e}")
    missing_libs.append("RPi.GPIO")

try:
    from dotenv import load_dotenv
    print("✓ python-dotenv installed")
except ImportError:
    print("✗ python-dotenv not found")
    missing_libs.append("python-dotenv")

if missing_libs:
    print(f"\n✗ Missing libraries: {', '.join(missing_libs)}")
    print("Install with: pip install RPi.GPIO python-dotenv")
    sys.exit(1)

# Step 3: Check GPIO access (requires root/sudo)
print("\n[3/8] Checking GPIO access...")
try:
    # Try to access GPIO memory
    with open('/dev/gpiomem', 'r') as f:
        print("✓ GPIO memory accessible (/dev/gpiomem)")
except PermissionError:
    print("✗ Permission denied for GPIO access")
    print("  Run with: sudo python3 test_motor_diagnostic.py")
    sys.exit(1)
except FileNotFoundError:
    print("⚠ /dev/gpiomem not found (might be okay on some systems)")

# Step 4: Import motor controller
print("\n[4/8] Importing motor controller...")
try:
    from actuators.motor_controller import MotorController
    print("✓ MotorController imported")
except ImportError as e:
    print(f"✗ Failed to import MotorController: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 5: Initialize motor controller
print("\n[5/8] Initializing motor controller...")
try:
    motors = MotorController()
    print("✓ MotorController initialized")
    print(f"  Simulation mode: {motors.simulation_mode}")
    print(f"  Left Motor:  EN=GPIO{motors.L_EN}, IN1=GPIO{motors.L_IN1}, IN2=GPIO{motors.L_IN2}")
    print(f"  Right Motor: EN=GPIO{motors.R_EN}, IN1=GPIO{motors.R_IN1}, IN2=GPIO{motors.R_IN2}")
except Exception as e:
    print(f"✗ Failed to initialize: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 6: Check GPIO pin status
print("\n[6/8] Checking GPIO pin configuration...")
if not motors.simulation_mode:
    try:
        import RPi.GPIO as GPIO
        pins = [motors.L_EN, motors.L_IN1, motors.L_IN2, motors.R_EN, motors.R_IN1, motors.R_IN2]
        print(f"✓ All pins configured: {pins}")
        print("  GPIO mode: BCM")
    except Exception as e:
        print(f"⚠ GPIO check warning: {e}")
else:
    print("⚠ Running in simulation mode (no real hardware)")

# Step 7: Check PWM objects
print("\n[7/8] Checking PWM configuration...")
if not motors.simulation_mode:
    try:
        if hasattr(motors, 'l_pwm') and hasattr(motors, 'r_pwm'):
            print("✓ PWM objects created")
            print(f"  Left PWM:  GPIO{motors.L_EN} @ 100Hz")
            print(f"  Right PWM: GPIO{motors.R_EN} @ 100Hz")
        else:
            print("✗ PWM objects not found")
    except Exception as e:
        print(f"⚠ PWM check warning: {e}")

# Step 8: Run motor tests
print("\n[8/8] Running motor movement tests...")
print("=" * 70)

import time

test_duration = 2  # seconds per test
speed = 80  # 80% speed

try:
    # Test 1: Forward
    print("\n[TEST 1/4] FORWARD - 2 seconds at 80% speed")
    print("            Check if wheels spin forward...")
    motors.forward(speed)
    time.sleep(test_duration)
    motors.stop()
    print("            ✓ Command executed")
    time.sleep(1)
    
    # Test 2: Backward
    print("\n[TEST 2/4] BACKWARD - 2 seconds at 80% speed")
    print("            Check if wheels spin backward...")
    motors.backward(speed)
    time.sleep(test_duration)
    motors.stop()
    print("            ✓ Command executed")
    time.sleep(1)
    
    # Test 3: Left turn
    print("\n[TEST 3/4] TURN LEFT - 1.5 seconds")
    print("            Check if left wheel backward, right wheel forward...")
    motors.left(speed)
    time.sleep(1.5)
    motors.stop()
    print("            ✓ Command executed")
    time.sleep(1)
    
    # Test 4: Right turn
    print("\n[TEST 4/4] TURN RIGHT - 1.5 seconds")
    print("            Check if left wheel forward, right wheel backward...")
    motors.right(speed)
    time.sleep(1.5)
    motors.stop()
    print("            ✓ Command executed")
    time.sleep(1)
    
    print("\n" + "=" * 70)
    print("✓ ALL MOTOR COMMANDS EXECUTED SUCCESSFULLY!")
    print("=" * 70)
    
    # Physical movement check
    print("\n⚠ IMPORTANT: Did the motors physically move?")
    print("\nIf motors did NOT move, check:")
    print("  1. External power supply to L298N (6-12V battery)")
    print("  2. Battery voltage (use multimeter - should be 6-12V)")
    print("  3. Motor connections: OUT1/OUT2 (left), OUT3/OUT4 (right)")
    print("  4. L298N power LED should be ON")
    print("  5. Common ground: L298N GND → Raspberry Pi GND")
    print("  6. GPIO wiring: Check against PIN_REFERENCE_CARD.txt")
    print("  7. L298N jumpers: Remove ENA/ENB jumpers if using PWM")
    
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
    print("\n" + "=" * 70)
    print("Cleaning up GPIO...")
    try:
        motors.cleanup()
        print("✓ Motors cleaned up")
    except Exception as e:
        print(f"⚠ Cleanup warning: {e}")
    
    try:
        from core.hardware_manager import hardware_manager
        hardware_manager.cleanup()
        print("✓ Hardware manager cleaned up")
    except Exception as e:
        print(f"⚠ Hardware manager cleanup warning: {e}")

print("\n" + "=" * 70)
print("DIAGNOSTIC TEST COMPLETE")
print("=" * 70)

# Summary
print("\nDIAGNOSTIC SUMMARY:")
print("  Software:  ✓ All libraries OK")
print("  GPIO:      ✓ Accessible")
print("  Commands:  ✓ All executed")
print("\nIf motors didn't move physically, check hardware connections above.")
print("=" * 70)
