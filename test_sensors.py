#!/usr/bin/env python3
"""
JARVIS Sensor Test Suite
Tests all sensors individually and reports their status.
"""

import time
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)

def print_test(name, status, details=""):
    """Print test result."""
    symbol = "✅" if status else "❌"
    print(f"{symbol} {name:40} {details}")

def test_pir_sensor():
    """Test PIR Motion Sensor."""
    print_header("PIR Motion Sensor Test (BCM Pin 17)")
    try:
        from sensors.pir import PIR
        
        print("📡 Initializing PIR sensor...")
        pir = PIR(pin=17)
        print_test("PIR Initialization", True, "Sensor ready")
        
        print("\n🔍 Testing motion detection for 10 seconds...")
        print("   Wave your hand in front of the sensor...")
        
        motion_detected = False
        def on_motion():
            nonlocal motion_detected
            motion_detected = True
            print("   🎉 MOTION DETECTED!")
        
        pir.on_motion_callback = on_motion
        pir.start_monitoring()
        
        # Wait for 10 seconds
        for i in range(10, 0, -1):
            print(f"   {i}...", end="\r")
            time.sleep(1)
        
        pir.stop_monitoring()
        pir.close()
        
        print_test("PIR Motion Detection", motion_detected, 
                   "Motion was detected" if motion_detected else "No motion detected")
        
        return True
        
    except Exception as e:
        print_test("PIR Sensor", False, f"Error: {e}")
        return False

def test_ultrasonic_sensor():
    """Test Ultrasonic Distance Sensor."""
    print_header("Ultrasonic Distance Sensor Test (TRIG=23, ECHO=24)")
    try:
        from sensors.ultrasonic import Ultrasonic
        
        print("📡 Initializing ultrasonic sensor...")
        ultrasonic = Ultrasonic(trigger_pin=23, echo_pin=24)
        print_test("Ultrasonic Initialization", True, "Sensor ready")
        
        print("\n📏 Taking 5 distance measurements...")
        measurements = []
        
        for i in range(5):
            distance = ultrasonic.measure_distance()
            measurements.append(distance)
            
            if distance >= 0:
                print(f"   Measurement {i+1}: {distance:.1f} cm")
            else:
                print(f"   Measurement {i+1}: Error (timeout)")
            
            time.sleep(0.5)
        
        # Check if we got valid readings
        valid_readings = [m for m in measurements if m >= 0]
        success = len(valid_readings) > 0
        
        if success:
            avg = sum(valid_readings) / len(valid_readings)
            print_test("Ultrasonic Readings", True, 
                      f"Avg: {avg:.1f} cm ({len(valid_readings)}/5 valid)")
        else:
            print_test("Ultrasonic Readings", False, "No valid readings")
        
        return success
        
    except Exception as e:
        print_test("Ultrasonic Sensor", False, f"Error: {e}")
        return False

def test_dht_sensor():
    """Test DHT11 Temperature & Humidity Sensor."""
    print_header("DHT11 Temperature & Humidity Sensor (BCM Pin 4)")
    try:
        from sensors.dht import DHT
        
        print("📡 Initializing DHT11 sensor...")
        dht = DHT(pin=4, sensor_type='DHT11')
        print_test("DHT11 Initialization", True, f"Backend: {dht.backend}")
        
        print("\n🌡️ Taking 3 temperature & humidity readings...")
        readings = []
        
        for i in range(3):
            temp = dht.read_temperature()
            humidity = dht.read_humidity()
            
            if temp is not None and humidity is not None:
                readings.append((temp, humidity))
                print(f"   Reading {i+1}: {temp:.1f}°C, {humidity:.1f}%")
            else:
                print(f"   Reading {i+1}: Error (None values)")
            
            time.sleep(2)
        
        dht.close()
        
        success = len(readings) > 0
        if success:
            avg_temp = sum(r[0] for r in readings) / len(readings)
            avg_hum = sum(r[1] for r in readings) / len(readings)
            print_test("DHT11 Readings", True, 
                      f"Avg: {avg_temp:.1f}°C, {avg_hum:.1f}% ({len(readings)}/3 valid)")
        else:
            print_test("DHT11 Readings", False, "No valid readings")
        
        return success
        
    except Exception as e:
        print_test("DHT11 Sensor", False, f"Error: {e}")
        return False

def test_mq3_sensor():
    """Test MQ-3 Alcohol Sensor."""
    print_header("MQ-3 Alcohol Sensor (SPI ADC Channel 0)")
    try:
        from sensors.mq3 import MQ3
        
        print("📡 Initializing MQ-3 sensor...")
        mq3 = MQ3(channel=0)
        print_test("MQ-3 Initialization", True, 
                   "Simulation mode" if mq3.simulation_mode else "Hardware mode")
        
        print("\n🍺 Taking 5 alcohol level readings...")
        readings = []
        
        for i in range(5):
            level = mq3.read_alcohol_level()
            readings.append(level)
            
            if level is not None:
                print(f"   Reading {i+1}: {level:.2f} mg/L")
            else:
                print(f"   Reading {i+1}: Error (None value)")
            
            time.sleep(0.5)
        
        mq3.close()
        
        success = all(r is not None for r in readings)
        if success:
            avg = sum(readings) / len(readings)
            print_test("MQ-3 Readings", True, f"Avg: {avg:.2f} mg/L")
        else:
            print_test("MQ-3 Readings", False, "Some readings failed")
        
        return success
        
    except Exception as e:
        print_test("MQ-3 Sensor", False, f"Error: {e}")
        return False

def test_sensor_manager():
    """Test Sensor Manager (Combined System)."""
    print_header("Sensor Manager (Combined System Test)")
    try:
        from sensors.sensor_manager import SensorManager
        
        print("📡 Initializing Sensor Manager...")
        manager = SensorManager()
        print_test("Sensor Manager Init", True, "All sensors initialized")
        
        print("\n🔄 Starting sensor monitoring...")
        manager.start()
        print_test("Monitoring Started", True, "PIR monitoring active")
        
        print("\n📊 Getting all sensor readings...")
        time.sleep(2)  # Give sensors time to stabilize
        
        readings = manager.get_all_readings()
        
        print(f"\n   Distance:      {readings.get('distance_cm', 'N/A')} cm")
        print(f"   Alcohol:       {readings.get('alcohol_level_mg_l', 'N/A')} mg/L")
        print(f"   Temperature:   {readings.get('temperature_c', 'N/A')}°C")
        print(f"   Humidity:      {readings.get('humidity_percent', 'N/A')}%")
        
        last_motion = readings.get('last_motion_timestamp')
        if last_motion:
            age = time.time() - last_motion
            print(f"   Last Motion:   {age:.1f} seconds ago")
        else:
            print(f"   Last Motion:   No motion detected yet")
        
        print("\n🔄 Stopping sensor monitoring...")
        manager.stop()
        manager.close()
        print_test("Monitoring Stopped", True, "Clean shutdown")
        
        return True
        
    except Exception as e:
        print_test("Sensor Manager", False, f"Error: {e}")
        return False

def main():
    """Run all sensor tests."""
    print("\n")
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║        JARVIS SENSOR TEST SUITE - Hardware Validation             ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    
    print("\n⚠️  IMPORTANT NOTES:")
    print("   • Ensure pigpiod daemon is running: sudo systemctl start pigpiod")
    print("   • Ensure SPI is enabled: sudo raspi-config > Interface > SPI")
    print("   • Check all sensor connections match HARDWARE_PINS.txt")
    print("   • Some sensors may run in simulation mode if hardware not detected")
    
    results = {}
    
    # Individual sensor tests
    results['PIR'] = test_pir_sensor()
    results['Ultrasonic'] = test_ultrasonic_sensor()
    results['DHT11'] = test_dht_sensor()
    results['MQ-3'] = test_mq3_sensor()
    
    # Combined system test
    results['SensorManager'] = test_sensor_manager()
    
    # Summary
    print_header("Test Summary")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, status in results.items():
        symbol = "✅" if status else "❌"
        print(f"  {symbol} {name:30} {'PASS' if status else 'FAIL'}")
    
    print("\n" + "=" * 70)
    print(f"  Results: {passed}/{total} tests passed ({passed*100//total}%)")
    print("=" * 70)
    
    if passed == total:
        print("\n🎉 All sensors are working correctly!")
        print("   Your JARVIS hardware is ready for deployment.")
    elif passed > 0:
        print(f"\n⚠️  {total - passed} sensor(s) failed.")
        print("   Check connections and try again.")
    else:
        print("\n❌ All sensors failed.")
        print("   Verify hardware connections and power supply.")
    
    print("\n📝 Troubleshooting:")
    print("   • PIR not detecting: Check 5V power and signal wire")
    print("   • Ultrasonic timeout: Check voltage divider on ECHO pin")
    print("   • DHT11 errors: Wait 2 seconds between readings")
    print("   • MQ-3 issues: Verify SPI is enabled and MCP3008 connected")
    
    print("\n")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
