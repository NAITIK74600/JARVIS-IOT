"""
Face Tracking Module for JARVIS
Tracks faces using camera and controls neck servo to follow the face.
Uses OpenCV for face detection and servo for tracking.
"""

import cv2
import time
import threading
import os
from typing import Optional, Tuple
import numpy as np

class FaceTracker:
    def __init__(self, servo_controller=None, camera_index=0):
        """
        Initialize face tracker.
        
        Args:
            servo_controller: Multi servo controller instance
            camera_index: Camera device index (default 0)
        """
        self.servo = servo_controller
        self.camera_index = camera_index
        self.camera = None
        self.tracking = False
        self._tracking_thread = None
        self._stop_event = threading.Event()
        
        # Face detection cascade
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        
        if self.face_cascade.empty():
            print("Warning: Face cascade classifier not loaded. Face tracking may not work.")
        
        # Tracking parameters
        self.frame_width = 640
        self.frame_height = 480
        self.center_threshold = 50  # Pixels from center to trigger movement
        self.servo_step = 5  # Degrees to move servo
        self.min_face_size = (50, 50)  # Minimum face size to detect
        
        # Servo limits (neck servo typically 30-150 degrees)
        self.servo_min = 30
        self.servo_max = 150
        self.servo_center = 90
        
        print("FaceTracker initialized")
    
    def _initialize_camera(self):
        """Initialize camera capture."""
        if self.camera is None or not self.camera.isOpened():
            self.camera = cv2.VideoCapture(self.camera_index)
            if not self.camera.isOpened():
                print("Error: Could not open camera")
                return False
            
            # Set camera resolution
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)
            print("Camera initialized")
        return True
    
    def _release_camera(self):
        """Release camera resources."""
        if self.camera is not None:
            self.camera.release()
            self.camera = None
            print("Camera released")
    
    def detect_face(self, frame) -> Optional[Tuple[int, int, int, int]]:
        """
        Detect largest face in frame.
        
        Args:
            frame: OpenCV frame (BGR)
        
        Returns:
            Tuple (x, y, w, h) of largest face or None if no face detected
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=self.min_face_size
        )
        
        if len(faces) == 0:
            return None
        
        # Return largest face
        largest_face = max(faces, key=lambda f: f[2] * f[3])  # area = w * h
        return tuple(largest_face)
    
    def calculate_servo_adjustment(self, face_x, face_w, current_angle) -> Optional[int]:
        """
        Calculate servo angle adjustment to center face.
        
        Args:
            face_x: X position of face
            face_w: Width of face
            current_angle: Current servo angle
        
        Returns:
            New servo angle or None if no adjustment needed
        """
        # Calculate face center
        face_center_x = face_x + face_w // 2
        frame_center_x = self.frame_width // 2
        
        # Calculate offset from center
        offset = face_center_x - frame_center_x
        
        # Check if adjustment needed
        if abs(offset) < self.center_threshold:
            return None  # Face is centered
        
        # Calculate new angle
        # If face is to the right, turn right (increase angle)
        # If face is to the left, turn left (decrease angle)
        if offset > 0:  # Face is right of center
            new_angle = current_angle + self.servo_step
        else:  # Face is left of center
            new_angle = current_angle - self.servo_step
        
        # Clamp to servo limits
        new_angle = max(self.servo_min, min(self.servo_max, new_angle))
        
        return new_angle
    
    def _tracking_loop(self):
        """Main tracking loop running in separate thread."""
        print("Face tracking started")
        
        # Update display
        try:
            from actuators.display import display
            display.clear()
            display.write_text("Tracking Face", row=0, col=1)
        except:
            pass
        
        if not self._initialize_camera():
            print("Failed to initialize camera for tracking")
            return
        
        # Get neck servo and its lock
        neck_servo = None
        neck_lock = None
        current_angle = self.servo_center
        
        if self.servo:
            neck_servo = self.servo.get_servo('neck')
            neck_lock = self.servo.get_lock('neck')
            
            if neck_servo and neck_lock:
                # Center the servo at start
                if neck_lock.acquire(blocking=False):
                    try:
                        neck_servo.set_angle(current_angle)
                        time.sleep(0.5)
                    finally:
                        neck_lock.release()
        
        face_lost_count = 0
        max_lost_frames = 30  # Return to center after 30 frames without face
        
        while not self._stop_event.is_set():
            ret, frame = self.camera.read()
            if not ret:
                print("Error: Failed to read frame")
                time.sleep(0.1)
                continue
            
            # Detect face
            face = self.detect_face(frame)
            
            if face is not None:
                x, y, w, h = face
                face_lost_count = 0
                
                # Calculate servo adjustment
                if neck_servo and neck_lock:
                    new_angle = self.calculate_servo_adjustment(x, w, current_angle)
                    
                    if new_angle is not None and new_angle != current_angle:
                        # Move servo
                        if neck_lock.acquire(blocking=False):
                            try:
                                neck_servo.set_angle(new_angle)
                                current_angle = new_angle
                                print(f"[Face Track] Adjusted to {current_angle}°")
                            finally:
                                neck_lock.release()
                
                # Update display with tracking status
                try:
                    from actuators.display import display
                    display.clear()
                    display.write_text("Face Locked", row=0, col=2)
                    display.write_text(f"Angle: {current_angle}", row=1, col=0)
                except:
                    pass
            else:
                face_lost_count += 1
                
                # If face lost for too long, return to center
                if face_lost_count >= max_lost_frames:
                    if current_angle != self.servo_center:
                        if neck_servo and neck_lock:
                            if neck_lock.acquire(blocking=False):
                                try:
                                    neck_servo.set_angle(self.servo_center)
                                    current_angle = self.servo_center
                                    print("[Face Track] Face lost, returning to center")
                                finally:
                                    neck_lock.release()
                    
                    # Update display
                    try:
                        from actuators.display import display
                        display.clear()
                        display.write_text("Searching...", row=0, col=2)
                    except:
                        pass
                    
                    face_lost_count = 0
            
            # Small delay to prevent CPU overload
            time.sleep(0.05)  # 20 FPS
        
        # Return to center when stopping
        if neck_servo and neck_lock:
            if neck_lock.acquire(blocking=True, timeout=2):
                try:
                    neck_servo.set_angle(self.servo_center)
                finally:
                    neck_lock.release()
        
        self._release_camera()
        print("Face tracking stopped")
    
    def start_tracking(self) -> bool:
        """
        Start face tracking in background thread.
        
        Returns:
            True if tracking started successfully
        """
        if self.tracking:
            print("Face tracking already running")
            return False
        
        self._stop_event.clear()
        self._tracking_thread = threading.Thread(target=self._tracking_loop, daemon=True)
        self._tracking_thread.start()
        self.tracking = True
        
        return True
    
    def stop_tracking(self):
        """Stop face tracking."""
        if not self.tracking:
            return
        
        print("Stopping face tracking...")
        self._stop_event.set()
        
        if self._tracking_thread and self._tracking_thread.is_alive():
            self._tracking_thread.join(timeout=3)
        
        self.tracking = False
        
        # Clear display
        try:
            from actuators.display import display
            display.show_face('neutral')
        except:
            pass
    
    def is_tracking(self) -> bool:
        """Check if currently tracking."""
        return self.tracking
    
    def cleanup(self):
        """Cleanup resources."""
        self.stop_tracking()
        self._release_camera()


# Global instance
_face_tracker = None

def get_face_tracker(servo_controller=None):
    """Get or create global face tracker instance."""
    global _face_tracker
    if _face_tracker is None:
        _face_tracker = FaceTracker(servo_controller)
    return _face_tracker


if __name__ == '__main__':
    """Test face tracking."""
    print("Testing Face Tracker...")
    print("This requires a camera and neck servo.")
    
    tracker = FaceTracker()
    
    try:
        print("\nStarting face tracking...")
        tracker.start_tracking()
        
        print("Tracking for 30 seconds (move your face around)...")
        time.sleep(30)
        
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    finally:
        print("\nStopping tracker...")
        tracker.cleanup()
        print("Done!")
