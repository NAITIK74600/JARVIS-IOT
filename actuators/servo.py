import sys
import os
import time
import threading
try:
    import pigpio
except Exception as _pigpio_err:
    pigpio = None  # Will handle later

# Add the project root to the Python path to allow for absolute imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Global shared pigpio connection to prevent multiple connections and segfaults
_shared_pigpio_instance = None
_pigpio_instance_count = 0
_pigpio_lock = threading.Lock()  # Thread safety for cleanup

def _get_shared_pigpio():
    """Get or create a shared pigpio instance."""
    global _shared_pigpio_instance, _pigpio_instance_count
    with _pigpio_lock:
        if pigpio is None:
            return None
        if _shared_pigpio_instance is None:
            try:
                _shared_pigpio_instance = pigpio.pi()
                if not _shared_pigpio_instance.connected:
                    print("[SERVO] Could not connect to pigpio daemon.")
                    _shared_pigpio_instance = None
                    return None
            except Exception as e:
                print(f"[SERVO] pigpio initialization failed: {e}")
                _shared_pigpio_instance = None
                return None
        _pigpio_instance_count += 1
        return _shared_pigpio_instance

def _release_shared_pigpio():
    """Release the shared pigpio instance when no longer needed."""
    global _shared_pigpio_instance, _pigpio_instance_count
    with _pigpio_lock:
        _pigpio_instance_count -= 1
        if _pigpio_instance_count <= 0 and _shared_pigpio_instance is not None:
            try:
                _shared_pigpio_instance.stop()
                print("[SERVO] Shared pigpio connection closed.")
            except Exception as e:
                print(f"[SERVO] Error closing pigpio: {e}")
            finally:
                _shared_pigpio_instance = None
                _pigpio_instance_count = 0

class Servo:
    def __init__(self, pin, min_pulse=500, max_pulse=2400, angle_offset=0, min_angle=0, max_angle=180, reverse=False, verbose=None):
        """High level servo abstraction using pigpio.

        Many hobby servos respond safely in roughly the 500–2400µs pulse width
        range. If your servo binds or buzzes at the extremes, reduce the range
        (e.g. 600–2300). You can experiment with `set_pulse_width` directly.
        
        Args:
            pin: GPIO pin number (BCM mode)
            min_pulse: Minimum pulse width in microseconds
            max_pulse: Maximum pulse width in microseconds
            angle_offset: Angle offset to apply (e.g., -90 makes 90° physical = 0° logical)
            min_angle: Minimum safe angle (software limit)
            max_angle: Maximum safe angle (software limit)
            reverse: Reverse direction (180° becomes 0°, 0° becomes 180°)
            verbose: Enable verbose logging
        """
        self.pin = pin
        self.min_pulse = min_pulse
        self.max_pulse = max_pulse
        self.angle_offset = angle_offset  # Angle offset for logical remapping
        self.min_angle = min_angle  # Safe minimum angle
        self.max_angle = max_angle  # Safe maximum angle
        self.reverse = reverse  # Reverse direction flag
        self.current_angle = None
        self._cleaned_up = False  # Track cleanup state
        # Verbosity control
        if verbose is None:
            verbose = os.getenv("SERVO_VERBOSE", "0") == "1"
        self.verbose = verbose

        # Use shared pigpio instance instead of creating a new one
        self.pi = _get_shared_pigpio()
        
        # Basic platform hint (only warn if clearly not a Pi)
        if self.verbose:
            print(f"[SERVO] Initializing on platform: {os.uname().machine}")
        
        if self.pi is None:
            print("FATAL: pigpio library not available or daemon not running.")
            print("Install with 'pip install pigpio' and ensure daemon: sudo systemctl enable --now pigpiod")
        else:
            if self.verbose:
                print(f"[SERVO] Connected to pigpio daemon. HW revision: {self.pi.get_hardware_revision():X}")
            print(f"Servo on pin {self.pin} initialized with pigpio (range {self.min_pulse}-{self.max_pulse}µs).")

    def set_angle(self, angle):
        """
        Set servo to logical angle with safety limits.
        The angle_offset is applied to convert logical to physical angle.
        Angle is clamped to min_angle and max_angle for safety.
        If reverse is True, the direction is inverted.
        
        Args:
            angle: Logical angle
        """
        if self.pi is None:
            print("[WARN] pigpio not connected. Angle ignored. (Did pigpiod start?)")
            return
        
        # Apply software safety limits
        if angle < self.min_angle or angle > self.max_angle:
            print(f"[WARN] Angle {angle}° out of safe range ({self.min_angle}°–{self.max_angle}°). Clamping.")
            angle = max(self.min_angle, min(self.max_angle, angle))
        
        # Apply reverse if enabled (invert direction)
        if self.reverse:
            angle = 180 - angle
        
        # Apply angle offset to convert logical to physical angle
        physical_angle = angle + self.angle_offset
        
        # Validate physical angle is in valid range
        if physical_angle < 0 or physical_angle > 180:
            print(f"[WARN] Physical angle {physical_angle}° out of bounds (0–180). Logical={angle}°, offset={self.angle_offset}°. Clamping.")
            physical_angle = max(0, min(180, physical_angle))
        
        pulse_width = self.min_pulse + (physical_angle / 180.0) * (self.max_pulse - self.min_pulse)
        try:
            self.pi.set_servo_pulsewidth(self.pin, pulse_width)
            if self.verbose:
                print(f"[SERVO] logical {angle}° (physical {physical_angle}°) => {int(pulse_width)}µs")
        except Exception as e:
            print(f"[ERROR] Failed to set angle {angle}: {e}")
        self.current_angle = angle  # Store logical angle

    def set_pulse_width(self, microseconds):
        """Direct low‑level pulse control (microseconds). Use for calibration."""
        if self.pi is None:
            return
        self.pi.set_servo_pulsewidth(self.pin, microseconds)

    def center(self):
        """Move servo to mid position (approx 90° logical, considering offset)."""
        self.set_angle(90)

    def sweep(self, delay=0.6, step=30):
        """Sweep through the range for a basic functional test."""
        for a in range(0, 181, step):
            print(f"Angle -> {a}")
            self.set_angle(a)
            time.sleep(delay)
        for a in range(180, -1, step):
            print(f"Angle -> {a}")
            self.set_angle(a)
            time.sleep(delay)

    def detach(self):
        """Stop pulses (servo will relax)."""
        if self.pi:
            try:
                self.pi.set_servo_pulsewidth(self.pin, 0)
            except Exception:
                pass

    def cleanup(self):
        """
        Cleans up the servo and releases the shared pigpio connection.
        """
        if self._cleaned_up:
            if self.verbose:
                print(f"[SERVO] Servo on pin {self.pin} already cleaned up, skipping.")
            return
        
        self._cleaned_up = True
        
        if self.pi:
            try:
                self.detach()  # Detach before cleanup
                if self.verbose:
                    print(f"[SERVO] Servo on pin {self.pin} detached.")
            except Exception as e:
                print(f"[SERVO] Error detaching servo on pin {self.pin}: {e}")
            finally:
                # Release the shared pigpio instance
                _release_shared_pigpio()
                print(f"Servo on pin {self.pin} cleaned up.")

def test_servo():
    servo_pin = 12
    servo = Servo(servo_pin)
    if not servo.pi:
        return
    try:
        print("Centered (90°)")
        servo.center()
        time.sleep(1.2)
        print("Sweeping...")
        servo.sweep(step=45, delay=0.7)
        print("Raw pulse min -> max -> mid")
        for pw in (servo.min_pulse, servo.max_pulse, (servo.min_pulse + servo.max_pulse)//2):
            print(f"Pulse {pw}µs")
            servo.set_pulse_width(pw)
            time.sleep(1)
        print("Detach (servo should relax)")
        servo.detach()
        time.sleep(1)
        print("Re-center")
        servo.center()
        time.sleep(1)
    except KeyboardInterrupt:
        print("Interrupted.")
    finally:
        servo.cleanup()

if __name__ == "__main__":
    test_servo()


