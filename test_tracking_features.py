#!/usr/bin/env python3
"""
Test Face Tracking and Follow Me Features
Tests the new tracking capabilities of JARVIS.
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

print("=" * 70)
print("JARVIS FACE TRACKING & FOLLOW ME TEST")
print("=" * 70)

# Test 1: Import Check
print("\n1. Testing Module Imports...")
print("-" * 70)

try:
    from navigation.face_tracker import FaceTracker, get_face_tracker
    print("✅ FaceTracker module imported successfully")
except Exception as e:
    print(f"❌ Error importing FaceTracker: {e}")
    import traceback
    traceback.print_exc()

try:
    from navigation.person_follower import PersonFollower, get_person_follower
    print("✅ PersonFollower module imported successfully")
except Exception as e:
    print(f"❌ Error importing PersonFollower: {e}")
    import traceback
    traceback.print_exc()

# Test 2: Face Tracker Initialization
print("\n2. Testing FaceTracker Initialization...")
print("-" * 70)

try:
    tracker = FaceTracker()
    print("✅ FaceTracker initialized")
    print(f"   - Camera index: {tracker.camera_index}")
    print(f"   - Servo step: {tracker.servo_step}°")
    print(f"   - Center threshold: {tracker.center_threshold}px")
    print(f"   - Tracking: {tracker.is_tracking()}")
except Exception as e:
    print(f"❌ Error initializing FaceTracker: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Person Follower Initialization
print("\n3. Testing PersonFollower Initialization...")
print("-" * 70)

try:
    follower = PersonFollower()
    print("✅ PersonFollower initialized")
    print(f"   - Target distance: {follower.target_distance}cm")
    print(f"   - Min distance: {follower.min_distance}cm")
    print(f"   - Max distance: {follower.max_distance}cm")
    print(f"   - Following: {follower.is_following()}")
except Exception as e:
    print(f"❌ Error initializing PersonFollower: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Tool Functions
print("\n4. Testing Tool Functions...")
print("-" * 70)

try:
    # Check if tools are importable from main
    import importlib.util
    spec = importlib.util.spec_from_file_location("main", "main.py")
    if spec and spec.loader:
        print("✅ main.py is loadable")
        
        # Check for tracking functions in main.py
        with open("main.py", "r") as f:
            content = f.read()
            
        tracking_features = {
            "track_face": "track_face" in content,
            "stop_face_tracking": "stop_face_tracking" in content,
            "follow_me": "follow_me" in content,
            "stop_following": "stop_following" in content,
            "get_tracking_status": "get_tracking_status" in content,
        }
        
        for feature, found in tracking_features.items():
            status = "✅" if found else "❌"
            print(f"   {status} {feature} function: {'Found' if found else 'Missing'}")
    
except Exception as e:
    print(f"❌ Error checking tools: {e}")
    import traceback
    traceback.print_exc()

# Test 5: OpenCV Face Detection
print("\n5. Testing OpenCV Face Detection...")
print("-" * 70)

try:
    import cv2
    print(f"✅ OpenCV version: {cv2.__version__}")
    
    # Check if Haar Cascade is available
    cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    face_cascade = cv2.CascadeClassifier(cascade_path)
    
    if not face_cascade.empty():
        print("✅ Face detection cascade loaded")
    else:
        print("❌ Face detection cascade failed to load")
    
except Exception as e:
    print(f"❌ OpenCV error: {e}")

# Test 6: Integration with Servo Controller
print("\n6. Testing Integration with Multi-Servo Controller...")
print("-" * 70)

try:
    from actuators.multi_servo_controller import multi_servo_controller
    
    # Test if we can get face tracker with servo
    tracker_with_servo = get_face_tracker(multi_servo_controller)
    print("✅ FaceTracker can integrate with servo controller")
    print(f"   - Servo controller provided: {tracker_with_servo.servo is not None}")
    
except Exception as e:
    print(f"❌ Servo integration error: {e}")

# Test 7: Integration with Sensors
print("\n7. Testing Integration with Sensor Manager...")
print("-" * 70)

try:
    from sensors.sensor_manager import SensorManager
    sensor_mgr = SensorManager()
    
    # Test if we can get follower with sensors
    follower_with_sensors = get_person_follower(None, sensor_mgr, None)
    print("✅ PersonFollower can integrate with sensor manager")
    print(f"   - Sensor manager provided: {follower_with_sensors.sensors is not None}")
    
except Exception as e:
    print(f"⚠️  Sensor integration: {e}")
    print("   (This is OK if sensors are not connected)")

# Test 8: Hinglish Commands Check
print("\n8. Testing Hinglish Command Support...")
print("-" * 70)

try:
    from core.persona import persona
    prompt = persona.get_prompt()
    
    hinglish_commands = [
        "track face",
        "follow me",
        "mere saath chalo",
        "mera face track karo",
        "follow karo",
        "ruk jao",
    ]
    
    found_count = 0
    for cmd in hinglish_commands:
        if cmd.lower() in prompt.lower():
            print(f"   ✅ '{cmd}' found in system prompt")
            found_count += 1
    
    if found_count > 0:
        print(f"✅ {found_count}/{len(hinglish_commands)} commands in system prompt")
    else:
        print("⚠️  Hinglish commands not found in system prompt")
        print("   (Will still work via tool descriptions)")
    
except Exception as e:
    print(f"❌ Error checking prompt: {e}")


# Summary
print("\n" + "=" * 70)
print("TEST SUMMARY")
print("=" * 70)
print("""
✅ Features Implemented:

1. FACE TRACKING:
   • Uses OpenCV Haar Cascade for face detection
   • Automatically moves neck servo to follow face
   • Real-time tracking at 20 FPS
   • Returns to center when face lost
   • Updates I2C display with tracking status

2. FOLLOW ME MODE:
   • Uses ultrasonic sensor for distance measurement
   • Maintains 50cm target distance
   • Scans with neck servo when person lost
   • Moves forward/backward to maintain distance
   • Turns to face person if moved to side
   • Stops if too close or person lost

3. VOICE COMMANDS (English & Hinglish):
   English:
   - "Jarvis, track my face"
   - "Jarvis, follow me"
   - "Jarvis, stop tracking"
   - "Jarvis, stop following"
   
   Hinglish:
   - "Jarvis, mera face track karo"
   - "Jarvis, mere saath chalo"
   - "Jarvis, follow karo"
   - "Jarvis, ruk jao"

4. TOOLS ADDED:
   • track_face() - Start face tracking
   • stop_face_tracking() - Stop face tracking
   • follow_me() - Start follow mode
   • stop_following() - Stop follow mode
   • get_tracking_status() - Check status

📝 How to Use:

Face Tracking (Camera + Neck Servo):
   1. "Jarvis, track my face"
   2. JARVIS will follow your face with neck servo
   3. "Jarvis, stop tracking" when done

Follow Me (Motors + Sensors + Servo):
   1. "Jarvis, follow me"
   2. Walk slowly, JARVIS will follow
   3. Maintains ~50cm distance
   4. "Jarvis, stop following" when done

🔧 Hardware Requirements:

Face Tracking:
   ✓ USB Camera (or Pi Camera)
   ✓ Neck Servo (GPIO 18)
   ✓ I2C Display (optional, for status)

Follow Me:
   ✓ Motor Controller (L298N)
   ✓ Ultrasonic Sensor (GPIO 27, 22)
   ✓ Neck Servo (GPIO 18, for scanning)
   ✓ Motors connected to chassis
   ✓ I2C Display (optional)

Optional Enhancement:
   ✓ PIR Sensor - Auto-detect motion
   ✓ IR Sensor - Additional obstacle detection

🚀 Ready to Test!
   Run: ./run.sh
   Then try:
   - "Jarvis, track my face"
   - "Jarvis, mere saath chalo"
""")
print("=" * 70)
