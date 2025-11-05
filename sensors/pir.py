from core.hardware_manager import hardware_manager
import RPi.GPIO as GPIO
import time
import threading
import random

class PIR:
    def __init__(self, pin, on_motion_callback=None):
        self.pin = pin
        self.on_motion_callback = on_motion_callback
        self.last_motion_time = None
        self._running = False
        self._monitor_thread = None
        self.simulation_mode = hardware_manager.simulation_mode

        if not self.simulation_mode:
            GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
            print(f"PIR Motion Sensor initialized on pin {self.pin}")
        else:
            print(f"PIR Motion Sensor initialized on pin {self.pin} (Simulation Mode)")

    def _monitor(self):
        """
        Private method to monitor the sensor in a separate thread.
        """
        print("PIR monitoring started.")
        fallback_poll = False
        while self._running:
            if self.simulation_mode:
                time.sleep(random.randint(10, 20))
                motion_detected = True
            else:
                motion_detected = False
                if not fallback_poll:
                    try:
                        GPIO.wait_for_edge(self.pin, GPIO.RISING, timeout=5000)  # 5s timeout for responsive shutdown
                        # If wait_for_edge returns, it means an edge was detected or timeout occurred.
                        # We still check the pin state to be sure.
                        if GPIO.input(self.pin) == GPIO.HIGH:
                            motion_detected = True
                    except RuntimeError as e:
                        print(f"[PIR] wait_for_edge runtime error: {e}. Switching to polling mode.")
                        fallback_poll = True
                if fallback_poll:
                    # Polling fallback: sample pin every 100ms
                    if GPIO.input(self.pin) == GPIO.HIGH:
                        motion_detected = True
                    else:
                        time.sleep(0.1)

            if motion_detected:
                self.last_motion_time = time.time()
                print(f"Motion detected at {time.ctime()}!")
                if self.on_motion_callback:
                    try:
                        # Run callback in a separate thread to avoid blocking the monitor loop
                        threading.Thread(target=self.on_motion_callback, daemon=True).start()
                    except Exception as e:
                        print(f"Error in on_motion_callback: {e}")
            
            # In hardware mode, wait_for_edge handles the waiting.
            # In simulation, we add a small delay to prevent a tight loop if we change the logic.
            if self.simulation_mode:
                time.sleep(1)

        print("PIR monitoring stopped.")

    def start_monitoring(self):
        """
        Starts monitoring for motion in a background thread.
        """
        if not self._running:
            self._running = True
            self._monitor_thread = threading.Thread(target=self._monitor, daemon=True)
            self._monitor_thread.start()

    def stop_monitoring(self):
        """
        Stops the motion monitoring thread.
        """
        if self._running:
            self._running = False
            print("PIR monitoring stop signal sent.")
        thread = self._monitor_thread
        if thread and thread.is_alive():
            thread.join(timeout=2.0)
            if thread.is_alive():
                print("Warning: PIR monitoring thread did not terminate within timeout.")
        self._monitor_thread = None

    def close(self):
        self.stop_monitoring()

if __name__ == '__main__':
    import random
    # Example usage
    def motion_alert():
        print(f"CALLBACK TRIGGERED: Motion has been detected in the area at {time.ctime()}!")

    pir_sensor = PIR(pin=17, on_motion_callback=motion_alert)
    pir_sensor.start_monitoring()

    try:
        print("Monitoring for motion... (Press Ctrl+C to exit)")
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nExiting.")
    finally:
        pir_sensor.stop_monitoring()
        # HardwareManager will handle GPIO.cleanup()
