#!/bin/bash
# Navigate to the script's directory (your jarvis folder)
cd "$(dirname "$0")"

# Fix Bluetooth microphone configuration
echo "🔧 Configuring Bluetooth microphone..."
./fix_bluetooth_mic.sh

# Activate the virtual environment
source .venv/bin/activate

# Enable sensors
export MQ3_ENABLED=true

# Run the main Python script with sudo for GPIO access, preserving environment
sudo -E DISPLAY=:0 PYTHONUNBUFFERED=1 .venv/bin/python main.py
