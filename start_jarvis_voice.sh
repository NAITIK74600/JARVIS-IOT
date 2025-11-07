#!/bin/bash
# Start JARVIS with voice input/output support
# This script handles permissions properly for both GPIO and audio

cd /home/naitik/JARVIS-IOT

# Add user to required groups if not already
sudo usermod -a -G gpio,i2c,spi $(whoami) 2>/dev/null

# Set GPIO permissions without requiring sudo
sudo chmod 666 /dev/gpiomem 2>/dev/null
sudo chmod 666 /dev/i2c-* 2>/dev/null

# Start pigpio daemon if not running
if ! pgrep -x "pigpiod" > /dev/null; then
    echo "Starting pigpio daemon..."
    sudo pigpiod
    sleep 1
fi

# Run JARVIS as regular user (not sudo) to access audio properly
echo "Starting J.A.R.V.I.S. with voice support..."
DISPLAY=:0 .venv/bin/python main.py
