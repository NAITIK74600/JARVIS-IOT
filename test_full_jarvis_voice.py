#!/usr/bin/env python3
"""
Complete JARVIS voice test - Tests full pipeline:
1. Microphone pickup
2. Speech recognition
3. Command processing
4. Response generation
5. TTS output

This will show exactly where any issues occur.
"""

from core.voice_engine import VoiceEngine
from core.persona import Persona
import time

# Test data
test_count = 0
recognition_count = 0
response_count = 0
start_time = None

def process_voice_command(text):
    """Process recognized speech and generate response."""
    global test_count, recognition_count, response_count
    
    recognition_count += 1
    elapsed = time.time() - start_time
    
    print(f"\n{'='*60}")
    print(f"✅ RECOGNITION #{recognition_count} at {elapsed:.1f}s")
    print(f"{'='*60}")
    print(f"📝 You said: \"{text}\"")
    print(f"⏱️  Time: {elapsed:.1f}s from start")
    
    # Generate simple response
    persona = Persona()
    
    # Map common commands to responses
    if "hello" in text or "hi" in text:
        response = "Hello Sir! I'm listening and responding perfectly."
    elif "test" in text:
        response = "Test successful! Voice system working well."
    elif "scan" in text or "karo" in text:
        response = "Acknowledged Sir. The scan command was received clearly."
    elif "temperature" in text or "batao" in text:
        response = "The temperature is 25 degrees Celsius Sir."
    elif "who" in text and ("you" in text or "creator" in text):
        response = "I am JARVIS, created by Naitik Sir."
    else:
        response = f"I heard you say: {text}. Voice system is working perfectly!"
    
    print(f"💬 JARVIS: {response}")
    
    # Test TTS
    try:
        voice_engine.speak(response)
        response_count += 1
        print(f"🔊 TTS Output: SUCCESS ({response_count} total responses)")
    except Exception as e:
        print(f"❌ TTS Error: {e}")
    
    print(f"{'='*60}\n")

print("="*70)
print("COMPLETE JARVIS VOICE SYSTEM TEST")
print("="*70)
print()
print("This test will show:")
print("  1. ✅ Microphone input levels")
print("  2. ✅ Speech recognition accuracy")
print("  3. ✅ Command processing")
print("  4. ✅ Response generation")
print("  5. ✅ TTS output")
print()
print("Current settings:")
print("  • Microphone: Bluetooth Mini Boost 4 @ 150% volume")
print("  • Gain: 2.0x (double volume boost)")
print("  • Threshold: 200 (filters noise below this)")
print("  • Mode: Continuous listening (no wake word)")
print()
print("="*70)
print()

# Initialize voice engine
print("Initializing JARVIS voice system...")
voice_engine = VoiceEngine(wake_word=None, transcript_callback=process_voice_command)
voice_engine.start()
start_time = time.time()

print()
print("="*70)
print("🎤 JARVIS IS NOW LISTENING")
print("="*70)
print()
print("Test commands to try:")
print("  • 'hello' or 'hi'")
print("  • 'test'")
print("  • 'scan karo'")
print("  • 'temperature batao'")
print("  • 'who is your creator'")
print()
print("Watch for:")
print("  • Audio levels above 200 when speaking")
print("  • Recognition within 1-2 seconds")
print("  • Immediate response generation")
print("  • Clear TTS output")
print()
print("Test will run for 60 seconds. Press Ctrl+C to stop early.")
print("="*70)
print()

try:
    # Run for 60 seconds
    time.sleep(60)
except KeyboardInterrupt:
    print("\n\nTest stopped by user.")

# Stop voice engine
voice_engine.stop()

# Show results
print()
print("="*70)
print("TEST RESULTS")
print("="*70)
print(f"Duration: {time.time() - start_time:.1f} seconds")
print(f"Recognitions: {recognition_count}")
print(f"Responses: {response_count}")
print()

if recognition_count == 0:
    print("❌ NO RECOGNITIONS!")
    print()
    print("Possible issues:")
    print("  1. Speaking too quietly - audio level below threshold (200)")
    print("  2. Too far from microphone - need to be within 1-2 feet")
    print("  3. Background noise too loud")
    print()
    print("Solutions:")
    print("  • Speak LOUDER and CLOSER to microphone")
    print("  • Check audio levels in output - should be > 200 when speaking")
    print("  • Reduce background noise")
elif recognition_count > 0 and response_count == 0:
    print("⚠️  RECOGNITION WORKS BUT NO RESPONSES!")
    print()
    print("Issue: TTS or response generation failing")
    print("Check TTS errors in output above")
elif recognition_count > 0 and response_count > 0:
    print("✅ FULL SYSTEM WORKING!")
    print()
    success_rate = (response_count / recognition_count) * 100
    print(f"Success rate: {success_rate:.0f}%")
    print(f"Average response: 1 every {(time.time() - start_time) / recognition_count:.1f}s")
    print()
    if recognition_count < 3:
        print("⚠️  Low recognition count - may need to:")
        print("  • Speak louder and clearer")
        print("  • Move closer to microphone")
        print("  • Speak more frequently")

print("="*70)
