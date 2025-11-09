from core.hardware_manager import hardware_manager
import RPi.GPIO as GPIO
import time
import random
import os

class Ultrasonic:
    def __init__(self, trigger_pin, echo_pin):
        self.trigger_pin = trigger_pin
        self.echo_pin = echo_pin
        self.simulation_mode = hardware_manager.simulation_mode

        if not self.simulation_mode:
            # Configure pins. Use an internal pull-down on ECHO to avoid floating reads
            GPIO.setup(self.trigger_pin, GPIO.OUT)
            # Ensure trigger is low initially
            GPIO.output(self.trigger_pin, False)
            # ECHO should be input with pull-down to avoid spurious HIGH
            try:
                GPIO.setup(self.echo_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
            except TypeError:
                # Some older RPi.GPIO versions may not accept pull_up_down here
                GPIO.setup(self.echo_pin, GPIO.IN)

            print(f"Ultrasonic Sensor initialized with TRIGGER={self.trigger_pin} and ECHO={self.echo_pin}")
        else:
            print(f"Ultrasonic Sensor initialized (Simulation Mode)")

    def measure_distance(self):
        """
        Measures the distance using the ultrasonic sensor.
        Returns the distance in centimeters.
        """
        if self.simulation_mode:
            # Simulate a distance reading
            return random.uniform(5, 200)

        # Ensure trigger is low for a moment, then send a 10us pulse
        GPIO.output(self.trigger_pin, False)
        time.sleep(0.000005)
        GPIO.output(self.trigger_pin, True)
        time.sleep(0.00001)
        GPIO.output(self.trigger_pin, False)

        # Use a timeout to avoid getting stuck
        timeout_start = time.time()
        
        # Wait for the echo to go high (with timeout)
        start_time = time.time()
        while GPIO.input(self.echo_pin) == 0:
            start_time = time.time()
            if start_time - timeout_start > 0.1:  # 100ms timeout
                # This is the most common failure point
                print("[ULTRASONIC] Timeout: Echo pin never went HIGH. Check wiring.")
                return -1

        # Wait for the echo to go low (with timeout)
        stop_time = time.time()
        while GPIO.input(self.echo_pin) == 1:
            stop_time = time.time()
            if stop_time - start_time > 0.1: # 100ms timeout
                print("[ULTRASONIC] Timeout: Echo pin never went LOW. Check wiring.")
                return -1

        time_elapsed = stop_time - start_time
        # Speed of sound is approx 34300 cm/s
        # Distance = (Time x Speed of Sound) / 2 (because it's a round trip)
        distance = (time_elapsed * 34300) / 2

        # Add a sanity check for the reading
        if distance > 400 or distance < 2:
            return -2 # Out of range
            
        return distance

if __name__ == '__main__':
    # This block allows testing this file directly
    # It is not used when imported by SensorManager
    print("--- Ultrasonic Sensor Direct Test ---")
    # NOTE: This test uses BCM pins 23/24 by default.
    # The main app uses 27/22. We will use the main app's pins for this test.
    trigger = int(os.getenv('ULTRASONIC_TRIGGER_PIN', '27'))
    echo = int(os.getenv('ULTRASONIC_ECHO_PIN', '22'))
    
    ultrasonic_sensor = Ultrasonic(trigger_pin=trigger, echo_pin=echo)
    
    print(f"Testing with TRIGGER={trigger}, ECHO={echo}. Press Ctrl+C to exit.")
    
    try:
        while True:
            dist = ultrasonic_sensor.measure_distance()
            if dist == -1:
                # Timeout error already printed
                pass
            elif dist == -2:
                print("Measurement out of range.")
            else:
                print(f"Measured Distance = {dist:.1f} cm")
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nMeasurement stopped by User.")
    finally:
        GPIO.cleanup()
        print("GPIO cleanup complete.")
