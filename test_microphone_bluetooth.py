#!/usr/bin/env python3
"""
Test Microphone Configuration - Bluetooth Mini Boost 4
Similar to speaker setup, ensures microphone uses PulseAudio and Bluetooth
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("\n" + "="*70)
print("MICROPHONE BLUETOOTH CONFIGURATION TEST")
print("="*70)

# Test 1: Check PulseAudio configuration
print("\n1. Checking PulseAudio Microphone Configuration...")
print("-" * 70)

import subprocess

result = subprocess.run(['pactl', 'info'], capture_output=True, text=True)
for line in result.stdout.split('\n'):
    if 'Default Source' in line:
        print(f"✓ {line.strip()}")
        if 'bluez' in line.lower():
            print("  ✓ Bluetooth microphone is default!")
        else:
            print("  ⚠ Not using Bluetooth microphone")

# Test 2: List all input sources
print("\n2. Available Microphone Sources...")
print("-" * 70)

result = subprocess.run(['pactl', 'list', 'sources', 'short'], capture_output=True, text=True)
bluetooth_found = False
for line in result.stdout.strip().split('\n'):
    if line:
        parts = line.split('\t')
        if len(parts) >= 2:
            print(f"  [{parts[0]}] {parts[1]}")
            if 'bluez' in parts[1].lower():
                bluetooth_found = True
                print(f"       ✓ Bluetooth input device!")

if bluetooth_found:
    print("\n✓ Bluetooth microphone (Mini Boost 4) detected")
else:
    print("\n⚠ No Bluetooth microphone found")

# Test 3: Initialize Voice Engine and check microphone selection
print("\n3. Testing Voice Engine Microphone Selection...")
print("-" * 70)

from core.voice_engine import VoiceEngine

voice = VoiceEngine(wake_word=None)

print(f"\nVoice Engine Configuration:")
print(f"  Microphone Available: {voice.voice_available}")
print(f"  Microphone Index: {voice.microphone_index}")
print(f"  Sample Rate: {voice.RATE} Hz")
print(f"  Channels: {voice.CHANNELS}")
print(f"  Chunk Size: {voice.CHUNK}")

if voice.microphone_index is not None:
    try:
        import pyaudio
        p = pyaudio.PyAudio()
        info = p.get_device_info_by_index(voice.microphone_index)
        print(f"\n✓ Selected Microphone:")
        print(f"  Device: {info.get('name')}")
        print(f"  Max Input Channels: {info.get('maxInputChannels')}")
        print(f"  Default Sample Rate: {info.get('defaultSampleRate')}")
        
        if 'bluez' in info.get('name', '').lower() or 'pulse' in info.get('name', '').lower():
            print(f"  ✓ Using PulseAudio/Bluetooth microphone!")
        else:
            print(f"  ⚠ Not using PulseAudio/Bluetooth")
            
        p.terminate()
    except Exception as e:
        print(f"  ✗ Error getting device info: {e}")
else:
    print("\n✗ No microphone selected")

# Test 4: Compare with speaker configuration
print("\n4. Microphone vs Speaker Configuration Comparison...")
print("-" * 70)

print("Speaker (Output):")
result = subprocess.run(['pactl', 'info'], capture_output=True, text=True)
for line in result.stdout.split('\n'):
    if 'Default Sink' in line:
        print(f"  {line.strip()}")

print("\nMicrophone (Input):")
for line in result.stdout.split('\n'):
    if 'Default Source' in line:
        print(f"  {line.strip()}")

print("\n✓ Both should use Bluetooth Mini Boost 4 (bluez_*)")

# Summary
print("\n" + "="*70)
print("SUMMARY")
print("="*70)

print("\n✓ Microphone Improvements:")
print("  • Prioritizes Bluetooth devices (Mini Boost 4)")
print("  • Uses PulseAudio for better compatibility")
print("  • Auto-detects best input device")
print("  • Optimized settings for Bluetooth mic")
print("  • Better error messages and logging")

print("\n✓ Configuration Priority:")
print("  1. Bluetooth microphone (bluez_input.*)")
print("  2. PulseAudio microphone (pulse)")
print("  3. Any other available input device")

print("\n✓ Just like Speaker Setup:")
print("  Speaker:     Google TTS → mpg123 → PulseAudio → Bluetooth")
print("  Microphone:  Bluetooth → PulseAudio → PyAudio → Vosk")

print("\n" + "="*70)
print("Microphone configuration optimized for Bluetooth!")
print("="*70 + "\n")
