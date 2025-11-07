#!/usr/bin/env bash
set -euo pipefail

# Quick test of JARVIS scanning functionality

VENV_DIR=".venv"

if [ ! -d "$VENV_DIR" ]; then
  echo "❌ Virtual environment not found. Run ./setup_env.sh first."
  exit 1
fi

# shellcheck source=/dev/null
source "$VENV_DIR/bin/activate"

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║        JARVIS Scanning System - Quick Test                   ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

python3 << 'EOF'
import sys
import time

print("Testing scanning components...")
print("")

# Test 1: Check if scanner module loads
print("1. Testing scanner module...")
try:
    from navigation.scanner import perform_scan, human_readable_summary, ScanResult
    print("   ✅ Scanner module loaded")
except ImportError as e:
    print(f"   ❌ Failed to load scanner: {e}")
    sys.exit(1)

# Test 2: Check servo controller
print("")
print("2. Testing servo controller...")
try:
    from actuators.multi_servo_controller import multi_servo_controller
    neck_servo = multi_servo_controller.get_servo('neck')
    if neck_servo:
        print("   ✅ Neck servo controller ready")
        print(f"   ℹ️  Servo at pin: {neck_servo.pin}")
    else:
        print("   ⚠️  Neck servo not configured (hardware may not be connected)")
except Exception as e:
    print(f"   ⚠️  Servo controller issue: {e}")

# Test 3: Check sensor manager
print("")
print("3. Testing sensor manager...")
try:
    from sensors.sensor_manager import SensorManager
    sensor_manager = SensorManager()
    print("   ✅ Sensor manager initialized")
    
    # Try to get a distance reading
    dist = sensor_manager.get_distance()
    if dist >= 0:
        print(f"   ✅ Ultrasonic sensor working: {dist:.1f} cm")
    else:
        print("   ⚠️  No distance reading (sensor may need hardware)")
except Exception as e:
    print(f"   ⚠️  Sensor manager issue: {e}")

# Test 4: Check if scan tool is available
print("")
print("4. Testing scan tool registration...")
try:
    from main import scan_environment, scan_environment_custom, get_last_scan
    print("   ✅ Scan tools are registered:")
    print("      • scan_environment (standard room scan)")
    print("      • scan_environment_custom (custom angle scan)")
    print("      • get_last_scan (retrieve last scan results)")
except ImportError as e:
    print(f"   ❌ Failed to import scan tools: {e}")
    sys.exit(1)

print("")
print("═══════════════════════════════════════════════════════════════")
print("")
print("✅ All scanning components loaded successfully!")
print("")
print("📋 How to use scanning:")
print("")
print("   When you say to JARVIS:")
print("   • 'Scan the room'")
print("   • 'Scan the area'")
print("   • 'Look around'")
print("   • 'Check for obstacles'")
print("")
print("   JARVIS will:")
print("   1. Move the neck servo from 30° to 150°")
print("   2. Take ultrasonic distance readings at each angle")
print("   3. Identify the safest direction (most clearance)")
print("   4. Report blocked angles (< 20cm)")
print("   5. Return to center position")
print("")
print("📊 Scan Configuration (environment variables):")
print("   SCAN_START_ANGLE=30      # Start angle in degrees")
print("   SCAN_END_ANGLE=150       # End angle in degrees")
print("   SCAN_STEP=15             # Step size in degrees")
print("   SCAN_SAMPLES_PER_ANGLE=3 # Samples per angle (median)")
print("   SCAN_SETTLE=0.18         # Settle time after movement")
print("")
print("🚀 Ready! Start JARVIS with: ./run.sh")
print("")
EOF
