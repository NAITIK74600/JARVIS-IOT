#!/usr/bin/env python3
"""
Minimal JARVIS - Voice Only (No GUI, No Hardware)
Tests speaking and listening without hardware dependencies
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("\n" + "="*70)
print("MINIMAL JARVIS - VOICE TEST")
print("="*70)

# Import only voice engine (no hardware)
from core.voice_engine import VoiceEngine
import time

def process_command(text):
    """Simple command processor"""
    text = text.lower().strip()
    print(f"\n🎤 You said: '{text}'")
    
    # Simple responses
    if 'scan' in text or 'karo' in text:
        response = "Scanning functionality requires hardware. Running in voice-only mode."
    elif 'temperature' in text or 'batao' in text:
        response = "Temperature sensor not available in voice-only mode."
    elif 'hello' in text or 'hi' in text or 'haal' in text:
        response = "Hello Sir! I am J.A.R.V.I.S. All systems operational."
    elif 'test' in text:
        response = "Voice system is working perfectly, Sir."
    elif 'stop' in text or 'exit' in text or 'quit' in text:
        response = "Shutting down. Goodbye Sir."
        voice.speak(response)
        voice.stop()
        sys.exit(0)
    else:
        response = f"I heard you say: {text}. Voice recognition is working, Sir."
    
    # Speak the response
    voice.speak(response)

# Initialize voice engine
print("\nInitializing Voice Engine...")
voice = VoiceEngine(
    wake_word=None,  # No wake word - continuous listening
    transcript_callback=process_command
)

print(f"\nConfiguration:")
print(f"  TTS Backend: {voice.tts_backend}")
print(f"  Microphone: {'✓ Ready' if voice.voice_available else '✗ Not available'}")
print(f"  Continuous Mode: ✓")

# Start
voice.speak("J.A.R.V.I.S. voice system online. Listening continuously. Say 'stop' to exit.")

print("\n" + "="*70)
print("LISTENING... (Say 'stop' or 'exit' to quit)")
print("="*70)
print("\nTry saying:")
print("  - hello")
print("  - test")
print("  - scan karo")
print("  - temperature batao")
print("  - stop\n")

# Start listening
voice.start()

# Keep running
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n\nShutting down...")
    voice.speak("Goodbye Sir.")
    voice.stop()

print("\n" + "="*70)
print("JARVIS voice test complete")
print("="*70 + "\n")
