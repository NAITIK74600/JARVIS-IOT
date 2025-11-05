#!/bin/bash
# Safe Jarvis startup script with proper error handling

JARVIS_DIR="/home/naitik/jarvis"
PYTHON="$JARVIS_DIR/jarvis-env/bin/python"
MAIN_PY="$JARVIS_DIR/main.py"

echo "=============================================="
echo "  Starting J.A.R.V.I.S. (Segfault-Free)"
echo "=============================================="
echo ""

# Check if virtual environment exists
if [ ! -f "$PYTHON" ]; then
    echo "❌ Error: Virtual environment not found!"
    echo "   Expected: $PYTHON"
    exit 1
fi

# Check if main.py exists
if [ ! -f "$MAIN_PY" ]; then
    echo "❌ Error: main.py not found!"
    echo "   Expected: $MAIN_PY"
    exit 1
fi

# Check if pigpiod is running
if ! pgrep -x "pigpiod" > /dev/null; then
    echo "⚠️  Warning: pigpiod not running!"
    echo "   Starting pigpiod..."
    sudo systemctl start pigpiod
    sleep 1
fi

# Run Jarvis
echo "✓ All checks passed"
echo "✓ Starting Jarvis..."
echo ""

cd "$JARVIS_DIR"
exec "$PYTHON" "$MAIN_PY"
