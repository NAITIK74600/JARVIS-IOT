"""sensor_tools.py

Minimal tool wrappers for quick sensor access expected by main.py.
These functions are optional convenience layers; main.py already has direct
SensorManager usage but attempts to import this module for fast-path checks.
"""
from langchain.agents import tool

# Global reference to sensor manager, set by main.py
_sensor_manager = None

def set_sensor_manager(manager):
    """Set the global sensor manager reference. Called by main.py"""
    global _sensor_manager
    _sensor_manager = manager

def _get_manager():
    """Get the sensor manager instance"""
    return _sensor_manager

@tool
def check_distance(_: str = "") -> str:
    """Return current distance in cm from ultrasonic sensor."""
    mgr = _get_manager()
    if not mgr:
        return "Distance sensor unavailable."
    try:
        d = mgr.get_distance()
        if d is None:
            return "Distance read failed."
        return f"Distance {d:.1f} cm"
    except Exception as e:
        return f"Distance error: {e}"

@tool
def check_pir_motion(_: str = "") -> str:
    """Report last motion detection age (seconds) or none."""
    mgr = _get_manager()
    if not mgr:
        return "PIR sensor unavailable."
    ts = mgr.pir_sensor.last_motion_time if mgr.pir_sensor else None
    if not ts:
        return "No motion detected yet."
    import time
    age = time.time() - ts
    return f"Last motion {age:.0f}s ago"

@tool
def check_alcohol(_: str = "") -> str:
    """Check if alcohol is detected by the MQ-3 sensor."""
    mgr = _get_manager()
    if not mgr:
        return "Alcohol sensor unavailable."
    if not mgr.mq3_sensor:
        return "MQ-3 sensor not enabled. Set MQ3_ENABLED=true to enable."
    try:
        detected = mgr.get_alcohol_level()
        if detected is None:
            return "Alcohol sensor read failed."
        if detected:
            return "⚠️ ALCOHOL DETECTED! The MQ-3 sensor has detected alcohol vapors."
        else:
            return "✓ No alcohol detected. Air quality is normal."
    except Exception as e:
        return f"Alcohol sensor error: {e}"

@tool
def get_alcohol_status(_: str = "") -> str:
    """Get the current alcohol detection status (yes/no)."""
    mgr = _get_manager()
    if not mgr:
        return "unavailable"
    if not mgr.mq3_sensor:
        return "disabled"
    try:
        detected = mgr.get_alcohol_level()
        if detected is None:
            return "error"
        return "detected" if detected else "clear"
    except Exception:
        return "error"

# Export all sensor tools
all_sensor_tools = [
    check_distance,
    check_pir_motion,
    check_alcohol,
    get_alcohol_status,
]

