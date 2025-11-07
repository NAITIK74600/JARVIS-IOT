#!/usr/bin/env python3
"""
Test Google TTS voice quality
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.voice_engine import VoiceEngine
import time

print("\n" + "="*70)
print("GOOGLE TTS VOICE QUALITY TEST")
print("="*70)

# Initialize voice engine (should now use Google TTS)
voice = VoiceEngine()

print(f"\n📊 Voice Backend: {voice.tts_backend}")

if voice.tts_backend != 'gtts':
    print(f"\n⚠ Warning: Expected 'gtts' but got '{voice.tts_backend}'")
    print("Make sure you have internet connection for Google TTS.")
else:
    print("✓ Google TTS is active!")

print("\n" + "="*70)
print("Testing Google TTS with different phrases...")
print("Listen for smooth, natural human-like voice quality")
print("="*70)

test_phrases = [
    ("Good to see you, Sir.", "English - Greeting"),
    ("Right away, Sir.", "English - Acknowledgment"),
    ("Scan complete, Sir. Safest path at 90 degrees.", "English - Status"),
    ("My creator is Naitik Sir.", "English - Creator response"),
    ("The current time is 10:30 AM, Sir.", "English - Time"),
    ("Namaste Sir, aap kaise hain?", "Hinglish - Greeting"),
    ("Theek hai Sir, kaam ho gaya.", "Hinglish - Acknowledgment"),
]

print("\n🔊 Starting voice tests...\n")

for i, (text, description) in enumerate(test_phrases, 1):
    print(f"[{i}/{len(test_phrases)}] {description}")
    print(f'  Speaking: "{text}"')
    voice.speak(text)
    time.sleep(0.5)  # Brief pause between phrases
    print()

print("="*70)
print("✓ Google TTS Test Complete!")
print("="*70)

print("\n📋 Comparison:")
print("  eSpeak-NG (old): Robotic, broken, mechanical sound")
print("  Google TTS (new): Natural, smooth, human-like voice")

print("\n💡 Benefits of Google TTS:")
print("  ✓ Natural, human-like voice quality")
print("  ✓ Perfect pronunciation for English")
print("  ✓ Better Hinglish support")
print("  ✓ Smooth playback (no breaking or stuttering)")
print("  ✓ Multiple accents available")
print("  ✓ Professional sound like movie J.A.R.V.I.S.")

print("\n⚠ Note: Requires internet connection")
print("  Fallback to eSpeak-NG when offline")

print("\n" + "="*70)
