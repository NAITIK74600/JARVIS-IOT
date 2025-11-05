"""
Motor Controller for Jarvis Robot Chassis.

This module controls a 2-wheel drive chassis using a dual H-bridge motor
driver like the L298N. It provides functions for forward, backward,
left, right, and stop movements.

Assumed Pinout (BCM numbering):
- Left Motor (Motor A on L298N):
  - Enable Pin (ENA): BCM 12
  - Input 1 (IN1): BCM 5
  - Input 2 (IN2): BCM 6
- Right Motor (Motor B on L298N):
  - Enable Pin (ENB): BCM 13
  - Input 1 (IN3): BCM 26
  - Input 2 (IN4): BCM 16

These pins can be overridden with environment variables:
- MOTOR_L_EN, MOTOR_L_IN1, MOTOR_L_IN2
- MOTOR_R_EN, MOTOR_R_IN1, MOTOR_R_IN2
"""

from core.hardware_manager import hardware_manager
import RPi.GPIO as GPIO
import os
import time

class MotorController:
    def __init__(self):
        self.simulation_mode = hardware_manager.simulation_mode
        self._cleaned_up = False  # Track cleanup state

        # Get pin numbers from environment variables or use defaults
        self.L_EN = int(os.getenv('MOTOR_L_EN', 12))
        self.L_IN1 = int(os.getenv('MOTOR_L_IN1', 5))
        self.L_IN2 = int(os.getenv('MOTOR_L_IN2', 6))
        self.R_EN = int(os.getenv('MOTOR_R_EN', 13))
        self.R_IN1 = int(os.getenv('MOTOR_R_IN1', 26))
        self.R_IN2 = int(os.getenv('MOTOR_R_IN2', 16))

        if not self.simulation_mode:
            self._setup_gpio()
        else:
            print("MotorController initialized (Simulation Mode)")

    def _setup_gpio(self):
        """Sets up GPIO pins for motor control."""
        pins = [self.L_EN, self.L_IN1, self.L_IN2, self.R_EN, self.R_IN1, self.R_IN2]
        GPIO.setup(pins, GPIO.OUT)
        
        # Set up PWM for speed control
        self.l_pwm = GPIO.PWM(self.L_EN, 100) # 100 Hz frequency
        self.r_pwm = GPIO.PWM(self.R_EN, 100)
        self.l_pwm.start(0)
        self.r_pwm.start(0)
        print("MotorController GPIO initialized.")

    def _set_speed(self, left_speed, right_speed):
        """Sets the speed of the motors. Speed is a value from 0 to 100."""
        if self.simulation_mode:
            print(f"[SIM] Setting motor speed: Left={left_speed}, Right={right_speed}")
            return
        
        self.l_pwm.ChangeDutyCycle(left_speed)
        self.r_pwm.ChangeDutyCycle(right_speed)

    def forward(self, speed=80, duration=None):
        """Move the robot forward."""
        if self.simulation_mode:
            print(f"[SIM] Moving forward at speed {speed}")
        else:
            GPIO.output(self.L_IN1, GPIO.HIGH)
            GPIO.output(self.L_IN2, GPIO.LOW)
            GPIO.output(self.R_IN1, GPIO.HIGH)
            GPIO.output(self.R_IN2, GPIO.LOW)
        self._set_speed(speed, speed)
        if duration:
            time.sleep(duration)
            self.stop()

    def backward(self, speed=80, duration=None):
        """Move the robot backward."""
        if self.simulation_mode:
            print(f"[SIM] Moving backward at speed {speed}")
        else:
            GPIO.output(self.L_IN1, GPIO.LOW)
            GPIO.output(self.L_IN2, GPIO.HIGH)
            GPIO.output(self.R_IN1, GPIO.LOW)
            GPIO.output(self.R_IN2, GPIO.HIGH)
        self._set_speed(speed, speed)
        if duration:
            time.sleep(duration)
            self.stop()

    def left(self, speed=70, duration=None):
        """Turn the robot left on the spot."""
        if self.simulation_mode:
            print(f"[SIM] Turning left at speed {speed}")
        else:
            GPIO.output(self.L_IN1, GPIO.LOW)
            GPIO.output(self.L_IN2, GPIO.HIGH) # Left motor backward
            GPIO.output(self.R_IN1, GPIO.HIGH)
            GPIO.output(self.R_IN2, GPIO.LOW)  # Right motor forward
        self._set_speed(speed, speed)
        if duration:
            time.sleep(duration)
            self.stop()

    def right(self, speed=70, duration=None):
        """Turn the robot right on the spot."""
        if self.simulation_mode:
            print(f"[SIM] Turning right at speed {speed}")
        else:
            GPIO.output(self.L_IN1, GPIO.HIGH)
            GPIO.output(self.L_IN2, GPIO.LOW)  # Left motor forward
            GPIO.output(self.R_IN1, GPIO.LOW)
            GPIO.output(self.R_IN2, GPIO.HIGH) # Right motor backward
        self._set_speed(speed, speed)
        if duration:
            time.sleep(duration)
            self.stop()

    def stop(self):
        """Stop all motor movement."""
        if self.simulation_mode:
            print("[SIM] Stopping motors")
        else:
            GPIO.output(self.L_IN1, GPIO.LOW)
            GPIO.output(self.L_IN2, GPIO.LOW)
            GPIO.output(self.R_IN1, GPIO.LOW)
            GPIO.output(self.R_IN2, GPIO.LOW)
        self._set_speed(0, 0)

    def cleanup(self):
        """Clean up GPIO resources."""
        if self._cleaned_up:
            print("MotorController already cleaned up, skipping.")
            return
        
        self._cleaned_up = True
        
        if not self.simulation_mode:
            try:
                self.l_pwm.stop()
                self.r_pwm.stop()
                print("MotorController cleaned up.")
            except Exception as e:
                print(f"Error cleaning up MotorController: {e}")
            # GPIO.cleanup() is handled by HardwareManager

if __name__ == '__main__':
    # Example usage
    motors = MotorController()
    try:
        print("Moving forward for 2 seconds")
        motors.forward(speed=90, duration=2)
        
        print("Moving backward for 2 seconds")
        motors.backward(speed=90, duration=2)

        print("Turning left for 1 second")
        motors.left(duration=1)

        print("Turning right for 1 second")
        motors.right(duration=1)

        print("Test complete.")
    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        motors.cleanup()
        hardware_manager.cleanup()
