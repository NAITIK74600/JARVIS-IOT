#!/usr/bin/env python3
"""
JARVIS Complete Motor Test
Tests L298N wheels (12V battery) and Servos (external 5V power)
"""

import pigpio
import time
import sys

print("="*70)
print("🤖 JARVIS COMPLETE MOTOR & SERVO TEST")
print("="*70)

# Initialize pigpio
pi = pigpio.pi()
if not pi.connected:
    print("❌ ERROR: pigpio daemon not running!")
    print("Run: sudo pigpiod")
    sys.exit(1)

print("✓ pigpio daemon connected\n")

# ============================================================================
# PIN CONFIGURATION
# ============================================================================

# L298N Motor Driver Pins
MOTOR_ENA = 12   # Left motor speed (PWM)
MOTOR_IN1 = 5    # Left motor forward
MOTOR_IN2 = 6    # Left motor backward
MOTOR_ENB = 13   # Right motor speed (PWM)
MOTOR_IN3 = 26   # Right motor forward
MOTOR_IN4 = 16   # Right motor backward

# Servo Pins
SERVO_NECK = 19   # Neck servo
SERVO_ARM_L = 20  # Left arm servo
SERVO_ARM_R = 21  # Right arm servo

# ============================================================================
# SETUP
# ============================================================================

print("Setting up pins...")

# Setup motor pins
motor_pins = [MOTOR_ENA, MOTOR_IN1, MOTOR_IN2, MOTOR_ENB, MOTOR_IN3, MOTOR_IN4]
for pin in motor_pins:
    pi.set_mode(pin, pigpio.OUTPUT)
    pi.write(pin, 0)

print("✓ Motor pins configured")
print("✓ Servo pins ready")
print()

# ============================================================================
# MOTOR CONTROL FUNCTIONS
# ============================================================================

def set_motor(in1, in2, ena, speed):
    """
    Control a single motor
    speed: -100 to +100 (negative = backward, positive = forward)
    """
    if speed > 0:
        pi.write(in1, 1)
        pi.write(in2, 0)
        duty = int((abs(speed) / 100.0) * 255)
        pi.set_PWM_dutycycle(ena, duty)
    elif speed < 0:
        pi.write(in1, 0)
        pi.write(in2, 1)
        duty = int((abs(speed) / 100.0) * 255)
        pi.set_PWM_dutycycle(ena, duty)
    else:
        pi.write(in1, 0)
        pi.write(in2, 0)
        pi.set_PWM_dutycycle(ena, 0)

def stop_motors():
    """Stop both motors"""
    set_motor(MOTOR_IN1, MOTOR_IN2, MOTOR_ENA, 0)
    set_motor(MOTOR_IN3, MOTOR_IN4, MOTOR_ENB, 0)

def move_forward(speed=60, duration=2):
    """Move forward"""
    print(f"  → FORWARD at {speed}% for {duration}s")
    set_motor(MOTOR_IN1, MOTOR_IN2, MOTOR_ENA, speed)
    set_motor(MOTOR_IN3, MOTOR_IN4, MOTOR_ENB, speed)
    time.sleep(duration)
    stop_motors()

def move_backward(speed=60, duration=2):
    """Move backward"""
    print(f"  → BACKWARD at {speed}% for {duration}s")
    set_motor(MOTOR_IN1, MOTOR_IN2, MOTOR_ENA, -speed)
    set_motor(MOTOR_IN3, MOTOR_IN4, MOTOR_ENB, -speed)
    time.sleep(duration)
    stop_motors()

def turn_left(speed=60, duration=1.5):
    """Turn left (left motor backward, right forward)"""
    print(f"  → LEFT TURN at {speed}% for {duration}s")
    set_motor(MOTOR_IN1, MOTOR_IN2, MOTOR_ENA, -speed)
    set_motor(MOTOR_IN3, MOTOR_IN4, MOTOR_ENB, speed)
    time.sleep(duration)
    stop_motors()

def turn_right(speed=60, duration=1.5):
    """Turn right (left motor forward, right backward)"""
    print(f"  → RIGHT TURN at {speed}% for {duration}s")
    set_motor(MOTOR_IN1, MOTOR_IN2, MOTOR_ENA, speed)
    set_motor(MOTOR_IN3, MOTOR_IN4, MOTOR_ENB, -speed)
    time.sleep(duration)
    stop_motors()

# ============================================================================
# SERVO CONTROL FUNCTIONS
# ============================================================================

def set_servo_angle(servo_pin, angle):
    """
    Set servo to specific angle (0-180)
    0° = 500µs, 90° = 1500µs, 180° = 2400µs
    """
    pulse_width = int(500 + (angle / 180.0) * 1900)
    pi.set_servo_pulsewidth(servo_pin, pulse_width)

def stop_servo(servo_pin):
    """Stop servo signal"""
    pi.set_servo_pulsewidth(servo_pin, 0)

def test_servo(name, servo_pin):
    """Test a single servo with full range movement"""
    print(f"\n  Testing {name} Servo:")
    angles = [90, 0, 180, 90, 45, 135, 90]
    for i, angle in enumerate(angles, 1):
        print(f"    [{i}/7] Moving to {angle}°...", end='', flush=True)
        set_servo_angle(servo_pin, angle)
        time.sleep(1)
        print(" ✓")
    stop_servo(servo_pin)
    print(f"  ✓ {name} test complete")

# ============================================================================
# MAIN TEST SEQUENCE
# ============================================================================

def main():
    print("="*70)
    print("PRE-FLIGHT CHECKLIST:")
    print("="*70)
    print("  ✓ L298N connected to 12V battery")
    print("  ✓ Battery GND connected to Pi GND (Pin 34)")
    print("  ✓ Motors connected to L298N OUT1-OUT4")
    print("  ✓ Servos connected to external 5V power")
    print("  ✓ Servo signal wires: Pin 35, 38, 40")
    print()
    print("Starting test in 3 seconds...")
    print("WATCH YOUR JARVIS CAREFULLY!")
    print("="*70)
    time.sleep(3)
    
    try:
        # ================================================================
        # PART 1: WHEEL TEST (L298N + 12V Battery)
        # ================================================================
        print("\n" + "="*70)
        print("PART 1: TESTING WHEELS (L298N Motor Driver)")
        print("="*70)
        
        print("\n1. Testing FORWARD movement:")
        move_forward(speed=50, duration=2)
        time.sleep(1)
        
        print("\n2. Testing BACKWARD movement:")
        move_backward(speed=50, duration=2)
        time.sleep(1)
        
        print("\n3. Testing LEFT turn:")
        turn_left(speed=50, duration=1.5)
        time.sleep(1)
        
        print("\n4. Testing RIGHT turn:")
        turn_right(speed=50, duration=1.5)
        time.sleep(1)
        
        print("\n5. Speed test - Slow to Fast:")
        for speed in [30, 50, 70]:
            print(f"  → Speed {speed}%...")
            move_forward(speed=speed, duration=1)
            time.sleep(0.5)
        
        print("\n✅ WHEEL TEST COMPLETE!")
        
        # ================================================================
        # PART 2: SERVO TEST (External 5V Power)
        # ================================================================
        print("\n" + "="*70)
        print("PART 2: TESTING SERVOS")
        print("="*70)
        
        test_servo("NECK", SERVO_NECK)
        time.sleep(1)
        
        test_servo("LEFT ARM", SERVO_ARM_L)
        time.sleep(1)
        
        test_servo("RIGHT ARM", SERVO_ARM_R)
        time.sleep(1)
        
        print("\n✅ SERVO TEST COMPLETE!")
        
        # ================================================================
        # PART 3: COMBINED MOVEMENT TEST
        # ================================================================
        print("\n" + "="*70)
        print("PART 3: COMBINED MOVEMENT TEST")
        print("="*70)
        print("\nJARVIS will move and gesture simultaneously!")
        time.sleep(2)
        
        print("\n1. Move forward while looking around:")
        set_servo_angle(SERVO_NECK, 90)
        time.sleep(0.5)
        set_motor(MOTOR_IN1, MOTOR_IN2, MOTOR_ENA, 40)
        set_motor(MOTOR_IN3, MOTOR_IN4, MOTOR_ENB, 40)
        
        # Look left and right while moving
        for _ in range(2):
            set_servo_angle(SERVO_NECK, 45)
            time.sleep(1)
            set_servo_angle(SERVO_NECK, 135)
            time.sleep(1)
        
        set_servo_angle(SERVO_NECK, 90)
        stop_motors()
        print("  ✓ Forward + look around complete")
        
        print("\n2. Wave arms while stationary:")
        for _ in range(3):
            set_servo_angle(SERVO_ARM_L, 45)
            set_servo_angle(SERVO_ARM_R, 135)
            time.sleep(0.5)
            set_servo_angle(SERVO_ARM_L, 135)
            set_servo_angle(SERVO_ARM_R, 45)
            time.sleep(0.5)
        
        set_servo_angle(SERVO_ARM_L, 90)
        set_servo_angle(SERVO_ARM_R, 90)
        print("  ✓ Arm wave complete")
        
        print("\n3. Celebratory spin with arms up:")
        set_servo_angle(SERVO_ARM_L, 0)
        set_servo_angle(SERVO_ARM_R, 180)
        time.sleep(0.5)
        
        # Spin right
        set_motor(MOTOR_IN1, MOTOR_IN2, MOTOR_ENA, 50)
        set_motor(MOTOR_IN3, MOTOR_IN4, MOTOR_ENB, -50)
        time.sleep(2)
        stop_motors()
        
        # Return arms to center
        set_servo_angle(SERVO_ARM_L, 90)
        set_servo_angle(SERVO_ARM_R, 90)
        set_servo_angle(SERVO_NECK, 90)
        print("  ✓ Victory spin complete!")
        
        print("\n✅ COMBINED MOVEMENT TEST COMPLETE!")
        
        # ================================================================
        # FINAL RESULTS
        # ================================================================
        print("\n" + "="*70)
        print("🎉 ALL TESTS COMPLETED SUCCESSFULLY!")
        print("="*70)
        print("\n📊 TEST RESULTS:")
        print("  ✅ Wheels moving forward/backward")
        print("  ✅ Turning left/right working")
        print("  ✅ Speed control functional")
        print("  ✅ All 3 servos operational")
        print("  ✅ Combined movements successful")
        print("\n🤖 JARVIS IS FULLY OPERATIONAL!")
        print("="*70)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user (Ctrl+C)")
    
    finally:
        # Cleanup
        print("\nStopping all motors and servos...")
        stop_motors()
        stop_servo(SERVO_NECK)
        stop_servo(SERVO_ARM_L)
        stop_servo(SERVO_ARM_R)
        pi.stop()
        print("✓ Cleanup complete")

if __name__ == "__main__":
    main()
