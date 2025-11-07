#!/usr/bin/env python3
"""
Simple Voice Engine Test - Speaking and Listening
Tests both microphone (listening) and speaker (speaking) in continuous mode
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.voice_engine import VoiceEngine
import time

print("\n" + "="*70)
print("JARVIS VOICE ENGINE TEST - Speaker & Microphone")
print("="*70)

# Track what we hear
heard_texts = []

def on_text_recognized(text):
    """Callback when speech is recognized"""
    print(f"\n✓ RECOGNIZED: '{text}'")
    heard_texts.append(text)
    
    # Echo what we heard
    voice.speak(f"You said: {text}")
    
    # Stop after 3 recognized phrases
    if len(heard_texts) >= 3:
        print("\n✓ Test complete - heard 3 phrases!")
        voice.stop()

# Initialize voice engine in continuous mode (no wake word)
print("\n1. Initializing Voice Engine...")
print("-" * 70)
voice = VoiceEngine(
    wake_word=None,  # No wake word - continuous listening
    transcript_callback=on_text_recognized
)

print(f"\nVoice Engine Status:")
print(f"  Speaker Available: ✓" if voice.voice_available else "  Speaker Available: ✗")
print(f"  Microphone Available: ✓" if voice.voice_available else "  Microphone Available: ✗")
print(f"  TTS Backend: {voice.tts_backend}")
print(f"  Microphone Index: {voice.microphone_index}")
print(f"  Continuous Mode: ✓" if voice.continuous_mode else "  Continuous Mode: ✗")

# Test speaking
print("\n2. Testing Speaker (Google TTS)...")
print("-" * 70)
voice.speak("Hello Sir. I am J.A.R.V.I.S. Testing microphone and speaker.")
time.sleep(1)

# Start listening
print("\n3. Starting Continuous Listening...")
print("-" * 70)
print("🎤 Speak now! (will stop after 3 recognized phrases or 30 seconds)")
print("   Try saying:")
print("     - scan karo")
print("     - temperature batao")
print("     - kya haal hai")

voice.start()

# Wait for up to 30 seconds or until we hear 3 phrases
start_time = time.time()
while len(heard_texts) < 3 and (time.time() - start_time) < 30:
    time.sleep(0.5)

# Stop listening
voice.stop()

# Results
print("\n" + "="*70)
print("TEST RESULTS")
print("="*70)

if len(heard_texts) > 0:
    print(f"\n✓ SUCCESS! Recognized {len(heard_texts)} phrase(s):")
    for i, text in enumerate(heard_texts, 1):
        print(f"  {i}. '{text}'")
else:
    print("\n✗ No speech recognized")
    print("  Check:")
    print("    - Bluetooth microphone is connected and working")
    print("    - Speaking clearly and loudly enough")
    print("    - Microphone is not muted")

print("\n" + "="*70)
print("Voice engine test complete!")
print("="*70 + "\n")
