import RPi.GPIO as GPIO
import time
import os

# Set GPIO numbering mode
GPIO.setmode(GPIO.BCM)

# Set pins for Trigger and Echo from environment variables or defaults
GPIO_TRIGGER = int(os.getenv('ULTRASONIC_TRIGGER_PIN', '27'))
GPIO_ECHO = int(os.getenv('ULTRASONIC_ECHO_PIN', '22'))

print("--- Ultrasonic Sensor Standalone Test ---")
print(f"TRIGGER Pin (BCM): {GPIO_TRIGGER}")
print(f"ECHO Pin (BCM): {GPIO_ECHO}")

# Set TRIGGER as output and ECHO as input
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)

def get_distance():
    # Send a 10us pulse to trigger the measurement
    GPIO.output(GPIO_TRIGGER, False)
    time.sleep(0.000002) # Wait for sensor to settle
    GPIO.output(GPIO_TRIGGER, True)
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)

    timeout_start = time.time()

    # Wait for the echo to start (pin goes HIGH)
    start_time = time.time()
    while GPIO.input(GPIO_ECHO) == 0:
        start_time = time.time()
        if start_time - timeout_start > 0.1:
            print("[ERROR] Timeout: Echo pulse not detected. Check wiring.")
            return -1

    # Wait for the echo to end (pin goes LOW)
    stop_time = time.time()
    while GPIO.input(GPIO_ECHO) == 1:
        stop_time = time.time()
        if stop_time - start_time > 0.1:
            print("[ERROR] Timeout: Echo pulse did not end. Check wiring.")
            return -1

    # Calculate pulse duration and convert to distance
    time_elapsed = stop_time - start_time
    # Speed of sound is approx 34300 cm/s
    # Distance = (Time x Speed of Sound) / 2 (round trip)
    distance = (time_elapsed * 34300) / 2

    return distance

if __name__ == '__main__':
    try:
        while True:
            dist = get_distance()
            if dist > 0:
                print(f"Measured Distance = {dist:.1f} cm")
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nMeasurement stopped by User.")
    finally:
        # Clean up GPIO settings
        GPIO.cleanup()
        print("GPIO cleanup complete.")