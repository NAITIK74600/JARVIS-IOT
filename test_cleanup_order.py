#!/usr/bin/env python3
"""Test main.py with proper shutdown sequence capture."""

import subprocess
import sys
import time
import signal

print("Testing main.py cleanup sequence...")
print("=" * 70)

# Start main.py
proc = subprocess.Popen(
    ['/home/naitik/jarvis/jarvis-env/bin/python', '/home/naitik/jarvis/main.py'],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1
)

# Let it run for 6 seconds to initialize
print("Waiting 6 seconds for initialization...")
time.sleep(6)

# Send SIGTERM for graceful shutdown
print("Sending SIGTERM for graceful shutdown...")
proc.send_signal(signal.SIGTERM)

# Wait for it to exit
try:
    stdout, _ = proc.communicate(timeout=10)
    exit_code = proc.returncode
    
    print("\n" + "=" * 70)
    print("CLEANUP SEQUENCE (last 50 lines):")
    print("=" * 70)
    lines = stdout.split('\n')
    for line in lines[-50:]:
        if line.strip():
            print(line)
    print("=" * 70)
    
    # Check order
    cleanup_lines = [l for l in lines if 'cleaned up' in l.lower() or 'cleanup' in l.lower()]
    
    print("\nCLEANUP ORDER:")
    print("-" * 70)
    for i, line in enumerate(cleanup_lines[-15:], 1):
        print(f"{i}. {line.strip()}")
    print("-" * 70)
    
    if exit_code == 139:
        print("\n❌ SEGMENTATION FAULT DETECTED (exit code 139)")
        sys.exit(1)
    elif exit_code == -signal.SIGTERM or exit_code == 143:
        print(f"\n✓ Process terminated cleanly (exit code {exit_code})")
        
        # Check if GPIO cleanup happened before servo cleanup
        gpio_cleanup_line = None
        servo_cleanup_line = None
        
        for i, line in enumerate(lines):
            if 'GPIO cleanup complete' in line or 'Hardware manager (GPIO) cleaned up' in line:
                gpio_cleanup_line = i
            if 'Shared pigpio connection closed' in line:
                servo_cleanup_line = i
        
        if gpio_cleanup_line and servo_cleanup_line:
            if gpio_cleanup_line < servo_cleanup_line:
                print(f"❌ WRONG ORDER: GPIO cleanup (line {gpio_cleanup_line}) before servos (line {servo_cleanup_line})")
                print("   This can cause segfault!")
                sys.exit(1)
            else:
                print(f"✓ CORRECT ORDER: Servos cleanup (line {servo_cleanup_line}) before GPIO (line {gpio_cleanup_line})")
        
        sys.exit(0)
    else:
        print(f"\n⚠ Process exited with code {exit_code}")
        sys.exit(exit_code if exit_code else 0)
        
except subprocess.TimeoutExpired:
    print("\n⚠ Process didn't exit in time, killing it...")
    proc.kill()
    stdout, _ = proc.communicate()
    print(stdout[-1000:])
    sys.exit(1)
