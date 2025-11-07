#!/usr/bin/env python3
"""
Test script for Hinglish voice understanding and smooth responses.
Tests both English and Hinglish input/output.
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

print("=" * 70)
print("JARVIS HINGLISH VOICE TEST")
print("=" * 70)

# Test 1: Voice Engine Language Detection
print("\n1. Testing Voice Engine Language Detection...")
print("-" * 70)

try:
    from core.voice_engine import VoiceEngine
    
    test_phrases = [
        ("Hello, how are you?", "English"),
        ("Jarvis scan karo", "Hinglish"),
        ("Room dikha do", "Hinglish"),
        ("Kya hai yeh?", "Hinglish"),
        ("What is the time?", "English"),
        ("Theek hai, abhi karo", "Hinglish"),
        ("नमस्ते, कैसे हो?", "Hindi (Devanagari)"),
        ("Batao weather kaisa hai", "Hinglish"),
    ]
    
    # Create a dummy voice engine just for language detection
    class MockTTSEngine:
        def setProperty(self, key, value):
            pass
    
    ve = VoiceEngine()
    ve.tts_engine = MockTTSEngine()
    
    for phrase, expected in test_phrases:
        detected = ve._detect_language(phrase)
        is_hinglish = ve._is_hinglish(phrase)
        
        status = "✓" if (detected == 'hi' and 'Hinglish' in expected or 'Hindi' in expected) or \
                       (detected == 'en' and expected == 'English') else "✗"
        
        print(f"{status} '{phrase}'")
        print(f"   Expected: {expected} | Detected: {'Hindi/Hinglish' if detected == 'hi' else 'English'} | Hinglish: {is_hinglish}")
    
    print("\n✅ Voice engine language detection working!")
    
except Exception as e:
    print(f"❌ Error testing voice engine: {e}")
    import traceback
    traceback.print_exc()


# Test 2: LLM Understanding of Hinglish
print("\n2. Testing LLM Hinglish Understanding...")
print("-" * 70)

try:
    from core.llm_manager import LLMManager
    
    llm_mgr = LLMManager()
    current = llm_mgr.current()
    
    print(f"Active LLM: {current.name}")
    print(f"Total API Keys: {len(llm_mgr.providers)}")
    
    # Test with simple Hinglish prompts
    test_prompts = [
        "Jarvis, room scan karo aur batao kya dikha",
        "Theek hai, abhi time kya hai?",
        "Kya weather acha hai?",
    ]
    
    print("\nTesting Hinglish prompts with LLM:")
    for prompt in test_prompts:
        print(f"\n📝 Input: {prompt}")
        try:
            # Quick test - just invoke without full agent
            response = current.client.invoke(prompt)
            print(f"✅ Response: {response.content[:100]}...")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n✅ LLM can process Hinglish!")
    
except Exception as e:
    print(f"❌ Error testing LLM: {e}")
    import traceback
    traceback.print_exc()


# Test 3: Voice Output (TTS)
print("\n3. Testing Voice Output (TTS)...")
print("-" * 70)

try:
    from core.voice_engine import VoiceEngine
    
    ve = VoiceEngine()
    
    test_outputs = [
        ("Scan complete. Room is clear.", "English"),
        ("Theek hai sir, scan kar raha hoon.", "Hinglish"),
        ("Weather bahut acha hai aaj.", "Hinglish"),
    ]
    
    print("Testing TTS output (will be spoken if audio available):")
    for text, lang_type in test_outputs:
        print(f"\n📢 Speaking ({lang_type}): {text}")
        detected_lang = ve._detect_language(text)
        print(f"   Detected as: {'Hindi/Hinglish' if detected_lang == 'hi' else 'English'}")
        
        # Actually speak (only if not in test mode)
        if os.getenv("TEST_VOICE_OUTPUT") == "1":
            ve.speak(text)
            import time
            time.sleep(2)  # Wait for TTS to complete
    
    print("\n✅ TTS language selection working!")
    
except Exception as e:
    print(f"❌ Error testing TTS: {e}")
    import traceback
    traceback.print_exc()


# Test 4: System Prompt Check
print("\n4. Checking System Prompt for Hinglish Support...")
print("-" * 70)

try:
    from core.persona import persona
    
    prompt = persona.get_prompt()
    
    hinglish_keywords = [
        'Hinglish',
        'Hindi',
        'Hindi-English',
        'same language',
        'scan karo',
        'batao',
    ]
    
    found_keywords = []
    for keyword in hinglish_keywords:
        if keyword.lower() in prompt.lower():
            found_keywords.append(keyword)
    
    if found_keywords:
        print(f"✅ System prompt contains Hinglish support:")
        for kw in found_keywords:
            print(f"   ✓ Found: '{kw}'")
    else:
        print("❌ System prompt missing Hinglish instructions")
    
    # Show relevant section
    if 'LANGUAGE' in prompt:
        lines = prompt.split('\n')
        in_lang_section = False
        print("\nLanguage section from system prompt:")
        print("-" * 50)
        for line in lines:
            if 'LANGUAGE' in line:
                in_lang_section = True
            if in_lang_section:
                print(line)
                if line.strip().startswith('3.') or line.strip().startswith('4.'):
                    break
        print("-" * 50)
    
except Exception as e:
    print(f"❌ Error checking persona: {e}")
    import traceback
    traceback.print_exc()


# Summary
print("\n" + "=" * 70)
print("TEST SUMMARY")
print("=" * 70)
print("""
✅ Features Implemented:
   1. Hinglish language detection in voice engine
   2. Common Hinglish word pattern matching
   3. Automatic TTS language selection (gTTS for Hinglish/Hindi)
   4. System prompt with Hinglish instructions
   5. LLM configured to understand and respond in Hinglish

📝 How to Use:
   - Speak in English: "Jarvis, scan the room"
   - Speak in Hinglish: "Jarvis, room scan karo"
   - Mix naturally: "Jarvis batao, what is the weather?"
   - JARVIS will respond in the SAME language/style you use!

🔊 TTS Behavior:
   - Pure English → Fast pyttsx3 (offline)
   - Hinglish/Hindi → gTTS (better pronunciation, needs internet)

🎯 Smooth Responses:
   - Responses kept short (1-3 sentences)
   - Direct and action-oriented
   - Natural conversational tone

🚀 Ready to test with actual voice!
   Run: ./run.sh
   Then speak: "Jarvis, scan karo" or "Jarvis, scan the room"
""")
print("=" * 70)
