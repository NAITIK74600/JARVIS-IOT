#!/bin/bash
# Simple voice test script - Tests complete JARVIS voice system

echo "======================================================================"
echo "JARVIS VOICE SYSTEM TEST"
echo "======================================================================"
echo ""
echo "This will test the complete voice pipeline:"
echo "  1. Microphone input"
echo "  2. Speech recognition"  
echo "  3. Command processing"
echo "  4. TTS response"
echo ""
echo "Current settings:"
echo "  • Bluetooth microphone @ 150% volume"
echo "  • Input gain: 2.0x (double boost)"
echo "  • Noise threshold: 200"
echo "  • TTS: Google (25% faster)"
echo ""
echo "======================================================================"
echo ""
echo "Starting test in 3 seconds..."
sleep 3

cd /home/naitik/JARVIS-IOT
source .venv/bin/activate

# Run the full test
python test_full_jarvis_voice.py

echo ""
echo "======================================================================"
echo "Test complete!"
echo ""
echo "If you saw recognitions and responses, system is working ✅"
echo "If only recognitions but no responses, check for processing errors ⚠️"
echo "If no recognitions at all, speak louder or closer to microphone 📢"
echo "======================================================================"
