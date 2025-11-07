#!/bin/bash
# Start JARVIS Voice System (Minimal - No Hardware Dependencies)
# Use this when you want voice interaction without robot hardware

cd /home/naitik/JARVIS-IOT
source .venv/bin/activate

echo "========================================"
echo "Starting JARVIS Voice System..."
echo "========================================"

python test_voice_minimal.py
