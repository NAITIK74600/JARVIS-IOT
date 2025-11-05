"""
sensor_self_test.py

Quickly tests all major sensors (ultrasonic, PIR, DHT, MQ3) and reports status.
Run: python3 tools/sensor_self_test.py

Reads environment variables for pin config (see sensor_manager.py for details).
"""
import os
import time
import traceback

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

print("\n=== JARVIS SENSOR SELF-TEST ===\n")

# --- Ultrasonic ---
try:
    from sensors.ultrasonic import Ultrasonic
    trig = int(os.getenv('ULTRASONIC_TRIGGER_PIN', '23'))
    echo = int(os.getenv('ULTRASONIC_ECHO_PIN', '24'))
    u = Ultrasonic(trigger_pin=trig, echo_pin=echo)
    print(f"[Ultrasonic] Trigger: BCM {trig}, Echo: BCM {echo}")
    dists = []
    for i in range(5):
        d = u.measure_distance()
        dists.append(d)
        print(f"  Reading {i+1}: {d:.1f} cm" if d >= 0 else f"  Reading {i+1}: TIMEOUT")
        time.sleep(0.3)
    if all(x < 0 for x in dists):
        print("  [FAIL] All readings timed out. Check wiring, voltage divider, and pin config.")
    elif any(x < 0 for x in dists):
        print("  [WARN] Some timeouts. Check for loose wires or electrical noise.")
    else:
        print("  [OK] Ultrasonic sensor appears functional.")
except Exception as e:
    print(f"[Ultrasonic] ERROR: {e}\n{traceback.format_exc()}")

# --- PIR ---
try:
    from sensors.pir import PIR
    pir_pin = int(os.getenv('PIR_PIN', '17'))
    pir = PIR(pin=pir_pin)
    print(f"[PIR] Pin: BCM {pir_pin}")
    print("  Waiting for motion (10s window)... Move in front of sensor!")
    pir.start_monitoring()
    t0 = time.time()
    motion = False
    while time.time() - t0 < 10:
        if pir.last_motion_time:
            print(f"  [OK] Motion detected at {time.ctime(pir.last_motion_time)}")
            motion = True
            break
        time.sleep(0.2)
    pir.stop_monitoring()
    if not motion:
        print("  [WARN] No motion detected. Check sensor orientation and wiring.")
except Exception as e:
    print(f"[PIR] ERROR: {e}\n{traceback.format_exc()}")

# --- DHT ---
try:
    from sensors.dht import DHT
    dht_pin = int(os.getenv('DHT_PIN', '4'))
    dht = DHT(pin=dht_pin)
    print(f"[DHT] Pin: BCM {dht_pin}")
    temp = dht.read_temperature()
    hum = dht.read_humidity()
    if temp is not None and hum is not None:
        print(f"  [OK] Temp: {temp:.1f}°C, Humidity: {hum:.1f}%")
    else:
        print("  [FAIL] No reading. Check wiring, sensor type, and pull-up resistor.")
except Exception as e:
    print(f"[DHT] ERROR: {e}\n{traceback.format_exc()}")

# --- MQ3 ---
try:
    from sensors.mq3 import MQ3
    ch = int(os.getenv('MQ3_ADC_CHANNEL', '0'))
    mq3 = MQ3(channel=ch)
    print(f"[MQ3] ADC Channel: {ch}")
    val = mq3.read_alcohol_level()
    print(f"  [OK] Alcohol level: {val:.2f} (raw or mg/L)")
except Exception as e:
    print(f"[MQ3] ERROR: {e}\n{traceback.format_exc()}")

print("\n=== SENSOR SELF-TEST COMPLETE ===\n")
