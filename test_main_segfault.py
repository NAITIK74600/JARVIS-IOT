#!/usr/bin/env python3
"""Test main.py startup and check for clean initialization (no segfault on exit)."""

import subprocess
import sys
import time

print("Testing main.py - will run for 5 seconds then kill...")
print("Looking for segmentation fault on exit...")
print("=" * 60)

proc = subprocess.Popen(
    ['/home/naitik/jarvis/jarvis-env/bin/python', '/home/naitik/jarvis/main.py'],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True
)

# Wait 5 seconds
time.sleep(5)

# Kill the process
print("Killing process...")
proc.kill()
stdout, _ = proc.communicate()

print("\n" + "=" * 60)
print("OUTPUT (last 100 lines):")
print("=" * 60)
lines = stdout.split('\n')
for line in lines[-100:]:
    print(line)
print("=" * 60)

# Check for segfault
exit_code = proc.returncode
print(f"\nExit code: {exit_code}")

if "Segmentation fault" in stdout or exit_code == 139:
    print("\n❌ SEGMENTATION FAULT DETECTED!")
    sys.exit(1)
else:
    print("\n✓ NO SEGMENTATION FAULT - Clean exit!")
    sys.exit(0)
