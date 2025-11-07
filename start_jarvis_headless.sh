#!/bin/bash
# Start JARVIS in Headless Mode (No GUI)
# Use this for SSH access or when running without display

cd /home/naitik/JARVIS-IOT
source .venv/bin/activate

echo "========================================"
echo "Starting JARVIS (Headless Mode)..."
echo "========================================"

python jarvis_headless.py
