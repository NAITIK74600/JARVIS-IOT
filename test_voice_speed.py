#!/usr/bin/env python3
"""
Test voice generation speed optimizations.
Tests:
1. Cached phrases (instant)
2. Short phrases with pyttsx3 (fast local)
3. Long phrases with Google TTS (optimized)
"""

import time
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.voice_engine import VoiceEngine

def test_voice_speed():
    """Test different voice generation speeds"""
    print("=" * 60)
    print("VOICE SPEED OPTIMIZATION TEST")
    print("=" * 60)
    
    # Initialize voice engine
    print("\n1. Initializing Voice Engine...")
    voice = VoiceEngine(wake_word=None)
    
    # Test cases with expected speed
    test_phrases = [
        ("yes sir", "Cached/Fast Local", "Should be instant"),
        ("understood sir", "Cached/Fast Local", "Should be instant"),
        ("hello", "Fast Local TTS", "Should be < 1 second"),
        ("checking the weather now", "Fast Local TTS", "Should be < 2 seconds"),
        ("Sir, I am currently processing your request and will provide you with the information shortly", 
         "Google TTS Optimized", "Should be < 6 seconds"),
    ]
    
    print("\n2. Running Speed Tests...")
    print("-" * 60)
    
    for i, (text, method, expected) in enumerate(test_phrases, 1):
        print(f"\nTest {i}/{len(test_phrases)}: {method}")
        print(f"Text: {text[:50]}...")
        print(f"Expected: {expected}")
        
        start_time = time.time()
        voice.speak(text)
        elapsed = time.time() - start_time
        
        print(f"✓ Completed in {elapsed:.2f} seconds")
        
        # Brief pause between tests
        time.sleep(0.5)
    
    print("\n" + "=" * 60)
    print("OPTIMIZATION SUMMARY:")
    print("=" * 60)
    print("✓ Short phrases (1-5 words): Use cached or local TTS (instant)")
    print("✓ Medium phrases (6-10 words): Use fast local TTS (< 2s)")
    print("✓ Long phrases (10+ words): Use Google TTS with optimizations:")
    print("  - Faster timeout (3s)")
    print("  - 30% speed increase (sox tempo 1.3)")
    print("  - Smaller buffer (512)")
    print("  - Background caching for future use")
    print("=" * 60)

if __name__ == "__main__":
    test_voice_speed()
