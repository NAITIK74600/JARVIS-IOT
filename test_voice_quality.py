#!/usr/bin/env python3
"""
Test script for improved voice quality and recognition:
1. Smooth voice output (no choppy audio)
2. Better voice recognition with feedback
3. Proper audio routing through Bluetooth
"""

import sys
import os
import time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_voice_smoothness():
    """Test that voice output is smooth and clear."""
    print("\n" + "="*70)
    print("TESTING VOICE SMOOTHNESS")
    print("="*70)
    
    from core.voice_engine import VoiceEngine
    
    voice = VoiceEngine()
    
    test_phrases = [
        ("Good to see you, Sir.", "English greeting"),
        ("Right away, Sir.", "Short acknowledgment"),
        ("Scan complete, Sir. Safest path at 90 degrees.", "Status update"),
        ("Namaste Sir, aap kaise hain?", "Hinglish greeting"),
        ("The current temperature is 25 degrees celsius.", "Longer English sentence"),
    ]
    
    print("\n🔊 Testing voice output quality...")
    print("Listen for smooth, clear audio through your Bluetooth speaker.\n")
    
    for i, (text, description) in enumerate(test_phrases, 1):
        print(f"\n[{i}/{len(test_phrases)}] {description}")
        print(f"Speaking: \"{text}\"")
        
        voice.speak(text)
        time.sleep(0.5)  # Brief pause between phrases
    
    print("\n✓ Voice smoothness test completed")
    print("Did all phrases play smoothly without choppiness? (Should be YES)")

def test_voice_settings():
    """Display current voice engine settings."""
    print("\n" + "="*70)
    print("VOICE ENGINE SETTINGS")
    print("="*70)
    
    from core.voice_engine import VoiceEngine
    import subprocess
    
    voice = VoiceEngine()
    
    print(f"\n📊 Voice Engine Configuration:")
    print(f"  TTS Backend: {voice.tts_backend}")
    print(f"  Microphone Available: {voice.voice_available}")
    print(f"  Microphone Index: {voice.microphone_index}")
    print(f"  Sample Rate: {voice.RATE} Hz")
    print(f"  Chunk Size: {voice.CHUNK}")
    print(f"  Channels: {voice.CHANNELS}")
    print(f"  Wake Word: '{voice.wake_word}'")
    
    print(f"\n🔊 Audio Devices:")
    # Check PulseAudio settings
    result = subprocess.run(['pactl', 'info'], capture_output=True, text=True)
    for line in result.stdout.split('\n'):
        if 'Default Sink' in line or 'Default Source' in line:
            print(f"  {line.strip()}")
    
    # List Bluetooth devices
    result = subprocess.run(['pactl', 'list', 'sinks', 'short'], capture_output=True, text=True)
    print(f"\n🎧 Available Output Devices:")
    for line in result.stdout.strip().split('\n'):
        if line:
            parts = line.split('\t')
            if len(parts) >= 2:
                print(f"  [{parts[0]}] {parts[1]}")
    
    print("\n✓ Settings check completed")

def test_audio_routing():
    """Test that audio is routing through Bluetooth."""
    print("\n" + "="*70)
    print("TESTING BLUETOOTH AUDIO ROUTING")
    print("="*70)
    
    import subprocess
    
    # Check Bluetooth connection
    result = subprocess.run(['pactl', 'list', 'sinks', 'short'], capture_output=True, text=True)
    
    bluetooth_found = False
    for line in result.stdout.split('\n'):
        if 'bluez' in line.lower():
            print(f"✓ Bluetooth device found: {line.strip()}")
            bluetooth_found = True
    
    if not bluetooth_found:
        print("⚠ No Bluetooth audio device detected!")
        print("  Make sure your Mini Boost 4 is connected.")
        return False
    
    # Check default sink
    result = subprocess.run(['pactl', 'info'], capture_output=True, text=True)
    default_sink = None
    for line in result.stdout.split('\n'):
        if 'Default Sink:' in line:
            default_sink = line.split(':')[1].strip()
            break
    
    if default_sink and 'bluez' in default_sink.lower():
        print(f"✓ Default audio output is Bluetooth: {default_sink}")
        return True
    else:
        print(f"⚠ Default audio output is NOT Bluetooth: {default_sink}")
        print("  Audio may not play through your speaker.")
        return False

def test_espeak_quality():
    """Test eSpeak-NG with optimized settings."""
    print("\n" + "="*70)
    print("TESTING ESPEAK-NG QUALITY")
    print("="*70)
    
    import subprocess
    import tempfile
    import os
    
    print("\n🔊 Testing eSpeak-NG with optimized parameters...")
    
    test_text = "Good to see you, Sir. Systems are operational."
    
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
        tmp_path = tmp.name
    
    # Generate with optimized settings
    result = subprocess.run([
        'espeak-ng',
        '-v', 'en-us',
        '-s', '160',  # Speed
        '-p', '50',   # Pitch
        '-a', '200',  # Amplitude
        '-w', tmp_path,
        test_text
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✓ WAV generated: {os.path.getsize(tmp_path)} bytes")
        
        # Play it
        play_result = subprocess.run([
            'paplay', '--volume=65536', tmp_path
        ], capture_output=True, text=True)
        
        if play_result.returncode == 0:
            print("✓ Audio played successfully")
        else:
            print(f"✗ Audio playback failed: {play_result.stderr}")
        
        os.unlink(tmp_path)
    else:
        print(f"✗ WAV generation failed: {result.stderr}")

def main():
    print("\n" + "="*70)
    print("J.A.R.V.I.S. VOICE QUALITY & RECOGNITION TEST")
    print("="*70)
    print("\nThis test will verify:")
    print("1. Voice output is smooth (no choppy audio)")
    print("2. Audio routes through Bluetooth speaker")
    print("3. Voice recognition settings are optimal")
    print("4. eSpeak-NG quality improvements")
    
    # Test 1: Check settings
    test_voice_settings()
    
    # Test 2: Check Bluetooth routing
    bluetooth_ok = test_audio_routing()
    
    # Test 3: Test eSpeak quality
    test_espeak_quality()
    
    # Test 4: Test voice smoothness
    user_input = input("\nTest voice smoothness with actual phrases? (y/n): ").strip().lower()
    if user_input == 'y':
        test_voice_smoothness()
    
    print("\n" + "="*70)
    print("VOICE QUALITY TEST COMPLETED")
    print("="*70)
    
    print("\n📋 Summary:")
    if bluetooth_ok:
        print("✓ Bluetooth audio routing configured correctly")
    else:
        print("⚠ Check Bluetooth connection")
    
    print("\n💡 Improvements Made:")
    print("  • Removed threading for smoother playback")
    print("  • Added speech lock to prevent overlapping audio")
    print("  • Optimized eSpeak-NG with better voice, speed, and pitch")
    print("  • Reduced CHUNK size from 8192 to 4096 for better recognition")
    print("  • Added word-level timing for better wake word detection")
    print("  • Increased command timeout from 8s to 10s")
    print("  • Added visual feedback for wake word detection")
    
    print("\n🎤 To test recognition:")
    print("  1. Start JARVIS: ./start_jarvis_voice.sh")
    print("  2. Say: 'Jarvis'")
    print("  3. Wait for activation message")
    print("  4. Give a command")

if __name__ == "__main__":
    main()
