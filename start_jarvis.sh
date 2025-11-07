#!/bin/bash
# Navigate to the script's directory (your jarvis folder)
cd "$(dirname "$0")"

# Activate the virtual environment
source .venv/bin/activate

# Run the main Python script with sudo for GPIO access, preserving environment
sudo -E DISPLAY=:0 PYTHONUNBUFFERED=1 .venv/bin/python main.py
