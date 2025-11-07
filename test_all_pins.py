#!/usr/bin/env python3
"""
Complete Hardware Pin Test for JARVIS
Tests all GPIO pins and connected components individually.
"""

import os
import sys
import time
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("=" * 80)
print("JARVIS COMPLETE HARDWARE PIN TEST")
print("=" * 80)
print("\nThis script will test all GPIO pins and connected hardware.")
print("Make sure all components are properly wired before proceeding!\n")

def test_servo(servo_name):
    """Test a specific servo."""
    print(f"\n{'='*80}")
    print(f"TESTING SERVO: {servo_name.upper()}")
    print(f"{'='*80}")
    
    try:
        from actuators.multi_servo_controller import multi_servo_controller
        import time
        
        servo = multi_servo_controller.get_servo(servo_name)
        if not servo:
            print(f"❌ Servo '{servo_name}' not found in controller")
            return False
        
        pin = servo.pin
        print(f"✅ Servo '{servo_name}' found on GPIO {pin}")
        
        print(f"\n🔄 Testing {servo_name} servo movement...")
        print("   Watch the servo - it should move to different positions")
        
        # Center position
        print(f"   → Moving to center (90°)...")
        servo.set_angle(90)
        time.sleep(1)
        
        # Left/Right sweep
        positions = [60, 120, 30, 150, 90]
        for angle in positions:
            print(f"   → Moving to {angle}°...")
            servo.set_angle(angle)
            time.sleep(0.8)
        
        # Back to center
        print(f"   → Returning to center (90°)...")
        servo.set_angle(90)
        time.sleep(0.5)
        
        print(f"\n✅ {servo_name.upper()} servo test PASSED!")
        print(f"   If servo didn't move, check:")
        print(f"   - Signal wire connected to GPIO {pin}")
        print(f"   - VCC (red) connected to 5V")
        print(f"   - GND (brown/black) connected to GND")
        print(f"   - Servo has power")
        return True
        
    except Exception as e:
        print(f"❌ {servo_name.upper()} servo test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ultrasonic():
    """Test ultrasonic sensor."""
    print(f"\n{'='*80}")
    print("TESTING ULTRASONIC SENSOR (HC-SR04)")
    print(f"{'='*80}")
    
    try:
        from sensors.ultrasonic import Ultrasonic
        
        trigger_pin = 27
        echo_pin = 22
        
        print(f"✅ Ultrasonic sensor on TRIGGER=GPIO{trigger_pin}, ECHO=GPIO{echo_pin}")
        
        sensor = Ultrasonic(trigger_pin, echo_pin)
        
        print(f"\n🔄 Taking 5 distance measurements...")
        print("   Place an object 10-100cm in front of sensor")
        
        readings = []
        for i in range(5):
            dist = sensor.measure_distance()
            readings.append(dist)
            
            if dist > 0:
                print(f"   Reading {i+1}: {dist:.1f} cm ✓")
            else:
                print(f"   Reading {i+1}: Error (-1) ✗")
            
            time.sleep(0.5)
        
        valid_readings = [r for r in readings if r > 0]
        
        if len(valid_readings) >= 3:
            avg = sum(valid_readings) / len(valid_readings)
            print(f"\n✅ ULTRASONIC sensor test PASSED!")
            print(f"   Average distance: {avg:.1f} cm")
            print(f"   Valid readings: {len(valid_readings)}/5")
            return True
        else:
            print(f"\n⚠️  ULTRASONIC sensor test WARNING!")
            print(f"   Only {len(valid_readings)}/5 valid readings")
            print(f"   Check wiring:")
            print(f"   - TRIGGER → GPIO 27")
            print(f"   - ECHO → GPIO 22")
            print(f"   - VCC → 5V")
            print(f"   - GND → GND")
            return False
            
    except Exception as e:
        print(f"❌ ULTRASONIC sensor test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_pir():
    """Test PIR motion sensor."""
    print(f"\n{'='*80}")
    print("TESTING PIR MOTION SENSOR")
    print(f"{'='*80}")
    
    try:
        from sensors.pir import PIR
        import threading
        
        pin = 17
        print(f"✅ PIR sensor on GPIO {pin}")
        
        motion_detected = threading.Event()
        
        def on_motion():
            motion_detected.set()
            print(f"\n   🚨 MOTION DETECTED! ✅")
        
        pir = PIR(pin, on_motion_callback=on_motion)
        pir.start_monitoring()
        
        print(f"\n🔄 Monitoring for motion (15 seconds)...")
        print("   Wave your hand in front of the PIR sensor")
        
        time.sleep(15)
        
        pir.stop_monitoring()
        
        if motion_detected.is_set():
            print(f"\n✅ PIR sensor test PASSED!")
            print(f"   Motion was detected successfully")
            return True
        else:
            print(f"\n⚠️  PIR sensor test WARNING!")
            print(f"   No motion detected in 15 seconds")
            print(f"   Check wiring:")
            print(f"   - OUT → GPIO 17")
            print(f"   - VCC → 5V")
            print(f"   - GND → GND")
            print(f"   Or wait longer and try again")
            return False
            
    except Exception as e:
        print(f"❌ PIR sensor test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_dht():
    """Test DHT11 temperature/humidity sensor."""
    print(f"\n{'='*80}")
    print("TESTING DHT11 SENSOR")
    print(f"{'='*80}")
    
    try:
        from sensors.sensor_manager import SensorManager
        
        pin = 4
        print(f"✅ DHT11 sensor on GPIO {pin}")
        
        sensors = SensorManager()
        
        print(f"\n🔄 Reading temperature and humidity...")
        
        temp = sensors.get_temperature()
        humidity = sensors.get_humidity()
        
        if temp is not None and humidity is not None:
            print(f"\n✅ DHT11 sensor test PASSED!")
            print(f"   Temperature: {temp:.1f}°C")
            print(f"   Humidity: {humidity:.1f}%")
            return True
        else:
            print(f"\n⚠️  DHT11 sensor test WARNING!")
            print(f"   Could not read temperature/humidity")
            print(f"   Check wiring:")
            print(f"   - DATA → GPIO 4")
            print(f"   - VCC → 3.3V (NOT 5V!)")
            print(f"   - GND → GND")
            print(f"   May need 4.7kΩ pull-up resistor on data line")
            return False
            
    except Exception as e:
        print(f"❌ DHT11 sensor test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_motors():
    """Test motor controller."""
    print(f"\n{'='*80}")
    print("TESTING MOTOR CONTROLLER (L298N)")
    print(f"{'='*80}")
    
    print("\n⚠️  WARNING: Motors will move!")
    print("   - Ensure robot is on blocks (wheels off ground)")
    print("   - Or in open area with clear path")
    print("   - Be ready to stop if needed")
    
    response = input("\n   Continue? (yes/no): ").strip().lower()
    if response != 'yes':
        print("   Skipping motor test")
        return None
    
    try:
        from actuators.motor_controller import MotorController
        
        print(f"\n✅ Motor pins:")
        print(f"   Left Motor:  ENA=GPIO12, IN1=GPIO5,  IN2=GPIO6")
        print(f"   Right Motor: ENB=GPIO13, IN3=GPIO26, IN4=GPIO16")
        
        motors = MotorController()
        
        speed = 40  # Low speed for safety
        duration = 1.5
        
        print(f"\n🔄 Testing motor movements (speed={speed})...")
        
        print(f"   → Forward for {duration}s...")
        motors.forward(speed=speed, duration=duration)
        time.sleep(0.5)
        
        print(f"   → Backward for {duration}s...")
        motors.backward(speed=speed, duration=duration)
        time.sleep(0.5)
        
        print(f"   → Left turn for {duration}s...")
        motors.left(speed=speed, duration=duration)
        time.sleep(0.5)
        
        print(f"   → Right turn for {duration}s...")
        motors.right(speed=speed, duration=duration)
        time.sleep(0.5)
        
        print(f"   → Stop")
        motors.stop()
        
        print(f"\n✅ MOTOR controller test PASSED!")
        print(f"   If motors didn't spin, check:")
        print(f"   - All 6 GPIO pins connected correctly")
        print(f"   - 12V power supply connected to L298N")
        print(f"   - Motors connected to OUT1-4")
        print(f"   - Common ground between Pi and L298N")
        return True
        
    except Exception as e:
        print(f"❌ MOTOR controller test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_display():
    """Test I2C display."""
    print(f"\n{'='*80}")
    print("TESTING I2C DISPLAY (16x2 LCD)")
    print(f"{'='*80}")
    
    try:
        from actuators.display import display
        
        print(f"✅ I2C Display on GPIO2 (SDA), GPIO3 (SCL)")
        print(f"   Address: 0x27 (or 0x3F)")
        
        print(f"\n🔄 Testing display...")
        print("   Watch the LCD screen")
        
        # Test 1: Clear and write
        print(f"   → Clearing display...")
        display.clear()
        time.sleep(0.5)
        
        print(f"   → Writing 'JARVIS'...")
        display.write_text("JARVIS", row=0, col=5)
        time.sleep(1)
        
        print(f"   → Writing 'Pin Test OK!'...")
        display.write_text("Pin Test OK!", row=1, col=1)
        time.sleep(2)
        
        # Test 2: Show face
        print(f"   → Showing happy face...")
        display.show_face('happy')
        time.sleep(2)
        
        # Test 3: Show neutral
        print(f"   → Showing neutral face...")
        display.show_face('neutral')
        time.sleep(1)
        
        print(f"\n✅ I2C DISPLAY test PASSED!")
        print(f"   If nothing appeared on screen, check:")
        print(f"   - SDA → GPIO 2 (Pin 3)")
        print(f"   - SCL → GPIO 3 (Pin 5)")
        print(f"   - VCC → 5V")
        print(f"   - GND → GND")
        print(f"   - I2C enabled: sudo raspi-config")
        print(f"   - Check address: sudo i2cdetect -y 1")
        return True
        
    except Exception as e:
        print(f"❌ I2C DISPLAY test FAILED: {e}")
        print(f"\n   Troubleshooting:")
        print(f"   - Run: sudo i2cdetect -y 1")
        print(f"   - Should see device at 0x27 or 0x3F")
        print(f"   - If not, check wiring and I2C enable")
        import traceback
        traceback.print_exc()
        return False


def test_all():
    """Test all components."""
    print(f"\n{'='*80}")
    print("TESTING ALL COMPONENTS")
    print(f"{'='*80}\n")
    
    results = {}
    
    # Test servos
    results['Neck Servo'] = test_servo('neck')
    results['Left Arm Servo'] = test_servo('arm_l')
    results['Right Arm Servo'] = test_servo('arm_r')
    
    # Test sensors
    results['Ultrasonic Sensor'] = test_ultrasonic()
    results['PIR Sensor'] = test_pir()
    results['DHT11 Sensor'] = test_dht()
    
    # Test display
    results['I2C Display'] = test_display()
    
    # Test motors (optional)
    motor_result = test_motors()
    if motor_result is not None:
        results['Motor Controller'] = motor_result
    
    # Summary
    print(f"\n{'='*80}")
    print("TEST SUMMARY")
    print(f"{'='*80}\n")
    
    for component, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"   {component:20s} : {status}")
    
    passed_count = sum(1 for p in results.values() if p)
    total_count = len(results)
    
    print(f"\n{'='*80}")
    print(f"TOTAL: {passed_count}/{total_count} components passed")
    print(f"{'='*80}\n")
    
    if passed_count == total_count:
        print("🎉 ALL TESTS PASSED! Hardware is ready!")
        print("\nYou can now run: ./run.sh")
    else:
        print("⚠️  Some tests failed. Check wiring and try again.")
        print("\nSee COMPLETE_PIN_CONFIGURATION.md for wiring details")


def main():
    parser = argparse.ArgumentParser(description='Test JARVIS hardware pins')
    parser.add_argument('--all', action='store_true', help='Test all components')
    parser.add_argument('--servo', type=str, choices=['neck', 'arm_l', 'arm_r'], help='Test specific servo')
    parser.add_argument('--ultrasonic', action='store_true', help='Test ultrasonic sensor')
    parser.add_argument('--pir', action='store_true', help='Test PIR sensor')
    parser.add_argument('--dht', action='store_true', help='Test DHT11 sensor')
    parser.add_argument('--motors', action='store_true', help='Test motor controller')
    parser.add_argument('--display', action='store_true', help='Test I2C display')
    
    args = parser.parse_args()
    
    # If no specific test selected, run all
    if not any([args.servo, args.ultrasonic, args.pir, args.dht, args.motors, args.display, args.all]):
        args.all = True
    
    try:
        if args.all:
            test_all()
        else:
            if args.servo:
                test_servo(args.servo)
            if args.ultrasonic:
                test_ultrasonic()
            if args.pir:
                test_pir()
            if args.dht:
                test_dht()
            if args.motors:
                test_motors()
            if args.display:
                test_display()
        
        print("\n" + "="*80)
        print("Test complete!")
        print("="*80 + "\n")
        
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        try:
            from core.hardware_manager import hardware_manager
            hardware_manager.cleanup()
        except:
            pass


if __name__ == '__main__':
    main()
