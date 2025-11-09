from core.hardware_manager import hardware_manager
import random
import time
import RPi.GPIO as GPIO

class MQ3:
    def __init__(self, digital_pin=6):
        self.digital_pin = digital_pin
        self.simulation_mode = hardware_manager.simulation_mode
        
        if not self.simulation_mode:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.digital_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
            print(f"MQ-3 Alcohol Sensor initialized on digital GPIO pin {self.digital_pin}")
        else:
            print("MQ-3 Alcohol Sensor initialized in simulation mode.")

    def read_alcohol_detected(self):
        """
        Reads the digital output pin.
        Returns True if alcohol is detected (pin is HIGH), False otherwise.
        """
        if self.simulation_mode:
            detected = random.choice([True, False])
            # print(f"Simulated alcohol detection: {'Yes' if detected else 'No'}")
            return detected

        # The D0 pin on the module goes HIGH when the threshold is exceeded.
        if GPIO.input(self.digital_pin) == GPIO.HIGH:
            return True
        else:
            return False

    def calibrate(self):
        """
        Simulates a calibration period for the sensor to warm up.
        With a digital pin, this is less about stabilizing readings and more about just letting the heater work.
        """
        print("Calibrating MQ-3 sensor (warming up)... Please wait 20 seconds.")
        if not self.simulation_mode:
            time.sleep(20)
        print("Calibration complete.")

    def close(self):
        """
        No action needed for digital GPIO reading, but method kept for consistency.
        """
        print("MQ-3 sensor resources released.")

if __name__ == '__main__':
    # This block is for direct execution and testing only.
    # It is self-contained and does not use the MQ3 class above to avoid import errors.
    import RPi.GPIO as GPIO
    import time

    # --- Standalone Test Configuration ---
    DIGITAL_PIN = 26  # The GPIO pin connected to the MQ-3's D0 output
    # -------------------------------------

    print("--- Standalone MQ-3 Digital Sensor Test ---")
    print(f"Reading from GPIO pin: {DIGITAL_PIN}")
    print("Press CTRL+C to exit.")

    try:
        # Setup GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(DIGITAL_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        print("\nSensor warming up... Please wait about 20 seconds.")
        # The sensor needs time for the heater to reach operating temperature.
        # We'll print dots to show progress.
        for i in range(20):
            print(".", end='', flush=True)
            time.sleep(1)
        print("\nWarm-up complete. Starting readings.\n")

        while True:
            # The D0 pin goes HIGH when the alcohol concentration exceeds the threshold
            # set by the onboard potentiometer.
            if GPIO.input(DIGITAL_PIN) == GPIO.HIGH:
                print("Alcohol DETECTED!")
            else:
                print("No alcohol detected.")
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nExiting test.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
    finally:
        # Clean up GPIO settings on exit
        GPIO.cleanup()
        print("GPIO cleaned up.")
