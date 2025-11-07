#!/usr/bin/env python3
"""
Motor Power Diagnostic - Find why motors make sound but don't move
This tests power levels, wiring, and motor driver issues
"""

import time
import sys

print("=" * 70)
print("MOTOR POWER DIAGNOSTIC - Sound but No Movement")
print("=" * 70)

try:
    from actuators.motor_controller import MotorController
    from core.hardware_manager import hardware_manager
except ImportError as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)

motors = MotorController()

print(f"\nMotor Configuration:")
print(f"  Simulation Mode: {motors.simulation_mode}")
print(f"  Left Motor:  EN=GPIO{motors.L_EN}, IN1=GPIO{motors.L_IN1}, IN2=GPIO{motors.L_IN2}")
print(f"  Right Motor: EN=GPIO{motors.R_EN}, IN1=GPIO{motors.R_IN1}, IN2=GPIO{motors.R_IN2}")

print("\n" + "=" * 70)
print("DIAGNOSIS: Motor makes sound but doesn't move")
print("=" * 70)
print("\nPossible causes:")
print("  1. Speed too LOW (PWM duty cycle insufficient)")
print("  2. External power supply voltage too LOW")
print("  3. Motor driver overheating (thermal shutdown)")
print("  4. Motor connections loose")
print("  5. ENA/ENB jumpers still ON (bypassing PWM)")
print("  6. Motor stall (mechanical obstruction)")

print("\n" + "=" * 70)
print("RUNNING PROGRESSIVE POWER TESTS")
print("=" * 70)

try:
    # Test 1: Speed ramp from 50% to 100%
    print("\n[TEST 1] FORWARD - Speed ramp 50% → 100%")
    print("         Watch carefully for when motors START moving")
    for speed in range(50, 101, 10):
        print(f"\n  Speed: {speed}%", end=" ", flush=True)
        motors.forward(speed)
        time.sleep(2)
        motors.stop()
        input("    Did motors MOVE? (Press Enter to continue)")
        time.sleep(0.5)
    
    print("\n" + "=" * 70)
    
    # Test 2: Maximum power test (100%)
    print("\n[TEST 2] MAXIMUM POWER TEST (100% for 5 seconds)")
    print("         Motors should DEFINITELY move at 100%")
    print("         Starting in 3 seconds...")
    time.sleep(3)
    motors.forward(100)
    time.sleep(5)
    motors.stop()
    
    moved = input("\n  Did motors MOVE at 100%? (yes/no): ").lower().strip()
    
    print("\n" + "=" * 70)
    
    if moved == "yes" or moved == "y":
        print("\n✓ MOTORS WORK! Finding minimum working speed...")
        
        # Test 3: Find minimum working speed
        print("\n[TEST 3] Finding MINIMUM working speed")
        for speed in range(60, 101, 5):
            print(f"\n  Testing {speed}%...", end=" ", flush=True)
            motors.forward(speed)
            time.sleep(2)
            motors.stop()
            works = input("Moved? (y/n): ").lower().strip()
            if works == "y" or works == "yes":
                print(f"\n✓ Minimum working speed found: {speed}%")
                print(f"  Recommendation: Use {speed}% or higher for reliable movement")
                break
            time.sleep(0.5)
    
    else:
        print("\n✗ MOTORS NOT MOVING even at 100% power")
        print("\n" + "=" * 70)
        print("HARDWARE TROUBLESHOOTING CHECKLIST:")
        print("=" * 70)
        
        print("\n1. CHECK EXTERNAL POWER SUPPLY:")
        print("   • Use multimeter to measure voltage at L298N +12V terminal")
        print("   • Should read 6-12V (ideally 9-12V for good torque)")
        print("   • If < 6V, battery is dead or power supply insufficient")
        print("   • L298N needs 1-3A current, ensure power supply can deliver")
        
        print("\n2. CHECK L298N BOARD:")
        print("   • Power LED should be ON (red LED near power input)")
        print("   • If LED is OFF → check power connections")
        print("   • Feel heat sink - should be warm but not burning hot")
        print("   • If VERY HOT → thermal shutdown, let cool and try again")
        
        print("\n3. CHECK MOTOR CONNECTIONS:")
        print("   • Left motor connected to OUT1 & OUT2?")
        print("   • Right motor connected to OUT3 & OUT4?")
        print("   • Try swapping motor wires (reverse polarity)")
        print("   • Disconnect motors and measure voltage at OUT pins while running")
        
        print("\n4. CHECK ENA/ENB JUMPERS:")
        print("   • Remove blue/yellow jumper caps from ENA and ENB pins")
        print("   • Jumpers ON = motors run at 100% only (no PWM control)")
        print("   • Jumpers OFF = PWM speed control works")
        
        print("\n5. VERIFY GPIO WIRING:")
        gpio_check = """
   FROM RASPBERRY PI              TO L298N
   Pin 32 (GPIO 12) ────────────→ ENA
   Pin 29 (GPIO 5)  ────────────→ IN1
   Pin 31 (GPIO 6)  ────────────→ IN2
   Pin 33 (GPIO 13) ────────────→ ENB
   Pin 37 (GPIO 26) ────────────→ IN3
   Pin 36 (GPIO 16) ────────────→ IN4
   Pin 34 (GND)     ────────────→ GND
        """
        print(gpio_check)
        
        print("\n6. TEST MOTORS DIRECTLY:")
        print("   • Disconnect motors from L298N")
        print("   • Connect motor directly to 6-9V battery")
        print("   • If motor doesn't spin → motor is broken")
        print("   • If motor spins → L298N or wiring issue")
        
        print("\n7. MEASURE VOLTAGES:")
        print("   • With multimeter in DC voltage mode:")
        print("   • Measure at L298N OUT1-OUT2 while forward() running")
        print("   • Should read battery voltage (6-12V)")
        print("   • If 0V → L298N not switching or GPIO signals wrong")
        print("   • If correct voltage but motor not moving → motor problem")
    
    print("\n" + "=" * 70)
    print("DIAGNOSTIC COMPLETE")
    print("=" * 70)

except KeyboardInterrupt:
    print("\n\n⚠ Test interrupted")
    motors.stop()

except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
    motors.stop()

finally:
    print("\nCleaning up...")
    try:
        motors.cleanup()
        hardware_manager.cleanup()
        print("✓ Cleanup complete")
    except Exception as e:
        print(f"⚠ Cleanup warning: {e}")

print("\n" + "=" * 70)
print("Next steps:")
print("  1. Check power supply voltage (most common issue)")
print("  2. Remove ENA/ENB jumpers if present")
print("  3. Ensure common ground between Pi and L298N")
print("  4. Test with fully charged battery (9-12V recommended)")
print("=" * 70)
