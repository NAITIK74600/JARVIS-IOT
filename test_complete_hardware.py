#!/usr/bin/env python3
"""
Complete Hardware Testing Script for JARVIS
Tests each component individually and provides detailed status

Run this after completing wiring to verify all connections!
"""

import os
import sys
import time
from datetime import datetime

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(60)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")

def print_success(text):
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")

def print_fail(text):
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")

def print_warning(text):
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")

def print_info(text):
    print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")

def wait_for_user(prompt="Press Enter to continue..."):
    input(f"{Colors.BOLD}{prompt}{Colors.ENDC}")

# Test results tracking
test_results = {
    "pigpiod": False,
    "dht11": False,
    "pir": False,
    "ultrasonic": False,
    "mq3": False,
    "servos": False,
    "motors": False,
}

def test_pigpiod():
    """Test if pigpiod daemon is running"""
    print_header("TEST 1: pigpiod Daemon")
    print_info("Checking if pigpiod daemon is running...")
    
    result = os.system("pgrep pigpiod > /dev/null 2>&1")
    if result == 0:
        print_success("pigpiod is running")
        test_results["pigpiod"] = True
        return True
    else:
        print_fail("pigpiod is NOT running")
        print_warning("Starting pigpiod daemon...")
        os.system("sudo pigpiod")
        time.sleep(2)
        result = os.system("pgrep pigpiod > /dev/null 2>&1")
        if result == 0:
            print_success("pigpiod started successfully")
            test_results["pigpiod"] = True
            return True
        else:
            print_fail("Failed to start pigpiod. Run: sudo pigpiod")
            return False

def test_dht11():
    """Test DHT11 temperature and humidity sensor"""
    print_header("TEST 2: DHT11 Temperature/Humidity Sensor")
    print_info("Pin: GPIO 4 (Physical Pin 7)")
    print_info("Reading sensor data...")
    
    try:
        from sensors.dht import DHT
        dht = DHT(pin=4, sensor_type='DHT11')
        
        # Try 3 readings
        success = False
        for attempt in range(3):
            temp = dht.read_temperature()
            humidity = dht.read_humidity()
            
            if temp is not None and humidity is not None:
                print_success(f"Temperature: {temp:.1f}°C")
                print_success(f"Humidity: {humidity:.1f}%")
                success = True
                test_results["dht11"] = True
                break
            else:
                print_warning(f"Attempt {attempt+1}/3 failed, retrying...")
                time.sleep(2)
        
        if not success:
            print_fail("DHT11 sensor not responding")
            print_info("Check: VCC→+5V, GND→GND, DATA→GPIO 4")
            
        dht.close()
        return success
        
    except Exception as e:
        print_fail(f"DHT11 test failed: {e}")
        return False

def test_pir():
    """Test PIR motion sensor"""
    print_header("TEST 3: PIR Motion Sensor")
    print_info("Pin: GPIO 17 (Physical Pin 11)")
    print_info("Wave your hand in front of the sensor for 10 seconds...")
    
    try:
        from sensors.pir import PIR
        
        motion_detected = [False]
        
        def on_motion():
            motion_detected[0] = True
            print_success("MOTION DETECTED!")
        
        pir = PIR(pin=17, on_motion_callback=on_motion)
        pir.start_monitoring()
        
        print_info("Waiting for motion (calibrating for 2 seconds)...")
        time.sleep(2)
        print_info("NOW wave your hand!")
        
        start = time.time()
        while time.time() - start < 10:
            if motion_detected[0]:
                break
            time.sleep(0.1)
        
        pir.stop_monitoring()
        
        if motion_detected[0]:
            print_success("PIR sensor working correctly")
            test_results["pir"] = True
            return True
        else:
            print_warning("No motion detected")
            print_info("Check: VCC→+5V, GND→GND, OUT→GPIO 17")
            print_info("Adjust sensitivity pot on PIR sensor if needed")
            return False
            
    except Exception as e:
        print_fail(f"PIR test failed: {e}")
        return False

def test_ultrasonic():
    """Test HC-SR04 ultrasonic distance sensor"""
    print_header("TEST 4: HC-SR04 Ultrasonic Sensor")
    print_info("TRIG: GPIO 23 (Pin 16), ECHO: GPIO 24 (Pin 18)")
    print_warning("⚠️  ECHO must use voltage divider (1kΩ + 2kΩ)!")
    print_info("Taking 5 distance measurements...")
    
    try:
        from sensors.ultrasonic import Ultrasonic
        
        ultrasonic = Ultrasonic(trigger_pin=23, echo_pin=24)
        
        readings = []
        for i in range(5):
            dist = ultrasonic.measure_distance()
            if dist > 0:
                readings.append(dist)
                print_success(f"Reading {i+1}: {dist:.1f} cm")
            else:
                print_fail(f"Reading {i+1}: Failed (timeout)")
            time.sleep(0.5)
        
        if len(readings) >= 3:
            avg = sum(readings) / len(readings)
            print_success(f"Average distance: {avg:.1f} cm")
            print_info("Move your hand closer/farther to verify readings change")
            test_results["ultrasonic"] = True
            return True
        else:
            print_fail("Too many failed readings")
            print_info("Check: VCC→+5V, GND→GND, TRIG→GPIO23")
            print_warning("CRITICAL: ECHO→Voltage Divider→GPIO24")
            return False
            
    except Exception as e:
        print_fail(f"Ultrasonic test failed: {e}")
        return False

def test_mq3():
    """Test MQ-3 alcohol/gas sensor"""
    print_header("TEST 5: MQ-3 Alcohol/Gas Sensor (Optional)")
    print_info("Requires ADS1115 ADC module on I2C")
    print_info("SDA: GPIO 2 (Pin 3), SCL: GPIO 3 (Pin 5)")
    
    try:
        from sensors.mq3 import MQ3
        
        mq3 = MQ3(channel=0)
        
        print_info("Taking 3 readings...")
        readings = []
        for i in range(3):
            level = mq3.read_alcohol_level()
            if level is not None:
                readings.append(level)
                print_success(f"Reading {i+1}: {level:.2f} mg/L")
            else:
                print_warning(f"Reading {i+1}: No data")
            time.sleep(1)
        
        if len(readings) > 0:
            print_success("MQ-3 sensor responding")
            test_results["mq3"] = True
            return True
        else:
            print_warning("MQ-3 not detected (optional sensor)")
            print_info("If you don't have ADS1115, you can skip this")
            return False
            
    except Exception as e:
        print_warning(f"MQ-3 skipped: {e}")
        print_info("This sensor is optional - system will work without it")
        return False

def test_servos():
    """Test all servo motors"""
    print_header("TEST 6: Servo Motors")
    print_info("Neck: GPIO 18 (Pin 12)")
    print_info("Arm_L: GPIO 22 (Pin 15)")
    print_info("Arm_R: GPIO 27 (Pin 13)")
    print_warning("Ensure servos are properly mounted before testing!")
    
    wait_for_user("Press Enter when ready to test servos (they will move)...")
    
    try:
        from actuators.multi_servo_controller import multi_servo_controller
        
        servos = ['neck', 'arm_l', 'arm_r']
        test_angles = [0, 90, 180, 90]
        
        for servo_name in servos:
            print_info(f"\nTesting {servo_name.upper()} servo...")
            servo = multi_servo_controller.get_servo(servo_name)
            
            if servo is None:
                print_fail(f"{servo_name} servo not initialized")
                continue
            
            for angle in test_angles:
                print_info(f"  Moving to {angle}°...")
                multi_servo_controller.set_angle(servo_name, angle)
                time.sleep(0.8)
            
            print_success(f"{servo_name} servo working!")
        
        # Center all servos
        print_info("\nCentering all servos...")
        for servo_name in servos:
            multi_servo_controller.set_angle(servo_name, 90)
        
        print_success("All servos tested successfully")
        test_results["servos"] = True
        return True
        
    except Exception as e:
        print_fail(f"Servo test failed: {e}")
        return False

def test_motors():
    """Test L298N motor controller"""
    print_header("TEST 7: L298N Motor Controller")
    print_info("Left Motor: ENA→GPIO12, IN1→GPIO5, IN2→GPIO6")
    print_info("Right Motor: ENB→GPIO13, IN3→GPIO26, IN4→GPIO16")
    print_warning("⚠️  Ensure robot has space to move!")
    print_warning("⚠️  Battery 7.4V connected to L298N VIN")
    print_warning("⚠️  L298N 5V jumper REMOVED")
    
    wait_for_user("Press Enter when ready to test motors (robot will move)...")
    
    try:
        from actuators.motor_controller import MotorController
        from core.hardware_manager import hardware_manager
        
        motors = MotorController()
        
        # Test each direction
        tests = [
            ("Forward", lambda: motors.forward(60, 1.5)),
            ("Backward", lambda: motors.backward(60, 1.5)),
            ("Turn Left", lambda: motors.left(60, 1)),
            ("Turn Right", lambda: motors.right(60, 1)),
        ]
        
        for name, test_func in tests:
            print_info(f"\nTesting: {name}...")
            time.sleep(1)
            test_func()
            motors.stop()
            time.sleep(0.5)
        
        motors.cleanup()
        hardware_manager.cleanup()
        
        print_success("Motor controller test complete")
        test_results["motors"] = True
        return True
        
    except Exception as e:
        print_fail(f"Motor test failed: {e}")
        return False

def print_summary():
    """Print test summary"""
    print_header("TEST SUMMARY")
    
    total = len(test_results)
    passed = sum(test_results.values())
    
    for test, result in test_results.items():
        if result:
            print_success(f"{test.upper()}: PASS")
        else:
            print_fail(f"{test.upper()}: FAIL")
    
    print(f"\n{Colors.BOLD}Results: {passed}/{total} tests passed{Colors.ENDC}")
    
    if passed == total:
        print_success("\n🎉 All tests passed! JARVIS hardware is ready!")
    elif passed >= total * 0.7:
        print_warning(f"\n⚠️  Most tests passed. Check failed components.")
    else:
        print_fail(f"\n❌ Multiple failures. Review wiring and connections.")
    
    # Save results to file
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("hardware_test_results.txt", "w") as f:
        f.write(f"JARVIS Hardware Test Results\n")
        f.write(f"Date: {timestamp}\n")
        f.write(f"="*60 + "\n\n")
        for test, result in test_results.items():
            status = "PASS" if result else "FAIL"
            f.write(f"{test.upper()}: {status}\n")
        f.write(f"\nTotal: {passed}/{total} passed\n")
    
    print_info(f"\nResults saved to: hardware_test_results.txt")

def main():
    print_header("🤖 JARVIS Hardware Test Suite 🤖")
    print_info(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print_info("This will test all hardware components one by one\n")
    
    print_warning("BEFORE STARTING:")
    print_info("1. All wiring completed as per COMPLETE_WIRING_GUIDE.md")
    print_info("2. Raspberry Pi powered via USB-C")
    print_info("3. Battery connected to L298N (switch OFF for now)")
    print_info("4. Voltage divider installed for Ultrasonic ECHO")
    print_info("5. L298N 5V jumper removed")
    
    wait_for_user("\nPress Enter to begin tests...")
    
    # Run tests
    test_pigpiod()
    wait_for_user()
    
    test_dht11()
    wait_for_user()
    
    test_pir()
    wait_for_user()
    
    test_ultrasonic()
    wait_for_user()
    
    test_mq3()
    wait_for_user()
    
    test_servos()
    wait_for_user()
    
    print_warning("\n⚠️  NEXT TEST REQUIRES BATTERY POWER")
    print_info("Turn ON the battery switch now")
    wait_for_user("Press Enter when battery is ON...")
    
    test_motors()
    
    # Print summary
    print_summary()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}Test interrupted by user{Colors.ENDC}")
        sys.exit(1)
    except Exception as e:
        print_fail(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
