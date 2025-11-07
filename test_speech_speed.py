#!/usr/bin/env python3
"""
Test Faster Speech Response
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.voice_engine import VoiceEngine
import time

print("\n" + "="*70)
print("TESTING FASTER SPEECH RESPONSE")
print("="*70)

voice = VoiceEngine(wake_word=None)

print("\n✓ Voice Engine Ready")
print("  Testing speech speed...\n")

# Test different sentences
test_phrases = [
    "Hello Sir, testing faster speech response.",
    "The quick brown fox jumps over the lazy dog.",
    "Temperature batao, scan karo, sab theek hai.",
    "Good to see you Sir. All systems operational."
]

for i, phrase in enumerate(test_phrases, 1):
    print(f"\n[Test {i}/4] Speaking: '{phrase}'")
    start = time.time()
    
    voice.speak(phrase)
    
    elapsed = time.time() - start
    print(f"          ✓ Completed in {elapsed:.2f} seconds")
    
    time.sleep(0.5)  # Brief pause between tests

print("\n" + "="*70)
print("SPEED TEST COMPLETE")
print("="*70)
print("\n✅ Improvements:")
print("   • 15% faster playback speed (1.15x)")
print("   • Reduced buffer delay")
print("   • Faster timeout (5s)")
print("   • Should be noticeably quicker!\n")
