#!/usr/bin/env python3
"""
Test voice recognition with actual callback to see if JARVIS responds
"""
import sys
import os
import time
import threading

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.voice_engine import VoiceEngine

print("=" * 60)
print("JARVIS VOICE RECOGNITION TEST")
print("=" * 60)
print()

# Track what we receive
recognized_phrases = []
callback_called = False

def my_callback(text):
    """Callback when speech is recognized"""
    global callback_called, recognized_phrases
    callback_called = True
    recognized_phrases.append(text)
    print(f"\n✓ CALLBACK RECEIVED: '{text}'")
    print(f"  Total phrases: {len(recognized_phrases)}")
    return True  # Process the input

# Initialize voice engine
print("1. Initializing Voice Engine...")
voice = VoiceEngine(
    wake_word=None,  # No wake word (continuous listening)
    transcript_callback=my_callback
)

print("2. Starting voice recognition...")
voice.start()

print()
print("=" * 60)
print("SYSTEM READY - Speak now!")
print("=" * 60)
print("Test phrases:")
print("  - 'hello jarvis'")
print("  - 'what time is it'")
print("  - 'scan room'")
print("  - 'hello'")
print()
print("Listening for 30 seconds...")
print("-" * 60)

# Listen for 30 seconds
start_time = time.time()
last_count = 0

while time.time() - start_time < 30:
    time.sleep(1)
    elapsed = int(time.time() - start_time)
    
    # Show progress every 5 seconds
    if elapsed % 5 == 0 and elapsed > 0:
        print(f"[{elapsed}s] Still listening... (Recognized: {len(recognized_phrases)})")
    
    # Show new recognitions immediately
    if len(recognized_phrases) > last_count:
        last_count = len(recognized_phrases)

print()
print("-" * 60)
print("RESULTS:")
print("-" * 60)
print(f"Callback called: {callback_called}")
print(f"Total phrases recognized: {len(recognized_phrases)}")

if recognized_phrases:
    print("\nRecognized phrases:")
    for i, phrase in enumerate(recognized_phrases, 1):
        print(f"  {i}. '{phrase}'")
    print("\n✓ VOICE RECOGNITION IS WORKING!")
else:
    print("\n✗ NO PHRASES RECOGNIZED")
    print("\nPossible issues:")
    print("  1. Microphone not picking up sound (speak louder)")
    print("  2. Recognition threshold too high")
    print("  3. Callback not being called")
    print("  4. Audio levels too low")

print()
print("Stopping voice engine...")
voice.stop()
print("Done.")
