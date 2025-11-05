from core.hardware_manager import hardware_manager
import RPi.GPIO as GPIO
import time
import random

class Ultrasonic:
    def __init__(self, trigger_pin, echo_pin):
        self.trigger_pin = trigger_pin
        self.echo_pin = echo_pin
        self.simulation_mode = hardware_manager.simulation_mode

        if not self.simulation_mode:
            GPIO.setup(self.trigger_pin, GPIO.OUT)
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

        # Send a 10us pulse to trigger
        GPIO.output(self.trigger_pin, True)
        time.sleep(0.00001)
        GPIO.output(self.trigger_pin, False)

        start_time = time.time()
        stop_time = time.time()

        # Save start time
        timeout = time.time() + 1 # 1s timeout
        while GPIO.input(self.echo_pin) == 0:
            start_time = time.time()
            if start_time > timeout:
                print("Ultrasonic sensor timeout waiting for echo start.")
                return -1 # Indicate an error

        # Save time of arrival
        timeout = time.time() + 0.1 # 100ms timeout
        while GPIO.input(self.echo_pin) == 1:
            stop_time = time.time()
            if stop_time > timeout:
                print("Ultrasonic sensor timeout waiting for echo end.")
                return -1 # Indicate an error

        time_elapsed = stop_time - start_time
        # Speed of sound is approx 34300 cm/s
        # Distance = (Time x Speed of Sound) / 2 (because the sound travels there and back)
        distance = (time_elapsed * 34300) / 2

        return distance

if __name__ == '__main__':
    # Example usage
    ultrasonic_sensor = Ultrasonic(trigger_pin=23, echo_pin=24)
    try:
        while True:
            dist = ultrasonic_sensor.measure_distance()
            if dist != -1:
                print(f"Measured Distance = {dist:.1f} cm")
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nExiting...")
    # HardwareManager handles GPIO cleanup
