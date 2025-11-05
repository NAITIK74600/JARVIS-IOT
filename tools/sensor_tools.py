"""robot_tools.py

Minimal tool wrappers for quick sensor access expected by main.py.
These functions are optional convenience layers; main.py already has direct
SensorManager usage but attempts to import this module for fast-path checks.
"""
from langchain.agents import tool

# The actual SensorManager instance lives in main.py. We lazily import there.
# These wrappers accept an optional empty string so they can be invoked as LangChain tools.

def _get_manager():
    try:
        # Late import to avoid circular dependency
        from sensors.sensor_manager import SensorManager  # noqa: F401
        from main import sensor_manager  # type: ignore
        return sensor_manager
    except Exception:
        return None

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
