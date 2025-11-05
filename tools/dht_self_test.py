"""dht_self_test.py

Quick diagnostic for the DHT11/DHT22 sensor.
Respects env:
  DHT_PIN (default 4)
  DHT_TYPE (11 or 22, default 11)
Run: python3 tools/dht_self_test.py
"""
import os, time, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from sensors.dht import DHT

pin = int(os.getenv('DHT_PIN', '4'))
type_env = os.getenv('DHT_TYPE', '11')
print(f"[INFO] DHT pin={pin} type={'DHT22' if type_env=='22' else 'DHT11'}")

sensor = DHT(pin=pin)

success = 0
attempts = 8
for i in range(1, attempts+1):
    t = sensor.read_temperature()
    h = sensor.read_humidity()
    if t is not None and h is not None:
        success += 1
        print(f"Reading {i}: {t:.1f}°C  {h:.1f}%")
    else:
        print(f"Reading {i}: FAILED")
    time.sleep(2)

print(f"\n[SUMMARY] {success}/{attempts} successful readings")
if success == 0:
    print("[HINT] Check: wiring (3.3V, GND, data with 10K pull-up), correct DHT_TYPE, stable power.")
elif success < attempts//2:
    print("[HINT] Many failures: sensor warming up or marginal. Give it more time or re-check pull-up resistor.")
else:
    print("[OK] Sensor operating within expected range.")
