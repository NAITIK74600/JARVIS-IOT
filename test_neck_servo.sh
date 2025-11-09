#!/bin/bash
# Neck Servo Test Script
# Properly sets up Python environment and runs neck control

cd "$(dirname "$0")"

# Start pigpiod if not running
if ! pgrep -x "pigpiod" > /dev/null; then
    echo "Starting pigpio daemon..."
    sudo pigpiod
    sleep 1
fi

# Activate virtual environment
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found. Run ./setup_env.sh first."
    exit 1
fi

source .venv/bin/activate

# Set PYTHONPATH to current directory
export PYTHONPATH="$(pwd)"

# Run neck control script
echo "Starting neck servo control..."
python -c "
import sys
sys.path.insert(0, '$(pwd)')

from actuators.multi_servo_controller import multi_servo_controller
import time

print('='*60)
print('NECK SERVO QUICK TEST')
print('='*60)

# Get neck servo
neck = multi_servo_controller.get_servo('neck')

if not neck:
    print('❌ ERROR: Neck servo not found!')
    print('Check if pigpiod is running: sudo systemctl status pigpiod')
    sys.exit(1)

print(f'✓ Neck Servo Found: GPIO 18 (BCM)')
print(f'Current Position: {neck.current_angle if neck.current_angle else \"Unknown\"}°')
print()

# Test sequence
print('Running test sequence:')
print('  1. Center (90°)')
print('  2. Left (45°)')
print('  3. Right (135°)')
print('  4. Center (90°)')
print()

positions = [(90, 'Center'), (45, 'Left'), (135, 'Right'), (90, 'Center')]

for angle, label in positions:
    print(f'Moving to {label} ({angle}°)...', end=' ')
    neck.set_angle(angle)
    time.sleep(1)
    print(f'✓ Current angle: {neck.current_angle}°')

print()
print('='*60)
print('✓ Neck servo test complete!')
print('='*60)
"
