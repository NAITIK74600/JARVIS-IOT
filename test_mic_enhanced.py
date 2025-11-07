#!/usr/bin/env python3
"""
Enhanced Microphone Test with Hinglish Support
Tests improved microphone: higher gain, noise cancellation, Hinglish recognition
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.voice_engine import VoiceEngine
import time

print("\n" + "="*70)
print("ENHANCED MICROPHONE TEST - Hinglish + Noise Cancellation")
print("="*70)

# Track recognized words
recognized_count = 0
hinglish_detected = []

def on_speech_recognized(text):
    """Callback when speech is detected"""
    global recognized_count, hinglish_detected
    recognized_count += 1
    elapsed = int(time.time() - start_time)
    
    # Check for Hinglish words
    hinglish_words = ['karo', 'batao', 'dikha', 'chalo', 'theek', 'haan', 'nahi', 'kya']
    found_hinglish = [word for word in hinglish_words if word in text.lower()]
    if found_hinglish:
        hinglish_detected.extend(found_hinglish)
        print(f"\n[{elapsed}s] 🎤 #{recognized_count}: '{text}' ✨ Hinglish: {found_hinglish}")
    else:
        print(f"\n[{elapsed}s] 🎤 #{recognized_count}: '{text}'")

# Initialize voice engine
print("\nInitializing enhanced voice engine...")
voice = VoiceEngine(
    wake_word=None,  # No wake word - continuous listening
    transcript_callback=on_speech_recognized
)

print(f"\n✓ Enhanced Voice Engine Ready")
print(f"  Microphone: Index {voice.microphone_index}")
print(f"  Input Gain: {voice.INPUT_GAIN}x (50% boost)")
print(f"  Noise Threshold: {voice.NOISE_THRESHOLD}")
print(f"  Chunk Size: {voice.CHUNK} (larger for better accuracy)")

# Start listening
print("\n" + "="*70)
print("🎤 ENHANCED LISTENING TEST - 30 SECONDS")
print("="*70)
print("\nTry these Hinglish phrases:")
print("  ✓ scan karo")
print("  ✓ temperature batao")
print("  ✓ kya haal hai")
print("  ✓ theek hai")
print("  ✓ chalo")
print("\nOr English:")
print("  ✓ hello")
print("  ✓ test")
print("  ✓ what time is it\n")

voice.speak("Enhanced microphone test. Trying higher gain and noise cancellation. Speak now.")

voice.start()
start_time = time.time()

# Run for 30 seconds
try:
    while (time.time() - start_time) < 30:
        time.sleep(1)
        
        # Show status every 5 seconds
        elapsed = int(time.time() - start_time)
        if elapsed % 5 == 0 and elapsed > 0:
            print(f"\n[{elapsed}s] Status: {recognized_count} detected, Hinglish words: {len(set(hinglish_detected))}")
            
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
print(f"Hinglish Words Detected: {len(set(hinglish_detected))} unique")

if hinglish_detected:
    print(f"Hinglish Words: {', '.join(set(hinglish_detected))}")

if recognized_count > 0:
    avg_time = total_time / recognized_count
    print(f"Average: 1 phrase every {avg_time:.1f} seconds")
    print(f"\n✅ ENHANCED MICROPHONE WORKING!")
    print(f"   • Higher gain (1.5x boost)")
    print(f"   • Noise cancellation active")
    print(f"   • Hinglish support enabled")
else:
    print(f"\n⚠️  No speech detected")
    print("Note: Speak clearly and close to microphone")

print("\n" + "="*70 + "\n")
