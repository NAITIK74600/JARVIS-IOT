#!/usr/bin/env python3
"""Quick test of main.py initialization and shutdown without GUI interaction."""

import subprocess
import sys
import time
import signal

print("Testing main.py with automatic shutdown after 8 seconds...")
print("=" * 60)

# Start main.py
proc = subprocess.Popen(
    ['/home/naitik/jarvis/jarvis-env/bin/python', '/home/naitik/jarvis/main.py'],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1
)

# Let it run for 8 seconds to initialize
print("Waiting 8 seconds for initialization...")
time.sleep(8)

# Send SIGTERM for graceful shutdown
print("\nSending SIGTERM for graceful shutdown...")
proc.send_signal(signal.SIGTERM)

# Wait for it to exit
try:
    stdout, _ = proc.communicate(timeout=10)
    exit_code = proc.returncode
    
    print("\n" + "=" * 60)
    print("STDOUT/STDERR OUTPUT:")
    print("=" * 60)
    print(stdout)
    print("=" * 60)
    
    if exit_code == 139:
        print("\n❌ SEGMENTATION FAULT DETECTED (exit code 139)")
        sys.exit(1)
    elif exit_code == -signal.SIGTERM:
        print(f"\n✓ Process terminated by SIGTERM (expected)")
        sys.exit(0)
    elif exit_code == 0:
        print(f"\n✓ Process exited cleanly (exit code 0)")
        sys.exit(0)
    else:
        print(f"\n⚠ Process exited with code {exit_code}")
        sys.exit(exit_code if exit_code else 0)
        
except subprocess.TimeoutExpired:
    print("\n⚠ Process didn't exit in time, killing it...")
    proc.kill()
    stdout, _ = proc.communicate()
    print(stdout)
    sys.exit(1)
