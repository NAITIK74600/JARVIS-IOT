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
        return "I'm afraid the distance sensor is not available, Sir."
    try:
        d = mgr.get_distance()
        if d is None or d < 0:
            return "Unable to read distance, Sir. The sensor may be blocked or out of range."
        if d < 10:
            return f"Very close, Sir. Only {d:.1f} centimeters."
        elif d < 50:
            return f"Distance is {d:.1f} centimeters, Sir."
        else:
            return f"Object detected at {d:.1f} centimeters, Sir."
    except Exception as e:
        return f"Distance sensor error, Sir: {e}"

@tool
def check_pir_motion(_: str = "") -> str:
    """Report last motion detection age (seconds) or none."""
    mgr = _get_manager()
    if not mgr:
        return "I'm afraid the motion sensor is not available, Sir."
    ts = mgr.pir_sensor.last_motion_time if mgr.pir_sensor else None
    if not ts:
        return "No motion detected yet, Sir."
    import time
    age = time.time() - ts
    if age < 5:
        return f"Motion detected just {age:.0f} seconds ago, Sir."
    elif age < 60:
        return f"Last motion detected {age:.0f} seconds ago, Sir."
    else:
        minutes = age / 60
        return f"Last motion was {minutes:.1f} minutes ago, Sir."

@tool
def check_alcohol(_: str = "") -> str:
    """Check if alcohol is detected by the MQ-3 sensor."""
    mgr = _get_manager()
    if not mgr:
        return "I'm afraid the alcohol sensor system is not available, Sir."
    if not mgr.mq3_sensor:
        return "The MQ-3 sensor is not enabled, Sir. It needs to be activated in the system configuration."
    try:
        detected = mgr.get_alcohol_level()
        if detected is None:
            return "Unable to read the alcohol sensor, Sir. There may be a hardware issue."
        if detected:
            return "Alert, Sir. Alcohol vapors have been detected in the environment."
        else:
            return "No alcohol detected, Sir. Air quality is normal."
    except Exception as e:
        return f"Alcohol sensor malfunction, Sir: {e}"

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

@tool
def get_environment_readings(_: str = "") -> str:
    """Get temperature and humidity from DHT11 sensor."""
    mgr = _get_manager()
    if not mgr:
        return "I'm afraid the environmental sensors are not available, Sir."
    if not mgr.dht_sensor:
        return "The DHT11 temperature and humidity sensor is not available, Sir."
    try:
        temp = mgr.get_temperature()
        humidity = mgr.get_humidity()
        if temp is None or humidity is None:
            return "Unable to read environmental data, Sir. The sensor may need a moment to warm up."
        return f"Current temperature is {temp:.1f} degrees Celsius with {humidity:.1f}% humidity, Sir."
    except Exception as e:
        return f"Environmental sensor error, Sir: {e}"

@tool
def get_all_sensor_readings(_: str = "") -> str:
    """Get readings from all available sensors."""
    mgr = _get_manager()
    if not mgr:
        return "I'm afraid the sensor system is not initialized, Sir."
    
    try:
        readings = mgr.get_all_readings()
        parts = []
        
        # Temperature and humidity
        if readings.get('temperature_c') is not None and readings.get('humidity_percent') is not None:
            parts.append(f"Temperature: {readings['temperature_c']:.1f}°C, Humidity: {readings['humidity_percent']:.1f}%")
        else:
            parts.append("Temperature/Humidity: Not available")
        
        # Distance
        dist = readings.get('distance_cm')
        if dist is not None and dist >= 0:
            parts.append(f"Distance: {dist:.1f} cm")
        else:
            parts.append("Distance: No reading")
        
        # Alcohol
        alcohol = readings.get('alcohol_detected')
        if alcohol is not None:
            parts.append(f"Alcohol: {'Detected' if alcohol else 'Clear'}")
        else:
            parts.append("Alcohol: Sensor disabled")
        
        # Motion
        motion_time = readings.get('last_motion_timestamp')
        if motion_time:
            import time
            age = time.time() - motion_time
            if age < 10:
                parts.append(f"Motion: Detected {age:.0f}s ago")
            else:
                parts.append(f"Motion: {age:.0f}s ago")
        else:
            parts.append("Motion: None detected")
        
        return "Sensor readings, Sir: " + " | ".join(parts)
    except Exception as e:
        return f"Error reading sensors, Sir: {e}"

# Export all sensor tools
all_sensor_tools = [
    check_distance,
    check_pir_motion,
    check_alcohol,
    get_alcohol_status,
    get_environment_readings,
    get_all_sensor_readings,
]

