#!/usr/bin/env python3
"""
Quick test script for motor wheels
Tests all directions: forward, backward, left, right, stop
"""
import time
from tools.motor_tools import move_forward, move_backward, turn_left, turn_right, stop_moving

def test_motors():
    """Test all motor movements"""
    print("=" * 50)
    print("🚗 JARVIS WHEEL TEST")
    print("=" * 50)
    
    print("\n1️⃣  Testing FORWARD...")
    result = move_forward("2")
    print(f"   ✓ {result}")
    time.sleep(1)
    
    print("\n2️⃣  Testing BACKWARD...")
    result = move_backward("2")
    print(f"   ✓ {result}")
    time.sleep(1)
    
    print("\n3️⃣  Testing LEFT TURN...")
    result = turn_left("1")
    print(f"   ✓ {result}")
    time.sleep(1)
    
    print("\n4️⃣  Testing RIGHT TURN...")
    result = turn_right("1")
    print(f"   ✓ {result}")
    time.sleep(1)
    
    print("\n5️⃣  Testing STOP...")
    result = stop_moving()
    print(f"   ✓ {result}")
    
    print("\n" + "=" * 50)
    print("✅ ALL MOTOR TESTS COMPLETE!")
    print("=" * 50)

if __name__ == "__main__":
    try:
        test_motors()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        stop_moving()
    except Exception as e:
        print(f"\n❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        stop_moving()
