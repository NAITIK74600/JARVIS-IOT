"""scanner.py

Enhanced coordinated head (servo) + ultrasonic scanning to map nearby obstacles
and suggest safe heading. Supports multi-sample median filtering, environment
variable driven configuration, and raw sample introspection.

Environment Variables (optional):
    SCAN_START_ANGLE       (int, default 30)
    SCAN_END_ANGLE         (int, default 150)
    SCAN_STEP              (int, default 15)
    SCAN_SAMPLES_PER_ANGLE (int, default 3)  # median of N samples per angle
    SCAN_SETTLE            (float, default 0.18)  # settle time after movement
    SCAN_RETRIES           (int, default 2)  # retries for timeouts per measurement

Design Goals:
    - Backwards compatible: perform_scan() signature retained.
    - Minimal added latency: multi-sample logic optimized (short delays).
    - Robust to occasional ultrasonic timeouts (ignored unless all fail).
"""
from __future__ import annotations
import time
import math
from typing import List, Dict, Tuple, Optional, Iterable
import os

def _median(values: Iterable[float]) -> float:
    vals = sorted(values)
    if not vals:
        return -1
    mid = len(vals)//2
    if len(vals) % 2:
        return vals[mid]
    return (vals[mid-1] + vals[mid]) / 2.0

# Expect these to be provided by main application
# - servo: instance of actuators.servo.Servo
# - sensor_manager: instance of sensors.sensor_manager.SensorManager (for ultrasonic)

class ScanResult:
    def __init__(self, samples: List[Tuple[int, float]], raw: Dict[int, List[float]], meta: Dict):
        self.samples = samples  # list of (angle, distance_cm or -1 for error)
        self.raw = raw          # angle -> list of raw (possibly including -1 entries)
        self.meta = meta        # configuration used

    def to_dict(self) -> Dict:
        return {"samples": self.samples, "summary": self.summary(), "raw": self.raw, "meta": self.meta}

    def valid_samples(self):
        return [(a, d) for a, d in self.samples if d >= 0]

    def summary(self) -> Dict:
        valid = self.valid_samples()
        if not valid:
            return {"status": "no-data"}
        # Find max clearance angle
        best_angle, best_dist = max(valid, key=lambda t: t[1])
        avg = sum(d for _, d in valid)/len(valid)
        blocked = [a for a, d in valid if d < 20]
        return {
            "status": "ok",
            "best_angle": best_angle,
            "best_clearance_cm": round(best_dist,1),
            "average_distance_cm": round(avg,1),
            "blocked_angles": blocked,
            "sample_count": len(valid)
        }


def _load_env_int(name: str, default: int, low: int, high: int) -> int:
    try:
        v = int(os.getenv(name, str(default)))
        return max(low, min(high, v))
    except Exception:
        return default

def _load_env_float(name: str, default: float, low: float, high: float) -> float:
    try:
        v = float(os.getenv(name, str(default)))
        return max(low, min(high, v))
    except Exception:
        return default

def perform_scan(servo, sensor_manager, *, start_angle: Optional[int]=None, end_angle: Optional[int]=None,
                 step: Optional[int]=None, settle: Optional[float]=None, retries: Optional[int]=None,
                 samples_per_angle: Optional[int]=None) -> ScanResult:
    """Sweep servo between angles taking ultrasonic distance measurements (median filtered).

    Args: parameters override env if provided.
    Returns: ScanResult containing filtered and raw data.
    """
    if not servo or not sensor_manager:
        return ScanResult([], {}, {"error": "missing-hardware"})

    # Try to import display for real-time feedback
    try:
        from actuators.display import display
        has_display = True
    except:
        has_display = False
        display = None

    # Load config (override precedence: explicit arg > env > default)
    cfg = {
        'start_angle': start_angle if start_angle is not None else _load_env_int('SCAN_START_ANGLE', 30, 0, 180),
        'end_angle': end_angle if end_angle is not None else _load_env_int('SCAN_END_ANGLE', 150, 0, 180),
        'step': step if step is not None else _load_env_int('SCAN_STEP', 15, 1, 90),
        'settle': settle if settle is not None else _load_env_float('SCAN_SETTLE', 0.18, 0.05, 1.0),
        'retries': retries if retries is not None else _load_env_int('SCAN_RETRIES', 2, 0, 5),
        'samples_per_angle': samples_per_angle if samples_per_angle is not None else _load_env_int('SCAN_SAMPLES_PER_ANGLE', 3, 1, 9)
    }

    # Sanity adjust if reversed
    if cfg['start_angle'] > cfg['end_angle']:
        cfg['start_angle'], cfg['end_angle'] = cfg['end_angle'], cfg['start_angle']

    angles = list(range(cfg['start_angle'], cfg['end_angle'] + 1, cfg['step']))
    samples: List[Tuple[int, float]] = []
    raw_map: Dict[int, List[float]] = {}

    # Display: Show scanning start
    if has_display:
        display.clear()
        display.write_text("Scanning...", row=0, col=3)
        display.write_text(f"{cfg['start_angle']}-{cfg['end_angle']} deg", row=1, col=3)
        time.sleep(0.5)

    try:
        total_angles = len(angles)
        for idx, angle in enumerate(angles):
            servo.set_angle(angle)
            time.sleep(cfg['settle'])
            
            # Display: Show current angle
            if has_display:
                display.clear()
                display.write_text(f"Angle: {angle:3d}", row=0, col=3)
                progress = f"{idx+1}/{total_angles}"
                display.write_text(progress, row=1, col=5)
            
            raw_vals: List[float] = []
            for s in range(cfg['samples_per_angle']):
                dist = sensor_manager.get_distance()
                attempt = 0
                while dist < 0 and attempt < cfg['retries']:
                    time.sleep(0.04)
                    dist = sensor_manager.get_distance()
                    attempt += 1
                raw_vals.append(dist)
                # tiny delay between multi-samples to reduce crosstalk
                if s != cfg['samples_per_angle'] - 1:
                    time.sleep(0.03)
            
            # Filter: remove -1 (timeouts) then median; if all invalid => -1
            filtered_candidates = [v for v in raw_vals if v >= 0]
            value = _median(filtered_candidates) if filtered_candidates else -1
            raw_map[angle] = raw_vals
            samples.append((angle, value))
            
            # Display: Show distance at this angle
            if has_display and value >= 0:
                display.clear()
                display.write_text(f"{angle}deg: {int(value)}cm", row=0, col=2)
                display.write_text(progress, row=1, col=5)
                time.sleep(0.3)
                
    finally:
        mid = (cfg['start_angle'] + cfg['end_angle']) // 2
        servo.set_angle(mid)
    
    # Calculate summary for display
    result = ScanResult(samples, raw_map, cfg)
    summ = result.summary()
    
    # Display: Show scan results
    if has_display:
        display.clear()
        if summ.get("status") == "ok":
            best_angle = summ['best_angle']
            clearance = int(summ['best_clearance_cm'])
            display.write_text(f"Best: {best_angle}deg", row=0, col=2)
            display.write_text(f"Clear: {clearance}cm", row=1, col=2)
            time.sleep(2)
        else:
            display.write_text("Scan Failed", row=0, col=3)
            display.write_text("No Data", row=1, col=4)
            time.sleep(2)
    
    return result


def human_readable_summary(scan: ScanResult) -> str:
    summ = scan.summary()
    if summ.get("status") != "ok":
        return "I could not gather distance data, Sir."
    best_angle = summ['best_angle']
    clearance = summ['best_clearance_cm']
    avg = summ['average_distance_cm']
    blocked = summ['blocked_angles']
    if blocked:
        blocked_str = ', '.join(str(a) for a in blocked)
    else:
        blocked_str = 'none'
    return (
        f"Scan complete. Safest direction is around {best_angle} degrees with {clearance} centimeters clearance. "
        f"Average distance {avg} cm. Blocked ( <20cm ) angles: {blocked_str}."
    )

__all__ = ["perform_scan", "human_readable_summary", "ScanResult"]
