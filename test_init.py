#!/usr/bin/env python3
"""Minimal test to check if Jarvis core initializes without UI."""

import sys
import os
from queue import Queue
import time
import traceback

# Ensure imports work
sys.path.insert(0, os.getcwd())

print("=" * 60)
print("JARVIS CORE INITIALIZATION TEST")
print("=" * 60)

ui_queue = Queue()
user_input_queue = Queue()

# Import the initialization function
try:
    from main import init_and_run_jarvis_core
    print("✓ Import successful")
except Exception as e:
    print(f"✗ Import failed: {e}")
    traceback.print_exc()
    sys.exit(1)

# Start the core in a thread
import threading
thread = threading.Thread(
    target=init_and_run_jarvis_core,
    args=(ui_queue, user_input_queue),
    daemon=True
)

print("\nStarting Jarvis core thread...")
thread.start()

# Wait for initialization
print("Waiting for initialization (8 seconds)...")
time.sleep(8)

# Check the queue for messages
print("\n" + "=" * 60)
print("CHECKING INITIALIZATION RESULTS")
print("=" * 60)

messages = []
while not ui_queue.empty():
    messages.append(ui_queue.get())

# Analyze messages
logs = [(msg_type, payload) for msg_type, payload in messages if msg_type == "log"]
statuses = [payload for msg_type, payload in messages if msg_type == "status"]
exit_signals = [(msg_type, payload) for msg_type, payload in messages if msg_type == "exit"]

print(f"\nTotal messages: {len(messages)}")
print(f"Log messages: {len(logs)}")
print(f"Status updates: {len(statuses)}")
print(f"Exit signals: {len(exit_signals)}")

# Check for key indicators
online_msg = any("online" in log[1].get('msg', '').lower() for log in logs)
error_msg = any("error" in log[1].get('msg', '').lower() or "failed" in log[1].get('msg', '').lower() for log in logs)

print(f"\nThread alive: {thread.is_alive()}")
print(f"Found 'online' message: {online_msg}")
print(f"Found error messages: {error_msg}")

# Print last few log messages
print("\n" + "-" * 60)
print("LAST 15 LOG MESSAGES:")
print("-" * 60)
for i, (msg_type, payload) in enumerate(messages[-15:]):
    if msg_type == "log":
        msg = payload.get('msg', '').strip()
        tag = payload.get('tag', '')
        if msg:
            print(f"[{tag or 'LOG'}] {msg}")
    elif msg_type == "status":
        print(f"[STATUS] {payload}")
    elif msg_type == "exit":
        print("[EXIT SIGNAL]")

# Print last status
if statuses:
    print("\n" + "-" * 60)
    print(f"LAST STATUS: {statuses[-1]}")
    print("-" * 60)

# Final verdict
print("\n" + "=" * 60)
if thread.is_alive() and online_msg and not exit_signals:
    print("✓ SUCCESS: Jarvis core initialized and running!")
elif exit_signals:
    print("✗ FAILURE: Exit signal sent (thread terminated)")
elif error_msg:
    print("✗ FAILURE: Errors detected during initialization")
elif not thread.is_alive():
    print("✗ FAILURE: Thread died")
else:
    print("? UNKNOWN: Thread alive but no 'online' message")
print("=" * 60)
