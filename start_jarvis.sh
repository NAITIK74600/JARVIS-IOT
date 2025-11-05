#!/bin/bash
# Navigate to the script's directory (your jarvis folder)
cd "$(dirname "$0")"

# Activate the virtual environment
source jarvis-env/bin/activate

# Run the main Python script with sudo for GPIO access
sudo python main.py
