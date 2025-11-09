#!/usr/bin/env bash
set -euo pipefail

# Creates a virtualenv in .venv and installs Python dependencies from requirements.txt
# Usage: ./setup_env.sh

PY=python3
VENV_DIR=".venv"

if ! command -v "$PY" >/dev/null 2>&1; then
  echo "Error: $PY not found. Please install Python 3.8+ and retry." >&2
  exit 2
fi

echo "Creating virtual environment in $VENV_DIR..."
$PY -m venv "$VENV_DIR"

# shellcheck source=/dev/null
source "$VENV_DIR/bin/activate"

echo "Upgrading pip, setuptools, wheel..."
python -m pip install --upgrade pip setuptools wheel

if [ ! -f requirements.txt ]; then
  echo "Warning: requirements.txt not found in repository root. Skipping pip install." >&2
else
  echo "Installing Python packages from requirements.txt (this may take several minutes)..."
  "$VENV_DIR/bin/python" -m pip install -r requirements.txt
fi

cat <<'EOF'
Setup complete.
- Activate the virtualenv with: source .venv/bin/activate
- Run the app with: ./run.sh (after making it executable)

Note: Some packages (audio, pigpio, DHT, spidev, etc.) require system packages or hardware-specific setup.
See README_RUN.md for platform-specific instructions.
EOF
