#!/usr/bin/env python3
"""Quick Google TTS voice test"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Simpler test without full voice engine
from gtts import gTTS
import subprocess
import tempfile
import uuid

print("\n🔊 Testing Google TTS Voice Quality\n")

test_phrases = [
    "Good to see you, Sir.",
    "My creator is Naitik Sir.",
    "Namaste Sir, aap kaise hain?",
]

temp_dir = "/tmp"

for text in test_phrases:
    print(f'Speaking: "{text}"')
    
    try:
        # Generate speech with Google TTS
        tts = gTTS(text=text, lang='en', slow=False, tld='com')
        temp_file = os.path.join(temp_dir, f"gtts_{uuid.uuid4()}.mp3")
        tts.save(temp_file)
        
        file_size = os.path.getsize(temp_file)
        print(f"  Generated: {file_size} bytes")
        
        # Play with mpg123
        result = subprocess.run(['mpg123', '--quiet', temp_file], 
                              capture_output=True, timeout=10)
        
        if result.returncode == 0:
            print("  ✓ Played successfully\n")
        else:
            print(f"  ✗ Playback failed: {result.returncode}\n")
        
        # Cleanup
        os.remove(temp_file)
        
    except Exception as e:
        print(f"  ✗ Error: {e}\n")

print("✓ Test complete!")
print("\nDid you hear smooth, natural voice through your Bluetooth speaker?")
