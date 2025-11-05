#!/usr/bin/env python3
"""
JARVIS Diagnostic Script
Tests all critical components of your JARVIS system
"""

import os
import sys
import traceback
from dotenv import load_dotenv

def test_environment():
    """Test environment variables and basic setup"""
    print("🔍 Testing Environment Setup...")
    
    # Load .env
    load_dotenv()
    
    # Check API key - Updated for Google Gemini
    api_key = os.getenv("GOOGLE_API_KEY")
    if api_key and len(api_key) > 10:
        print("✅ GOOGLE_API_KEY found and appears valid")
    else:
        print("❌ GOOGLE_API_KEY missing or invalid")
        print("   Please add your API key to .env file:")
        print("   GOOGLE_API_KEY=your-key-here")
        return False
    
    return True

def test_dependencies():
    """Test all required dependencies"""
    print("\n📦 Testing Dependencies...")
    
    dependencies = [
        'langchain',
        'langchain_openai',
        'pyaudio',
        'speech_recognition',
        'pyttsx3',
        'pyautogui',
        'langdetect',
        'vosk'
    ]
    
    failed = []
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"✅ {dep}")
        except ImportError as e:
            print(f"❌ {dep}: {e}")
            failed.append(dep)
    
    if failed:
        print(f"\n❌ Failed dependencies: {failed}")
        return False
    
    print("✅ All dependencies loaded successfully")
    return True

def test_audio_system():
    """Test audio input/output systems"""
    print("\n🎤 Testing Audio System...")
    
    try:
        import pyaudio
        p = pyaudio.PyAudio()
        info = p.get_default_input_device_info()
        print(f"✅ Input device: {info['name']}")
        p.terminate()
    except Exception as e:
        print(f"❌ Audio input error: {e}")
        return False
    
    try:
        import pyttsx3
        engine = pyttsx3.init()
        print("✅ Text-to-speech engine initialized")
    except Exception as e:
        print(f"❌ Text-to-speech error: {e}")
        return False
    
    return True

def test_core_systems():
    """Test core JARVIS systems"""
    print("\n🤖 Testing Core Systems...")
    
    try:
        from core.voice_engine import VoiceEngine
        print("✅ Voice engine class imported")
        engine = VoiceEngine()
        print("✅ Voice engine initialized")
        engine.speak("Core systems diagnostic check.")
        print("✅ Voice engine speak test successful.")
    except Exception as e:
        print(f"❌ Voice engine error: {e}")
        print(traceback.format_exc())
        return False
    
    try:
        import user_profile
        # Assuming user_profile has a FULL_NAME variable
        if hasattr(user_profile, 'FULL_NAME'):
            print(f"✅ User profile loaded for: {user_profile.FULL_NAME}")
        else:
            print("✅ User profile module loaded (no FULL_NAME attribute found).")
    except ImportError:
        print("⚠️ User profile (`user_profile.py`) not found. This is optional.")
    except Exception as e:
        print(f"❌ User profile error: {e}")
        return False
    
    return True

def main():
    """Run all diagnostic tests"""
    print("🚀 JARVIS Diagnostic Tool")
    print("=" * 50)
    
    tests = [
        ("Environment", test_environment),
        ("Dependencies", test_dependencies),
        ("Audio System", test_audio_system),
        ("Core Systems", test_core_systems)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 Diagnostic Results:")
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All systems ready! You can run main.py now")
    else:
        print("\n⚠️  Some issues detected. Please fix the failed tests above")
    
    return all_passed

if __name__ == "__main__":
    main()
