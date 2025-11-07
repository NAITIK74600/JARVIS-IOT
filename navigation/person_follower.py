"""
Follow Me Module for JARVIS
Makes the robot follow a person using sensors (PIR, Ultrasonic, IR).
Combines sensor data with motor control for autonomous following.
"""

import time
import threading
from typing import Optional
import random


class PersonFollower:
    def __init__(self, motor_controller=None, sensor_manager=None, servo_controller=None):
        """
        Initialize person follower.
        
        Args:
            motor_controller: Motor controller for robot movement
            sensor_manager: Sensor manager for distance/motion detection
            servo_controller: Servo controller for neck movements
        """
        self.motors = motor_controller
        self.sensors = sensor_manager
        self.servo = servo_controller
        
        self.following = False
        self._follow_thread = None
        self._stop_event = threading.Event()
        
        # Following parameters
        self.target_distance = 50  # Target distance in cm (maintain 50cm)
        self.min_distance = 30     # Stop if closer than 30cm
        self.max_distance = 150    # Lost person if farther than 150cm
        self.scan_step = 20        # Degrees to scan when searching
        self.search_timeout = 10   # Seconds before giving up search
        
        # Movement parameters
        self.forward_speed = 60    # Speed when moving forward
        self.turn_speed = 50       # Speed when turning
        self.backward_speed = 50   # Speed when backing up
        
        print("PersonFollower initialized")
    
    def _get_front_distance(self) -> Optional[float]:
        """Get distance reading from front ultrasonic sensor."""
        if not self.sensors:
            return random.uniform(40, 100)  # Simulation
        
        try:
            distance = self.sensors.get_ultrasonic_distance()
            return distance if distance > 0 else None
        except:
            return None
    
    def _scan_for_person(self) -> Optional[int]:
        """
        Scan left and right to find person.
        
        Returns:
            Angle where person detected, or None if not found
        """
        print("[Follow] Scanning for person...")
        
        # Update display
        try:
            from actuators.display import display
            display.clear()
            display.write_text("Searching...", row=0, col=2)
        except:
            pass
        
        # Get neck servo
        neck_servo = None
        neck_lock = None
        if self.servo:
            neck_servo = self.servo.get_servo('neck')
            neck_lock = self.servo.get_lock('neck')
        
        # Scan angles: center, right, left, far right, far left
        scan_angles = [90, 70, 110, 50, 130, 30, 150]
        
        for angle in scan_angles:
            if self._stop_event.is_set():
                return None
            
            # Move neck to angle
            if neck_servo and neck_lock:
                if neck_lock.acquire(blocking=False):
                    try:
                        neck_servo.set_angle(angle)
                        time.sleep(0.3)  # Wait for servo to move
                    finally:
                        neck_lock.release()
            
            # Check distance
            distance = self._get_front_distance()
            if distance and self.min_distance < distance < self.max_distance:
                print(f"[Follow] Person found at {angle}° ({distance:.1f}cm)")
                return angle
            
            time.sleep(0.1)
        
        # Person not found
        return None
    
    def _turn_to_angle(self, target_angle: int):
        """
        Turn robot body to face target angle.
        
        Args:
            target_angle: Neck servo angle (30-150, center=90)
        """
        if not self.motors:
            print(f"[Follow SIM] Turning to face {target_angle}°")
            return
        
        # Calculate turn direction and duration
        # Angles: 30=far left, 90=center, 150=far right
        if target_angle < 70:  # Far left
            print("[Follow] Turning left")
            self.motors.left(speed=self.turn_speed, duration=0.5)
        elif target_angle > 110:  # Far right
            print("[Follow] Turning right")
            self.motors.right(speed=self.turn_speed, duration=0.5)
        elif target_angle < 85:  # Slightly left
            print("[Follow] Adjusting left")
            self.motors.left(speed=self.turn_speed, duration=0.2)
        elif target_angle > 95:  # Slightly right
            print("[Follow] Adjusting right")
            self.motors.right(speed=self.turn_speed, duration=0.2)
        
        time.sleep(0.1)
    
    def _maintain_distance(self, current_distance: float):
        """
        Adjust robot position to maintain target distance.
        
        Args:
            current_distance: Current distance to person in cm
        """
        if not self.motors:
            print(f"[Follow SIM] Distance: {current_distance:.1f}cm")
            return
        
        distance_error = current_distance - self.target_distance
        
        if abs(distance_error) < 10:
            # Distance is good, don't move
            self.motors.stop()
            return
        
        if distance_error > 0:
            # Person is too far, move forward
            move_time = min(0.5, distance_error / 100)  # Scale time with distance
            print(f"[Follow] Moving forward ({current_distance:.1f}cm)")
            self.motors.forward(speed=self.forward_speed, duration=move_time)
        else:
            # Person is too close, back up
            move_time = min(0.3, abs(distance_error) / 100)
            print(f"[Follow] Backing up ({current_distance:.1f}cm)")
            self.motors.backward(speed=self.backward_speed, duration=move_time)
    
    def _center_neck_servo(self):
        """Return neck servo to center position."""
        if self.servo:
            neck_servo = self.servo.get_servo('neck')
            neck_lock = self.servo.get_lock('neck')
            
            if neck_servo and neck_lock:
                if neck_lock.acquire(blocking=True, timeout=2):
                    try:
                        neck_servo.set_angle(90)
                    finally:
                        neck_lock.release()
    
    def _follow_loop(self):
        """Main following loop running in separate thread."""
        print("Person following started")
        
        # Update display
        try:
            from actuators.display import display
            display.clear()
            display.write_text("Following You", row=0, col=1)
        except:
            pass
        
        # Center neck servo
        self._center_neck_servo()
        time.sleep(0.5)
        
        person_lost_time = None
        consecutive_good_readings = 0
        
        while not self._stop_event.is_set():
            # Get current distance
            distance = self._get_front_distance()
            
            if distance is None or distance > self.max_distance or distance < 5:
                # Person not in front or too close (sensor error)
                consecutive_good_readings = 0
                
                if person_lost_time is None:
                    person_lost_time = time.time()
                    print("[Follow] Person lost from view")
                
                # Check if lost too long
                if time.time() - person_lost_time > self.search_timeout:
                    print("[Follow] Search timeout, stopping")
                    break
                
                # Try to find person by scanning
                found_angle = self._scan_for_person()
                
                if found_angle is not None:
                    # Found person, turn to face them
                    self._turn_to_angle(found_angle)
                    self._center_neck_servo()
                    person_lost_time = None
                    time.sleep(0.3)
                else:
                    # Not found, wait a bit
                    time.sleep(0.5)
                
            elif distance < self.min_distance:
                # Too close, back up
                person_lost_time = None
                consecutive_good_readings = 0
                print(f"[Follow] Too close ({distance:.1f}cm), backing up")
                
                try:
                    from actuators.display import display
                    display.clear()
                    display.write_text("Too Close!", row=0, col=2)
                    display.write_text(f"{distance:.0f}cm", row=1, col=5)
                except:
                    pass
                
                if self.motors:
                    self.motors.backward(speed=self.backward_speed, duration=0.5)
                time.sleep(0.2)
            
            else:
                # Person detected at valid distance
                person_lost_time = None
                consecutive_good_readings += 1
                
                # Update display
                try:
                    from actuators.display import display
                    display.clear()
                    display.write_text("Following", row=0, col=3)
                    display.write_text(f"{distance:.0f}cm away", row=1, col=1)
                except:
                    pass
                
                # Maintain target distance
                self._maintain_distance(distance)
                time.sleep(0.2)
        
        # Stop motors when done
        if self.motors:
            self.motors.stop()
        
        # Center servo
        self._center_neck_servo()
        
        print("Person following stopped")
    
    def start_following(self) -> bool:
        """
        Start following mode in background thread.
        
        Returns:
            True if following started successfully
        """
        if self.following:
            print("Already following")
            return False
        
        if not self.motors and not self.sensors:
            print("Warning: No motors or sensors available, running in simulation mode")
        
        self._stop_event.clear()
        self._follow_thread = threading.Thread(target=self._follow_loop, daemon=True)
        self._follow_thread.start()
        self.following = True
        
        print("Person following activated!")
        return True
    
    def stop_following(self):
        """Stop following mode."""
        if not self.following:
            return
        
        print("Stopping person following...")
        self._stop_event.set()
        
        if self._follow_thread and self._follow_thread.is_alive():
            self._follow_thread.join(timeout=3)
        
        # Stop motors
        if self.motors:
            self.motors.stop()
        
        self.following = False
        
        # Clear display
        try:
            from actuators.display import display
            display.show_face('neutral')
        except:
            pass
        
        print("Following stopped")
    
    def is_following(self) -> bool:
        """Check if currently following."""
        return self.following
    
    def cleanup(self):
        """Cleanup resources."""
        self.stop_following()


# Global instance
_person_follower = None

def get_person_follower(motor_controller=None, sensor_manager=None, servo_controller=None):
    """Get or create global person follower instance."""
    global _person_follower
    if _person_follower is None:
        _person_follower = PersonFollower(motor_controller, sensor_manager, servo_controller)
    return _person_follower


if __name__ == '__main__':
    """Test person follower."""
    print("Testing Person Follower...")
    print("This requires motors, sensors, and servos.")
    
    follower = PersonFollower()
    
    try:
        print("\nStarting follow mode...")
        follower.start_following()
        
        print("Following for 30 seconds...")
        time.sleep(30)
        
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    finally:
        print("\nStopping follower...")
        follower.cleanup()
        print("Done!")
