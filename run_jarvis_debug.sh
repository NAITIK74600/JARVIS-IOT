#!/bin/bash
# Debug startup script for JARVIS
# This will show all errors and keep the window open

cd "$(dirname "$0")"

echo "════════════════════════════════════════════════════════"
echo "  Starting JARVIS in Debug Mode"
echo "════════════════════════════════════════════════════════"
echo ""

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "   Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "✓ Activating virtual environment..."
source .venv/bin/activate

# Check if pigpiod is running
echo "✓ Checking pigpiod daemon..."
if ! pgrep -x "pigpiod" > /dev/null; then
    echo "  Starting pigpiod..."
    sudo pigpiod
    sleep 1
fi

# Allow X11 access for sudo
echo "✓ Setting up display permissions..."
xhost +local:root > /dev/null 2>&1

# Start JARVIS with proper environment
echo "✓ Launching JARVIS..."
echo ""
echo "════════════════════════════════════════════════════════"
echo ""

# Run with sudo, preserve DISPLAY environment
sudo -E DISPLAY=:0 PYTHONUNBUFFERED=1 .venv/bin/python main.py

echo ""
echo "════════════════════════════════════════════════════════"
echo "  JARVIS has stopped"
echo "════════════════════════════════════════════════════════"
