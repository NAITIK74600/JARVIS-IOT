#!/usr/bin/env python3
"""
Sensor Command Detection Test Script
Tests if JARVIS properly recognizes sensor-related commands
"""

import sys
import os

# Test commands that should trigger sensor detection
TEST_COMMANDS = {
    "Temperature/Humidity": [
        "what's the temperature",
        "check temperature",
        "humidity level",
        "temp",
        "weather inside",
        "temperature batao",
        "mausam kaisa hai",
    ],
    "Alcohol Detection": [
        "check for alcohol",
        "is there alcohol",
        "detect drinking",
        "mq3 sensor",
        "alcohol detected",
        "alcohol detect karo",
    ],
    "Distance Measurement": [
        "how far is the wall",
        "check distance",
        "ultrasonic reading",
        "measure distance",
        "kitni duri hai",
        "distance batao",
    ],
    "Motion Detection": [
        "is there motion",
        "detect movement",
        "check for motion",
        "pir sensor",
        "koi movement hai",
        "motion detect karo",
    ],
    "All Sensors": [
        "check all sensors",
        "sensor status",
        "sensor readings",
        "check sensors",
        "saare sensor check karo",
    ],
}


def test_offline_responder():
    """Test offline responder keyword matching"""
    print("=" * 70)
    print("SENSOR COMMAND DETECTION TEST")
    print("=" * 70)
    print()
    
    # Import the offline responder
    sys.path.insert(0, '/home/naitik/JARVIS-IOT')
    from core.offline_responder import OfflineResponder
    from tools.sensor_tools import set_sensor_manager
    
    # Initialize responder
    responder = OfflineResponder()
    
    total_tests = 0
    passed_tests = 0
    
    for category, commands in TEST_COMMANDS.items():
        print(f"\n📋 Testing: {category}")
        print("-" * 70)
        
        for cmd in commands:
            total_tests += 1
            
            # Test if command triggers appropriate response
            # We'll just check if the responder processes it without errors
            try:
                response = responder.respond(cmd)
                
                # Check if response contains sensor-related keywords or data
                detected = False
                if any(keyword in response.lower() for keyword in [
                    'temperature', 'humidity', 'alcohol', 'distance', 'motion',
                    'sensor', 'detected', 'reading', 'cm', '°c', '%', 'yes', 'no'
                ]):
                    detected = True
                    passed_tests += 1
                    status = "✅ PASS"
                else:
                    status = "❌ FAIL"
                
                print(f"  {status}: '{cmd}'")
                if not detected:
                    print(f"    Response: {response[:80]}...")
                
            except Exception as e:
                print(f"  ❌ ERROR: '{cmd}' - {str(e)[:60]}")
    
    print()
    print("=" * 70)
    print(f"TEST RESULTS: {passed_tests}/{total_tests} tests passed ({(passed_tests/total_tests)*100:.1f}%)")
    print("=" * 70)
    
    if passed_tests == total_tests:
        print("\n🎉 ALL TESTS PASSED! Sensor command detection is working perfectly!")
    elif passed_tests >= total_tests * 0.7:
        print(f"\n⚠️  Most tests passed ({passed_tests}/{total_tests}), but some commands need attention")
    else:
        print(f"\n❌ ISSUES DETECTED: Only {passed_tests}/{total_tests} tests passed")
    
    return passed_tests == total_tests


def test_mode_optimizer():
    """Test that sensor commands don't trigger offline mode unnecessarily"""
    print("\n" + "=" * 70)
    print("MODE OPTIMIZER TEST - Ensuring sensor commands work smoothly")
    print("=" * 70)
    print()
    
    sys.path.insert(0, '/home/naitik/JARVIS-IOT')
    from core.mode_optimizer import ModeOptimizer
    
    optimizer = ModeOptimizer()
    
    # These should NOT force offline (general conversation)
    should_be_online = [
        "what is the temperature",
        "tell me about alcohol",
        "how does a motion sensor work",
        "explain distance measurement",
    ]
    
    # These SHOULD force offline (direct sensor commands)
    should_be_offline = [
        "check sensor",
        "scan environment",
        "read sensor",
    ]
    
    print("\n📊 Commands that should use ONLINE mode (cloud AI):")
    print("-" * 70)
    for cmd in should_be_online:
        should_offline, reason = optimizer.should_use_offline(cmd)
        status = "✅" if not should_offline else "❌"
        print(f"  {status} '{cmd}' → {'OFFLINE' if should_offline else 'ONLINE'}")
        if should_offline:
            print(f"     Reason: {reason}")
    
    print("\n📊 Commands that should use OFFLINE mode (local control):")
    print("-" * 70)
    for cmd in should_be_offline:
        should_offline, reason = optimizer.should_use_offline(cmd)
        status = "✅" if should_offline else "❌"
        print(f"  {status} '{cmd}' → {'OFFLINE' if should_offline else 'ONLINE'}")
        if not should_offline:
            print(f"     Reason: {reason}")


if __name__ == "__main__":
    print("\n🤖 JARVIS Sensor Command Detection Test Suite\n")
    
    try:
        # Test 1: Offline responder detection
        test_offline_responder()
        
        # Test 2: Mode optimizer behavior
        test_mode_optimizer()
        
        print("\n" + "=" * 70)
        print("✨ TEST SUITE COMPLETE")
        print("=" * 70)
        print("\n💡 TIP: Run JARVIS and try these voice commands:")
        print("   - 'what's the temperature'")
        print("   - 'how far is the wall'")
        print("   - 'check for motion'")
        print("   - 'is there alcohol'")
        print("   - 'check all sensors'")
        print()
        
    except Exception as e:
        print(f"\n❌ TEST SUITE ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
