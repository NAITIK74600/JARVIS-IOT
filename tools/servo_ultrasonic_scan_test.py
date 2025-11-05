"""servo_ultrasonic_scan_test.py

Standalone quick test to verify coordinated operation of the servo (head) and
ultrasonic sensor before using full Jarvis application.

Usage:
  export SERVO_PIN=19               # or your servo signal BCM pin
  export ULTRASONIC_TRIGGER_PIN=23  # optional override
  export ULTRASONIC_ECHO_PIN=24     # optional override
  python3 tools/servo_ultrasonic_scan_test.py

Adjust environment variables SCAN_START_ANGLE, SCAN_END_ANGLE, SCAN_STEP to tune.
"""
import os
import time
import sys

# Ensure project root on path when running directly
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from actuators.servo import Servo
from sensors.ultrasonic import Ultrasonic

SERVO_PIN = int(os.getenv("SERVO_PIN", "12"))
TRIG_PIN = int(os.getenv("ULTRASONIC_TRIGGER_PIN", "23"))
ECHO_PIN = int(os.getenv("ULTRASONIC_ECHO_PIN", "24"))

START = int(os.getenv("SCAN_START_ANGLE", "30"))
END = int(os.getenv("SCAN_END_ANGLE", "150"))
STEP = int(os.getenv("SCAN_STEP", "15"))
SETTLE = float(os.getenv("SCAN_SETTLE", "0.18"))

print(f"[INFO] Servo pin={SERVO_PIN}  Ultrasonic TRIG={TRIG_PIN} ECHO={ECHO_PIN}")
print(f"[INFO] Sweep {START}->{END} step {STEP}")

servo = Servo(SERVO_PIN)
ultra = Ultrasonic(TRIG_PIN, ECHO_PIN)

angles = list(range(START, END + 1, STEP))
results = []
try:
    for a in angles:
        servo.set_angle(a)
        time.sleep(SETTLE)
        d = ultra.measure_distance()
        if d < 0:
            status = 'TIMEOUT'
        else:
            status = f"{d:.1f} cm"
        print(f"Angle {a:3d} -> {status}")
        results.append((a, d))
    mid = (START + END)//2
    servo.set_angle(mid)
finally:
    servo.cleanup()

# Summary
valid = [d for _, d in results if d >= 0]
if valid:
    best_angle, best_dist = max(((a,d) for a,d in results if d >=0), key=lambda t: t[1])
    avg = sum(valid)/len(valid)
    print(f"\n[SUMMARY] Samples={len(valid)}  Best angle={best_angle} ({best_dist:.1f} cm)  Average={avg:.1f} cm")
else:
    print("\n[SUMMARY] No valid ultrasonic readings.")

print("Done.")
