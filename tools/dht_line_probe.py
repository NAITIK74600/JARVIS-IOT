"""dht_line_probe.py

Low-level probe for DHT11/DHT22 data line.
Objective: verify the sensor actually pulls the line low/high after the start signal.

Usage:
  export DHT_PIN=4   # BCM number (default 4 -> physical 7)
  python tools/dht_line_probe.py

Method:
  1. Configure pin with internal pull-up (if available) as output & drive low for >18ms (host start signal)
  2. Switch to input quickly
  3. Sample pin state at high frequency for ~5ms and record transitions with timestamps
  4. Report whether expected low->high->low handshake edges appeared.

Expected (simplified) for a valid sensor after host start:
  - Sensor pulls line low ~80us, then high ~80us (initial handshake) before sending bit pulses.
If no transitions (remains high), wiring/power/pull-up likely wrong or sensor dead.
If stuck low, data pin shorted or sensor holding line.

NOTE: This is a crude timing probe; Python timing is not microsecond-precise, but we should still see *some* edges if the sensor responds.
"""
import os, time, sys
import RPi.GPIO as GPIO

PIN = int(os.getenv('DHT_PIN', '4'))
print(f"[PROBE] Using BCM pin {PIN}")

GPIO.setmode(GPIO.BCM)

try:
    # Step 1: drive low >=18ms
    GPIO.setup(PIN, GPIO.OUT)
    GPIO.output(PIN, GPIO.LOW)
    time.sleep(0.02)  # 20ms

    # Step 2: release line (input with pull-up)
    GPIO.setup(PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    # Step 3: sample quickly
    samples = []
    start = time.perf_counter()
    duration = 0.006  # 6ms capture window
    last_state = GPIO.input(PIN)
    last_change_time = start
    samples.append((0.0, last_state))

    while (time.perf_counter() - start) < duration:
        s = GPIO.input(PIN)
        if s != last_state:
            t_rel = time.perf_counter() - start
            samples.append((t_rel, s))
            last_state = s
    end = time.perf_counter()

    # Analyze transitions
    lows = sum(1 for _, st in samples if st == 0)
    highs = sum(1 for _, st in samples if st == 1)

    print(f"[PROBE] Captured {len(samples)} state changes over {(end-start)*1000:.2f} ms")
    if len(samples) <= 1:
        print("[RESULT] No transitions detected. Line likely held HIGH the whole time.")
        print("[ADVICE] Re-check: data wire on correct BCM pin, 10K pull-up (or module resistor), sensor VCC=3.3V, GND common.")
    else:
        print("[TRANSITIONS]")
        for t_rel, st in samples:
            print(f"  t={t_rel*1e6:7.0f}us -> {'HIGH' if st else 'LOW'}")
        if lows and highs:
            print("[RESULT] Some transitions detected; sensor might be responding. Full driver should retry now.")
        else:
            print("[RESULT] Transitions incomplete; retest wiring.")
finally:
    GPIO.cleanup(PIN)
    print("[CLEANUP] Released pin.")
