"""Quick self-test for pigpio servo environment.
Run: python3 tools/servo_self_test.py <BCM_PIN>

It will:
1. Check pigpio import
2. Check daemon connectivity
3. Print hardware revision
4. Send center, min, max pulse
5. Offer hints if no movement detected
"""
import sys, time, os

DEFAULT_MIN = int(os.getenv("SERVO_MIN_PULSE", "500"))
DEFAULT_MAX = int(os.getenv("SERVO_MAX_PULSE", "2400"))

pin = 18
if len(sys.argv) > 1:
    try:
        pin = int(sys.argv[1])
    except ValueError:
        print("Invalid pin. Usage: python3 tools/servo_self_test.py <BCM_PIN>")
        sys.exit(1)

print(f"[INFO] Using BCM pin {pin}")

try:
    import pigpio
except Exception as e:
    print(f"[FATAL] Cannot import pigpio: {e}\nInstall with: pip install pigpio\nAnd ensure daemon: sudo systemctl enable --now pigpiod")
    sys.exit(1)

pi = pigpio.pi()
if not pi.connected:
    print("[FATAL] pigpio daemon not connected. Start it: sudo systemctl start pigpiod")
    sys.exit(1)

print(f"[OK] Connected to pigpio. HW Revision: {pi.get_hardware_revision():X}")
print(f"[INFO] Pulse test range {DEFAULT_MIN}-{DEFAULT_MAX}µs")

center_pw = (DEFAULT_MIN + DEFAULT_MAX)//2
sequence = [center_pw, DEFAULT_MIN, DEFAULT_MAX, center_pw]
labels = ["center","min","max","center"]
for label, pw in zip(labels, sequence):
    print(f"[TEST] {label}: {pw}µs")
    pi.set_servo_pulsewidth(pin, pw)
    time.sleep(1.2)

pi.set_servo_pulsewidth(pin, 0)
pi.stop()

print("\nIf servo did NOT move, check:")
print(" 1. Wiring: Brown/GND -> Pi GND, Red/V+ 5V (NOT 3.3V), Orange/Signal -> BCM pin")
print(" 2. Power: Stable 5V supply able to source ~500mA peaks; avoid drawing from weak USB ports")
print(" 3. Common Ground: External 5V ground must be tied to Pi ground")
print(" 4. Pin Mode: Ensure you used BCM numbering. Example: Physical pin 12 == BCM 18")
print(" 5. Servo Health: Try another servo or test this servo with simple Arduino/RC tester")
print(" 6. Range: Try narrower pulses: export SERVO_MIN_PULSE=1000 SERVO_MAX_PULSE=2000 then re-run")
print(" 7. Pigpio Daemon: Enable at boot: sudo systemctl enable pigpiod")
print(" 8. Conflicts: Stop other services using that pin (camera overlays, other PWM libs)")
