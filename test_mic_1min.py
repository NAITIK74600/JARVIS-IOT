#!/usr/bin/env python3
"""
1 Minute Microphone Detection Test
Tests microphone continuously for 60 seconds
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.voice_engine import VoiceEngine
import time

print("\n" + "="*70)
print("MICROPHONE TEST - 1 MINUTE")
print("="*70)

# Track recognized words
recognized_count = 0
last_recognition_time = time.time()

def on_speech_recognized(text):
    """Callback when speech is detected"""
    global recognized_count, last_recognition_time
    recognized_count += 1
    elapsed = int(time.time() - start_time)
    
    print(f"\n[{elapsed}s] 🎤 #{recognized_count}: '{text}'")
    last_recognition_time = time.time()

# Initialize voice engine
print("\nInitializing voice engine...")
voice = VoiceEngine(
    wake_word=None,  # No wake word - continuous listening
    transcript_callback=on_speech_recognized
)

print(f"\n✓ Voice Engine Ready")
print(f"  Microphone: Index {voice.microphone_index}")
print(f"  Backend: {voice.tts_backend}")

# Start listening
print("\n" + "="*70)
print("🎤 LISTENING FOR 60 SECONDS...")
print("="*70)
print("Speak anything - I will detect and show what I hear")
print("Try: hello, test, jarvis, scan karo, temperature, etc.\n")

voice.speak("Microphone test starting. Listening for one minute.")

voice.start()
start_time = time.time()

# Run for 60 seconds
try:
    while (time.time() - start_time) < 60:
        time.sleep(0.5)
        
        # Show status every 10 seconds
        elapsed = int(time.time() - start_time)
        if elapsed % 10 == 0 and elapsed > 0:
            time_since_last = int(time.time() - last_recognition_time)
            print(f"\n[{elapsed}s] Status: {recognized_count} phrases detected, last {time_since_last}s ago")
            
except KeyboardInterrupt:
    print("\n\n[!] Stopped by user")

# Stop
voice.stop()

# Results
print("\n" + "="*70)
print("TEST COMPLETE")
print("="*70)

total_time = int(time.time() - start_time)
print(f"\nDuration: {total_time} seconds")
print(f"Total Recognized: {recognized_count} phrases")

if recognized_count > 0:
    avg_time = total_time / recognized_count
    print(f"Average: 1 phrase every {avg_time:.1f} seconds")
    print(f"\n✅ MICROPHONE WORKING PERFECTLY!")
else:
    print(f"\n⚠️  No speech detected")
    print("Check:")
    print("  - Microphone volume/gain")
    print("  - Speaking clearly and loudly")
    print("  - Bluetooth microphone connection")

print("\n" + "="*70 + "\n")
