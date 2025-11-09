#!/bin/bash
# Quick restart script for Jarvis

echo "🔄 Restarting Jarvis..."

# Kill any existing Jarvis processes
pkill -f "python.*main.py" 2>/dev/null
sleep 1

# Start Jarvis
cd "$(dirname "$0")"
./start_jarvis.sh

echo "✅ Jarvis started!"
