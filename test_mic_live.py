#!/usr/bin/env python3
"""
Live Microphone Test with Audio Level Monitor
Shows real-time audio levels to help diagnose pickup issues
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.voice_engine import VoiceEngine
import time

print("\n" + "="*70)
print("LIVE MICROPHONE TEST - Audio Level Monitor")
print("="*70)

# Track recognized words
recognized_count = 0
start_time = time.time()

def on_speech_recognized(text):
    """Callback when speech is detected"""
    global recognized_count
    recognized_count += 1
    elapsed = int(time.time() - start_time)
    
    print(f"\n✅ [{elapsed}s] RECOGNIZED #{recognized_count}: '{text}'")
    print(f"   (Length: {len(text)} chars)")

# Initialize voice engine
print("\nInitializing voice engine with enhanced settings...")
voice = VoiceEngine(
    wake_word=None,
    transcript_callback=on_speech_recognized
)

print(f"\n📊 Voice Engine Configuration:")
print(f"  Microphone Index: {voice.microphone_index}")
print(f"  Input Gain: {voice.INPUT_GAIN}x (2x boost)")
print(f"  Noise Threshold: {voice.NOISE_THRESHOLD}")
print(f"  Chunk Size: {voice.CHUNK}")
print(f"  Sample Rate: {voice.RATE} Hz")

# Start listening
print("\n" + "="*70)
print("🎤 LISTENING NOW - Audio levels will show every 3 seconds")
print("="*70)
print("\nTips for best recognition:")
print("  • Speak clearly and at normal volume")
print("  • Keep microphone within 1-2 feet")
print("  • Watch the audio level - should be above threshold")
print("  • Try: 'hello', 'test', 'scan karo', 'temperature batao'")
print("\nPress Ctrl+C to stop\n")

voice.speak("Microphone test starting. Audio levels will be shown every three seconds.")

voice.start()

# Run for 60 seconds or until interrupted
try:
    while (time.time() - start_time) < 60:
        time.sleep(1)
        
except KeyboardInterrupt:
    print("\n\n[!] Stopped by user")

# Stop
voice.stop()

# Results
print("\n" + "="*70)
print("TEST RESULTS")
print("="*70)

total_time = int(time.time() - start_time)
print(f"\nDuration: {total_time} seconds")
print(f"Total Recognized: {recognized_count} phrases")

if recognized_count > 0:
    avg_time = total_time / recognized_count
    print(f"Average: 1 phrase every {avg_time:.1f} seconds")
    print(f"\n✅ MICROPHONE WORKING!")
    print(f"   Settings: 2x gain, threshold {voice.NOISE_THRESHOLD}")
else:
    print(f"\n⚠️  No speech detected in {total_time} seconds")
    print("\nTroubleshooting:")
    print("  1. Check if audio levels are showing above threshold")
    print("  2. Speak louder or move closer to microphone")
    print("  3. Check Bluetooth microphone connection")
    print("  4. Try: pactl list sources | grep bluez")

print("\n" + "="*70 + "\n")
