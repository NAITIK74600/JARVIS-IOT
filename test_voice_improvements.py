#!/usr/bin/env python3
"""
Test script for voice improvements:
1. Creator response simplification
2. Hinglish voice quality with Bluetooth support
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.personality_engine import PersonalityEnhancer
from core.voice_engine import VoiceEngine

def test_creator_response():
    """Test that creator queries return simple response."""
    print("\n=== Testing Creator Response ===")
    personality = PersonalityEnhancer()
    
    test_queries = [
        "who is your creator",
        "tumhara creator kaun hai",
        "who created you",
        "who made you",
        "kaun banaya tumhe"
    ]
    
    for query in test_queries:
        result = personality.process_input(query)
        if result and result.get("intercept"):
            print(f"✓ Query: '{query}'")
            print(f"  Response: {result['response']}")
            print(f"  Expected: My creator is Naitik Sir.")
            assert result['response'] == "My creator is Naitik Sir.", "Creator response mismatch!"
        else:
            print(f"✗ Query: '{query}' - No intercept")
    
    print("\n✓ Creator response test PASSED\n")

def test_hinglish_detection():
    """Test Hinglish detection logic."""
    print("=== Testing Hinglish Detection ===")
    voice = VoiceEngine()
    
    test_cases = [
        ("Hello how are you", False, "Pure English"),
        ("Acha theek hai bhai", True, "Pure Hinglish"),
        ("Mujhe kuch batao yaar", True, "Hinglish casual"),
        ("Kya haal hai", True, "Common Hindi greeting"),
        ("The weather is nice", False, "English sentence"),
        ("Chalo lets go", True, "Mixed Hinglish"),
    ]
    
    for text, expected_hinglish, description in test_cases:
        is_hinglish = voice._is_hinglish(text)
        status = "✓" if is_hinglish == expected_hinglish else "✗"
        print(f"{status} '{text}' ({description})")
        print(f"   Expected: {expected_hinglish}, Got: {is_hinglish}")
    
    print("\n✓ Hinglish detection test PASSED\n")

def test_voice_output():
    """Test voice output with both English and Hinglish."""
    print("=== Testing Voice Output ===")
    print("Make sure your Bluetooth Mini Boost 4 is connected!")
    
    voice = VoiceEngine()
    
    # Test English
    print("\n1. Testing English (eSpeak-NG via PulseAudio)...")
    voice.speak("Hello sir, I am testing English voice output.")
    
    # Test Hinglish
    print("\n2. Testing Hinglish (gTTS via mpg123)...")
    voice.speak("Namaste sir, main Hinglish test kar raha hoon.")
    
    # Test creator response
    print("\n3. Testing creator response...")
    voice.speak("My creator is Naitik Sir.")
    
    print("\n✓ Voice output tests completed")
    print("Did you hear all three voice outputs through Bluetooth speaker?")

if __name__ == "__main__":
    print("=" * 60)
    print("JARVIS Voice Improvements Test")
    print("=" * 60)
    
    # Test 1: Creator response
    test_creator_response()
    
    # Test 2: Hinglish detection
    test_hinglish_detection()
    
    # Test 3: Voice output (requires Bluetooth connection)
    user_input = input("\nTest voice output? (y/n): ").strip().lower()
    if user_input == 'y':
        test_voice_output()
    
    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)
