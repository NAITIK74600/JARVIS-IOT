#!/usr/bin/env python3
"""Minimal low-level servo pulse tester for pigpio.
Usage: python3 tools/servo_raw_test.py [pin]
Default pin = 12 (set SERVO_PIN env to override in other code).
"""
import sys, time, pigpio

PIN = int(sys.argv[1]) if len(sys.argv) > 1 else 12
pi = pigpio.pi()
if not pi.connected:
    print("ERROR: pigpio daemon not running. Start with: sudo systemctl start pigpiod")
    sys.exit(1)

print(f"Using BCM pin {PIN}. Sending center pulse (1500µs)...")
pi.set_servo_pulsewidth(PIN, 1500)

def step_sequence(pulses, delay=1.2):
    for pw in pulses:
        print(f"Pulse {pw}µs")
        pi.set_servo_pulsewidth(PIN, pw)
        time.sleep(delay)

try:
    step_sequence([500, 1000, 1500, 2000, 2400])
    print("Detaching (0µs)")
    pi.set_servo_pulsewidth(PIN, 0)
    time.sleep(1)
    print("Center again (1500µs)")
    pi.set_servo_pulsewidth(PIN, 1500)
    time.sleep(1)
finally:
    print("Stopping pigpio connection.")
    pi.set_servo_pulsewidth(PIN, 0)
    pi.stop()
