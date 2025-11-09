#!/usr/bin/env bash
set -euo pipefail

# Activates the virtualenv (created by setup_env.sh) and runs main.py
VENV_DIR=".venv"

if [ ! -d "$VENV_DIR" ]; then
  echo "Virtualenv not found. Run ./setup_env.sh first." >&2
  exit 3
fi

# Start pigpiod if not running
if ! pgrep -x "pigpiod" > /dev/null; then
    echo "Starting pigpio daemon..."
    sudo pigpiod
    sleep 1
fi

# shellcheck source=/dev/null
source "$VENV_DIR/bin/activate"

# Enable MQ-3 alcohol sensor
export MQ3_ENABLED=true

echo "Running JARVIS (main.py) in virtualenv..."
python main.py
