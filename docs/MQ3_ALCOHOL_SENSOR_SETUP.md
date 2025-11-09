# MQ-3 Alcohol Sensor Integration

## Overview
The MQ-3 alcohol sensor has been integrated into JARVIS to detect alcohol vapors in the environment using the digital output (D0) mode.

## Hardware Configuration
- **Sensor**: MQ-3 Alcohol Gas Sensor Module
- **GPIO Pin**: BCM 26 (Physical Pin 37)
- **Connection**: D0 pin of MQ-3 → GPIO 26 on Raspberry Pi
- **Mode**: Digital (threshold-based detection)

## Pin Configuration
```
MQ-3 Module    →    Raspberry Pi
VCC            →    5V
GND            →    GND
D0             →    GPIO 26 (BCM, Physical Pin 37)
```

## How It Works
The MQ-3 module has an onboard comparator and potentiometer that allows you to set a threshold. When the alcohol concentration exceeds this threshold, the D0 pin goes HIGH, otherwise it stays LOW.

### Adjusting Sensitivity
Use the blue potentiometer on the MQ-3 module:
- **Clockwise**: Less sensitive (higher threshold)
- **Counter-clockwise**: More sensitive (lower threshold)

## Enabling the Sensor
To enable the MQ-3 sensor in JARVIS, set the environment variable:
```bash
export MQ3_ENABLED=true
```

Or run JARVIS with:
```bash
MQ3_ENABLED=true bash run.sh
```

## Testing the Sensor
Run the standalone test script:
```bash
source .venv/bin/activate
python3 sensors/mq3_test.py
```

The test script will:
1. Warm up the sensor for 20 seconds
2. Continuously read and display the detection status
3. Show "Alcohol DETECTED!" when alcohol vapors are present
4. Show "No alcohol detected" when the air is clear

## Available Tools in JARVIS

### 1. `check_alcohol`
Checks if alcohol is currently detected by the sensor.

**Example usage**:
- "Check for alcohol"
- "Is there alcohol in the air?"
- "Detect alcohol"

**Returns**:
- "⚠️ ALCOHOL DETECTED! The MQ-3 sensor has detected alcohol vapors."
- "✓ No alcohol detected. Air quality is normal."

### 2. `get_alcohol_status`
Returns a simple status string (detected/clear/disabled/unavailable/error).

**Example usage**:
- "What's the alcohol status?"
- "Get alcohol sensor status"

**Returns**: One of: `detected`, `clear`, `disabled`, `unavailable`, `error`

## Code Files Modified

### 1. `sensors/mq3.py`
- Rewritten to use digital GPIO input instead of ADC
- Reads HIGH/LOW from D0 pin
- Returns boolean True/False for alcohol detection

### 2. `sensors/sensor_manager.py`
- Updated to initialize MQ-3 in digital mode
- Uses `MQ3_DIGITAL_PIN` environment variable (default: 26)
- `get_alcohol_level()` now returns boolean instead of analog value
- Updated `get_all_readings()` to include `alcohol_detected` field

### 3. `sensors/mq3_test.py` (NEW)
- Standalone test script for hardware verification
- Self-contained, doesn't require JARVIS core modules
- Shows real-time detection status

### 4. `tools/sensor_tools.py`
- Added `check_alcohol()` tool for JARVIS voice commands
- Added `get_alcohol_status()` for programmatic status checks
- Both tools integrate with the SensorManager

### 5. `main.py`
- Imported `all_sensor_tools` from `sensor_tools.py`
- Added sensor tools to the LLM agent's tool list
- JARVIS can now respond to alcohol-related queries

## Environment Variables
- `MQ3_ENABLED`: Set to `true` to enable the sensor (default: false)
- `MQ3_DIGITAL_PIN`: GPIO pin number in BCM mode (default: 26)

## Usage Examples

Once JARVIS is running with `MQ3_ENABLED=true`, you can ask:
- "Is there alcohol in the room?"
- "Check the alcohol sensor"
- "Detect any alcohol vapors"
- "What's the air quality?"

JARVIS will check the sensor and respond accordingly.

## Troubleshooting

### Sensor always shows "detected" or "not detected"
- Adjust the sensitivity potentiometer on the module
- Ensure the sensor has warmed up (20-30 seconds after power on)
- Check the wiring connections

### "MQ-3 sensor disabled" message
- Set `MQ3_ENABLED=true` in your environment
- Restart JARVIS after enabling

### Module import errors
- Use the standalone test script `sensors/mq3_test.py` for hardware testing
- Ensure GPIO permissions are set correctly

## Technical Notes
- The sensor needs 20-30 seconds to warm up after power on
- The heater element requires 5V power
- Response time: <2 seconds for detection
- Recovery time: ~30 seconds after alcohol is removed
- The analog output (A0) is not used in this configuration

## Safety Notice
This sensor is for detecting alcohol vapors in the air (e.g., from sanitizers, beverages, etc.). It is not a breathalyzer and should not be used for measuring blood alcohol content or making safety decisions about intoxication levels.
