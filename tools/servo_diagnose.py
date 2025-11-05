#!/usr/bin/env python3
"""Servo Diagnostic Utility

Usage: python3 tools/servo_diagnose.py [pin]
Default pin = 12 (BCM)

Features:
- Angle test (0,45,90,135,180)
- Sweep test
- Raw pulse test (enter µs directly)
- Auto boundary probe (optional)

Press Ctrl+C anytime to exit.
"""
import sys, os, time
import pigpio

DEFAULT_PIN = 12
MIN_PULSE = 500
MAX_PULSE = 2400

class ServoDiag:
    def __init__(self, pin, min_pulse=MIN_PULSE, max_pulse=MAX_PULSE):
        self.pin = pin
        self.min_pulse = min_pulse
        self.max_pulse = max_pulse
        self.pi = pigpio.pi()
        if not self.pi.connected:
            print("ERROR: Cannot connect to pigpio. Run: sudo systemctl start pigpiod")
            sys.exit(1)
        print(f"Connected to pigpio. Using pin {self.pin}.")

    def angle_to_pulse(self, angle):
        return int(self.min_pulse + (angle/180.0)*(self.max_pulse - self.min_pulse))

    def set_angle(self, angle):
        pw = self.angle_to_pulse(angle)
        print(f" Angle {angle:3d}° => {pw}µs")
        self.pi.set_servo_pulsewidth(self.pin, pw)

    def pulse(self, pw):
        print(f" Raw pulse => {pw}µs")
        self.pi.set_servo_pulsewidth(self.pin, pw)

    def detach(self):
        print(" Detach (pulse 0)")
        self.pi.set_servo_pulsewidth(self.pin, 0)

    def cleanup(self):
        self.detach()
        self.pi.stop()

    def angle_test(self):
        print("\n[Angle Test]")
        for a in (0,45,90,135,180,90):
            self.set_angle(a)
            time.sleep(1)

    def sweep(self, step=15, delay=0.05):
        print("\n[Sweep Test]")
        for a in range(0,181,step):
            self.set_angle(a)
            time.sleep(delay)
        for a in range(180,-1,-step):
            self.set_angle(a)
            time.sleep(delay)

    def pulse_test(self):
        print("\n[Raw Pulse Test] Enter microseconds (e.g. 500 .. 2400) or 'q' to quit.")
        while True:
            val = input(" pulse> ").strip().lower()
            if val in ("q","quit","exit"): break
            if not val.isdigit():
                print(" Enter a number in microseconds.")
                continue
            pw = int(val)
            if pw < 300 or pw > 2700:
                print(" WARNING: Outside typical safe range (300-2700). Proceeding anyway.")
            self.pulse(pw)

    def auto_probe(self):
        print("\n[Auto Boundary Probe] (Experimental)")
        print(" Expanding from mid outward until jitter detected. Press Ctrl+C to abort.")
        mid = self.angle_to_pulse(90)
        left = mid; right = mid
        try:
            for delta in range(0,140,5):
                left = self.angle_to_pulse(max(0,90-delta))
                right = self.angle_to_pulse(min(180,90+delta))
                print(f" Probe delta={delta:3d} => L {left}µs  R {right}µs")
                self.pi.set_servo_pulsewidth(self.pin, left); time.sleep(0.4)
                self.pi.set_servo_pulsewidth(self.pin, right); time.sleep(0.4)
        except KeyboardInterrupt:
            print(" Probe interrupted.")


def main():
    pin = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PIN
    diag = ServoDiag(pin)
    try:
        diag.angle_test()
        diag.sweep()
        diag.pulse_test()
        ans = input(" Run auto boundary probe? (y/N): ").strip().lower()
        if ans.startswith('y'):
            diag.auto_probe()
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
    finally:
        print("Cleaning up...")
        diag.cleanup()
        print("Done.")

if __name__ == "__main__":
    main()
