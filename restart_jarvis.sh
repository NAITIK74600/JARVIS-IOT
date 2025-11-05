#!/bin/bash
# Quick restart script for Jarvis

echo "🔄 Restarting Jarvis..."

# Kill any existing Jarvis processes
pkill -f "python.*main.py" 2>/dev/null
sleep 1

# Start Jarvis
cd /home/naitik/jarvis
./jarvis-env/bin/python main.py

echo "✅ Jarvis started!"
