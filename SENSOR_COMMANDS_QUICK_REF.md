# 🎯 JARVIS Sensor Commands - Quick Reference

## ✅ Optimization Complete!

All sensor-related commands have been optimized for better detection and response.

---

## 📡 Available Sensors

1. **DHT11** - Temperature & Humidity
2. **HC-SR04** - Ultrasonic Distance Sensor
3. **MQ-3** - Alcohol Detector (Digital)
4. **PIR** - Motion Detector

---

## 🗣️ Voice Commands (English)

### Temperature & Humidity
- "What's the temperature?"
- "Check temperature"
- "What's the humidity?"
- "How's the weather inside?"

### Distance Measurement
- "How far is the wall?"
- "Check distance"
- "Measure distance"
- "What's the ultrasonic reading?"

### Motion Detection
- "Is there any motion?"
- "Detect movement"
- "Check for motion"
- "Is someone there?"

### Alcohol Detection
- "Is there alcohol?"
- "Check for alcohol"
- "Detect alcohol"
- "Any alcohol detected?"

### All Sensors
- "Check all sensors"
- "Sensor status"
- "Give me sensor readings"
- "What are the sensor values?"

---

## 🗣️ Voice Commands (Hinglish)

### Temperature & Humidity
- "temperature batao"
- "mausam kaisa hai"
- "humidity check karo"

### Distance Measurement
- "kitni duri hai"
- "distance batao"
- "wall kitni door hai"

### Motion Detection
- "koi movement hai"
- "motion detect karo"
- "koi hai kya"

### Alcohol Detection
- "alcohol detect karo"
- "alcohol hai kya"

### All Sensors
- "saare sensor check karo"
- "sensor ki reading batao"

---

## 🧪 Testing

Run the test script to verify everything is working:

```bash
cd ~/JARVIS-IOT
python test_sensor_commands.py
```

This will test all command variations and show which ones are properly detected.

---

## 🔧 Technical Details

### Changes Made (commit: 43bdd11)
1. ✅ Added distance sensor detection keywords
2. ✅ Added motion sensor detection keywords  
3. ✅ Enhanced temperature/humidity detection
4. ✅ Improved alcohol detection with more variations
5. ✅ Better handling of "check all sensors" commands

### Files Modified
- `core/offline_responder.py` - Enhanced keyword matching

### How It Works
```
Voice Input → Speech Recognition
    ↓
Keyword Detection (offline_responder.py)
    ↓
Tool Selection (sensor_tools.py)
    ↓
Hardware Reading (sensor_manager.py)
    ↓
Response to User
```

---

## 📊 Success Indicators

✅ **Working Correctly:**
- JARVIS responds to sensor queries without saying "I don't understand"
- Natural language variations are recognized (e.g., "how far" vs "check distance")
- Both English and Hinglish commands work
- Responses include actual sensor data (temperature, distance, yes/no)

❌ **Issues:**
- "I don't understand" for sensor commands → Run test script to debug
- Switching to offline mode unexpectedly → Check mode_optimizer.py keywords
- No sensor data in response → Check if sensors are enabled and connected

---

## 🚀 Quick Start Testing

1. **Start JARVIS:**
   ```bash
   cd ~/JARVIS-IOT
   ./run.sh
   ```

2. **Try these commands in order:**
   - "Check all sensors" (should read all 4 sensors)
   - "What's the temperature?" (should give temp + humidity)
   - "How far is the wall?" (should give distance in cm)
   - "Is there motion?" (should say yes/no)
   - "Check for alcohol" (should say yes/no)

3. **Hinglish test:**
   - "temperature batao"
   - "kitni duri hai"
   - "koi movement hai"

---

## 📝 Notes

- All sensors must be properly connected and enabled
- MQ-3 is auto-enabled in run.sh (added in commit 27526c1)
- Voice recognition uses Dynamic Noise Gate for better accuracy
- Commands work in both online (Gemini AI) and offline modes
- Mode optimizer ensures sensor commands don't cause unnecessary mode switching

---

## 🐛 Troubleshooting

**Problem:** "I don't understand" for sensor commands
- **Solution:** Check if the command includes a keyword from the list above
- Run `python test_sensor_commands.py` to see detection results

**Problem:** No sensor data returned
- **Solution:** Check sensor connections and run individual sensor tests:
  ```bash
  python sensors/ultrasonic_test.py
  python sensors/mq3_test.py
  python tools/neck_control.py  # For servo check
  ```

**Problem:** Always switching to offline mode
- **Solution:** This was fixed! Broad keywords removed from mode_optimizer.py
- Only specific phrases like "check sensor" trigger offline mode now

---

## 📖 More Documentation

- Full optimization details: `SENSOR_COMMAND_OPTIMIZATION.md`
- MQ-3 setup guide: `docs/MQ3_ALCOHOL_SENSOR_SETUP.md`
- Voice recognition fixes: `VOICE_RECOGNITION_FIXES.txt`
- Pin reference: `PIN_REFERENCE_CARD.txt`

---

**Last Updated:** Today (commits: 43bdd11, d2462cb)
**Status:** ✅ All sensor commands optimized and tested
