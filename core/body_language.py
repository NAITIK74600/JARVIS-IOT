"""
Body Language and Gesture Engine for Jarvis.

This module defines and executes pre-programmed sequences of servo movements
to create lifelike gestures. It uses the MultiServoController to orchestrate
the neck, left arm, and right arm servos.

Each gesture is a sequence of (servo_name, angle, delay_after_move) tuples.
"""

from actuators.multi_servo_controller import multi_servo_controller
import time
import threading

class BodyLanguage:
    def __init__(self, controller=None):
        self.controller = controller or multi_servo_controller
        self.is_gesturing = False
        self.gesture_lock = threading.Lock()

        # --- Gesture Definitions ---
        # Each gesture is a list of tuples: (servo_name, angle, delay_ms)
        self.gestures = {
            "nod": [
                ("neck", 70, 300),
                ("neck", 110, 300),
                ("neck", 90, 200),
            ],
            "shake_head": [
                ("neck", 60, 350),
                ("neck", 120, 350),
                ("neck", 60, 350),
                ("neck", 120, 350),
                ("neck", 90, 200),
            ],
            "wave_right": [
                ("arm_r", 45, 200),
                ("arm_r", 0, 400),
                ("arm_r", 45, 400),
                ("arm_r", 0, 400),
                ("arm_r", 45, 400),
                ("arm_r", 90, 200), # Return to rest
            ],
            "wave_left": [
                ("arm_l", 135, 200),
                ("arm_l", 180, 400),
                ("arm_l", 135, 400),
                ("arm_l", 180, 400),
                ("arm_l", 135, 400),
                ("arm_l", 90, 200), # Return to rest
            ],
            "agree": [
                # A more enthusiastic nod
                ("neck", 80, 200),
                ("neck", 100, 200),
                ("neck", 80, 200),
                ("neck", 100, 200),
                ("neck", 90, 100),
            ],
            "disagree": [
                # A shorter, faster head shake
                ("neck", 75, 250),
                ("neck", 105, 250),
                ("neck", 75, 250),
                ("neck", 90, 100),
            ],
            "think": [
                ("neck", 80, 500),
                ("neck", 100, 1000),
                ("neck", 90, 200),
            ],
            "reset_position": [
                ("neck", 90, 300),
                ("arm_l", 90, 300),
                ("arm_r", 90, 300),
            ]
        }

    def list_gestures(self):
        """Returns a list of all available gesture names."""
        return list(self.gestures.keys())

    def perform_gesture(self, gesture_name: str, blocking=False):
        """
        Performs a named gesture.

        Args:
            gesture_name (str): The name of the gesture to perform.
            blocking (bool): If True, this call will wait for the gesture to finish.
                             If False, it runs in a background thread.
        """
        if gesture_name not in self.gestures:
            raise ValueError(f"Gesture '{gesture_name}' not found.")

        if self.is_gesturing:
            print(f"Cannot perform '{gesture_name}': another gesture is in progress.")
            return

        if blocking:
            self._execute_sequence(gesture_name)
        else:
            thread = threading.Thread(target=self._execute_sequence, args=(gesture_name,), daemon=True)
            thread.start()

    def _execute_sequence(self, gesture_name: str):
        """The core logic for executing a gesture sequence."""
        with self.gesture_lock:
            self.is_gesturing = True
            
        sequence = self.gestures[gesture_name]
        print(f"Performing gesture: {gesture_name}")

        try:
            for servo_name, angle, delay_ms in sequence:
                try:
                    self.controller.set_angle(servo_name, angle)
                    time.sleep(delay_ms / 1000.0)
                except ValueError as e:
                    print(f"Skipping step in '{gesture_name}': {e}")
                except RuntimeError as e:
                    print(f"Skipping step in '{gesture_name}' due to busy servo: {e}")
                    # If a servo is busy, we just skip the step and continue the gesture
                    time.sleep(delay_ms / 1000.0)
        finally:
            with self.gesture_lock:
                self.is_gesturing = False
            print(f"Finished gesture: {gesture_name}")

    def center_all(self):
        """Centers all known servos to 90 degrees."""
        for servo_name in ("neck", "arm_l", "arm_r"):
            try:
                self.controller.set_angle(servo_name, 90)
            except Exception as exc:  # pragma: no cover - hardware dependent
                print(f"Failed to center {servo_name}: {exc}")


# Singleton instance
body_language_engine = BodyLanguage()

if __name__ == '__main__':
    print("Running Body Language Engine test...")
    print("Available gestures:", body_language_engine.list_gestures())
    
    try:
        print("\nPerforming 'nod' (blocking)...")
        body_language_engine.perform_gesture("nod", blocking=True)
        
        print("\nPerforming 'shake_head' (non-blocking)...")
        body_language_engine.perform_gesture("shake_head")
        time.sleep(3) # Give it time to finish

        print("\nPerforming 'wave_right'...")
        body_language_engine.perform_gesture("wave_right")
        time.sleep(4)

        print("\nResetting position...")
        body_language_engine.perform_gesture("reset_position", blocking=True)

        print("\nTest complete.")

    except KeyboardInterrupt:
        print("\nTest interrupted.")
    finally:
        # In a real app, cleanup is handled by the main HardwareManager
        print("Test finished.")
