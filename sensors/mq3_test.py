#!/usr/bin/env python3
"""
Standalone MQ-3 Alcohol Sensor Test Script
Tests the digital output (D0) of the MQ-3 sensor module.
"""
import RPi.GPIO as GPIO
import time

# --- Configuration ---
DIGITAL_PIN = 26  # The GPIO pin connected to the MQ-3's D0 output
# ---------------------

def main():
    print("=" * 50)
    print("MQ-3 Alcohol Sensor Test (Digital D0 Mode)")
    print("=" * 50)
    print(f"Reading from GPIO pin: BCM {DIGITAL_PIN} (Physical Pin 37)")
    print("Press CTRL+C to exit.\n")

    try:
        # Setup GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(DIGITAL_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        print("✓ GPIO initialized successfully")

        print("\n🔥 Sensor warming up... Please wait about 20 seconds.")
        print("(The MQ-3 heater needs to reach operating temperature)")
        
        # Show progress during warm-up
        for i in range(20):
            print(".", end='', flush=True)
            time.sleep(1)
        
        print("\n✓ Warm-up complete. Starting readings...\n")

        # Continuous reading loop
        while True:
            # The D0 pin goes HIGH when the alcohol concentration exceeds 
            # the threshold set by the onboard potentiometer.
            pin_state = GPIO.input(DIGITAL_PIN)
            
            if pin_state == GPIO.HIGH:
                print("🚨 Alcohol DETECTED! (D0 = HIGH)")
            else:
                print("✓ No alcohol detected. (D0 = LOW)")
            
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n\n⚠ Test interrupted by user.")
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
    finally:
        # Clean up GPIO settings on exit
        GPIO.cleanup()
        print("✓ GPIO cleaned up. Test complete.")

if __name__ == '__main__':
    main()
