"""
Multi-Servo Controller for Jarvis Robot.

This module manages multiple servo motors, such as those for the neck,
arms, or other articulated parts. It uses the pigpio library for precise
pulse-width modulation (PWM) control.

Each servo is identified by a name (e.g., 'neck', 'arm_l', 'arm_r') and
is an instance of the single Servo class.

Default Pinout (BCM numbering):
- Neck Servo: BCM 18 (head rotation)
- Left Hand Servo: BCM 25
- Right Hand Servo: BCM 23

These can be overridden with environment variables:
- SERVO_PIN_NECK
- SERVO_PIN_ARM_L (left hand)
- SERVO_PIN_ARM_R (right hand)
"""

from __future__ import annotations

from actuators.servo import Servo
import os
import threading

class MultiServoController:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(MultiServoController, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        # Prevent re-initialization
        if hasattr(self, 'initialized') and self.initialized:
            return
            
        self.servos = {}
        self.servo_locks = {}
        self._cleaned_up = False  # Track cleanup state to prevent double cleanup
        
        # --- Define servo configurations ---
        # Note: neck servo has +90 offset so 0° logical = 90° physical (front-facing)
        servo_configs = {
            'neck': {
                'pin': int(os.getenv('SERVO_PIN_NECK', 18)),
                'min_pulse': int(os.getenv('SERVO_MIN_PULSE_NECK', 500)),
                'max_pulse': int(os.getenv('SERVO_MAX_PULSE_NECK', 2400)),
                'angle_offset': int(os.getenv('SERVO_OFFSET_NECK', 0)),
                'min_angle': int(os.getenv('SERVO_MIN_ANGLE_NECK', 0)),
                'max_angle': int(os.getenv('SERVO_MAX_ANGLE_NECK', 180)),
                'reverse': os.getenv('SERVO_REVERSE_NECK', 'false').lower() in ('true', '1', 'yes'),
            },
            'arm_l': {
                'pin': int(os.getenv('SERVO_PIN_ARM_L', 25)),
                'min_pulse': int(os.getenv('SERVO_MIN_PULSE_ARM_L', 500)),
                'max_pulse': int(os.getenv('SERVO_MAX_PULSE_ARM_L', 2400)),
                'angle_offset': int(os.getenv('SERVO_OFFSET_ARM_L', 0)),
                'min_angle': int(os.getenv('SERVO_MIN_ANGLE_ARM_L', 70)),
                'max_angle': int(os.getenv('SERVO_MAX_ANGLE_ARM_L', 160)),
            },
            'arm_r': {
                'pin': int(os.getenv('SERVO_PIN_ARM_R', 23)),
                'min_pulse': int(os.getenv('SERVO_MIN_PULSE_ARM_R', 500)),
                'max_pulse': int(os.getenv('SERVO_MAX_PULSE_ARM_R', 2400)),
                'angle_offset': int(os.getenv('SERVO_OFFSET_ARM_R', 0)),
                'min_angle': int(os.getenv('SERVO_MIN_ANGLE_ARM_R', 65)),
                'max_angle': int(os.getenv('SERVO_MAX_ANGLE_ARM_R', 160)),
            },
        }

        for name, config in servo_configs.items():
            try:
                servo = Servo(
                    pin=config['pin'], 
                    min_pulse=config['min_pulse'], 
                    max_pulse=config['max_pulse'],
                    angle_offset=config.get('angle_offset', 0),
                    min_angle=config.get('min_angle', 0),
                    max_angle=config.get('max_angle', 180),
                    reverse=config.get('reverse', False)
                )
                # Only add the servo if pigpio was successfully initialized
                if servo.pi is None:
                    raise RuntimeError("pigpio not available or daemon not running.")
                
                self.servos[name] = servo
                self.servo_locks[name] = threading.Lock()
                offset_info = f" (offset: {config.get('angle_offset', 0)}°)" if config.get('angle_offset', 0) != 0 else ""
                reverse_info = " [REVERSED]" if config.get('reverse', False) else ""
                limit_info = f" [safe: {config.get('min_angle', 0)}°-{config.get('max_angle', 180)}°]"
                print(f"Initialized servo '{name}' on BCM pin {config['pin']}{offset_info}{reverse_info}{limit_info}")
            except Exception as e:
                print(f"Warning: Could not initialize servo '{name}' on pin {config['pin']}: {e}")
        
        self.initialized = True

    def get_servo(self, name: str) -> Servo | None:
        """Returns the Servo instance for the given name."""
        return self.servos.get(name)

    def get_lock(self, name: str) -> threading.Lock | None:
        """Returns the lock for the given servo name."""
        return self.servo_locks.get(name)

    def set_angle(self, name: str, angle: int):
        """Sets the angle of a specific servo."""
        servo = self.get_servo(name)
        if not servo:
            raise ValueError(f"Servo '{name}' not found.")
        
        lock = self.get_lock(name)
        if not lock.acquire(blocking=False):
            raise RuntimeError(f"Servo '{name}' is busy.")
        
        try:
            servo.set_angle(angle)
        finally:
            lock.release()

    def center(self, name: str):
        """Centers a specific servo."""
        self.set_angle(name, 90)

    def cleanup(self):
        """Cleans up all servo resources."""
        if self._cleaned_up:
            print("[MultiServoController] Already cleaned up, skipping.")
            return
        
        self._cleaned_up = True
        for name, servo in self.servos.items():
            try:
                servo.cleanup()
                print(f"Cleaned up servo '{name}'.")
            except Exception as e:
                print(f"Error cleaning up servo '{name}': {e}")

# Create a singleton instance for the application to use
multi_servo_controller = MultiServoController()
