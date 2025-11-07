#!/usr/bin/env python3
"""
JARVIS - Headless Mode (No GUI)
Voice-controlled assistant without Tkinter interface
Perfect for running on headless Raspberry Pi via SSH
"""

import os
import time
import traceback
import faulthandler
from dotenv import load_dotenv

# Load environment
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(SCRIPT_DIR, '.env'))
faulthandler.enable()

# Lightweight fallback tool decorator
try:
    from langchain_core.tools import tool
except ImportError:
    try:
        from langchain.tools import tool
    except ImportError:
        def tool(func):
            return func

# Global hardware references
sensor_manager = None
hardware_manager = None

print("="*70)
print("J.A.R.V.I.S. - Headless Mode")
print("="*70)

def main():
    """Main function - runs JARVIS without GUI"""
    global sensor_manager, hardware_manager
    
    voice_engine = None
    jarvis = None
    
    try:
        # --- Initialize Hardware Manager (Optional) ---
        try:
            from core.hardware_manager import hardware_manager as hw_mgr
            hardware_manager = hw_mgr
            print("[✓] Hardware manager initialized")
        except Exception as e:
            print(f"[!] Hardware manager not available: {e}")
            hardware_manager = None
        
        # --- Initialize Sensor Manager (Optional) ---
        try:
            from sensors.sensor_manager import SensorManager
            sensor_manager = SensorManager()
            sensor_manager.start()
            print("[✓] Sensor manager initialized")
        except Exception as e:
            print(f"[!] Sensors not available: {e}")
            sensor_manager = None
        
        # --- Initialize Display (Optional) ---
        try:
            from actuators.display import display
            display.clear()
            display.write_text("JARVIS", row=0, col=5)
            display.write_text("Starting...", row=1, col=3)
            print("[✓] Display initialized")
        except Exception as e:
            print(f"[!] Display not available: {e}")
        
        # --- Load Components ---
        print("\nLoading components...")
        from core.jarvis_core import JarvisCore
        from core.memory import JarvisMemory
        from core.persona import persona
        from user_profile import user_profile
        from core.voice_engine import VoiceEngine
        from core.llm_manager import LLMManager, ProviderUnavailable
        from core.offline_responder import OfflineResponder
        
        # Import tools
        from tools.file_system_tools import list_files, read_file, write_file, delete_file
        from tools.memory_tools import read_from_memory, write_to_memory, delete_from_memory
        from tools.system_tools import get_os_version, get_cpu_usage, get_ram_usage
        from tools.network_tools import get_ip_address, check_internet_connection
        from tools.web_tools import search_web
        from tools.api_tools import get_weather, get_news
        
        print("[✓] Components loaded")
        
        # --- Initialize LLM Manager ---
        llm_manager = None
        try:
            llm_manager = LLMManager()
            print(f"[✓] LLM Manager: {llm_manager.status_summary()}")
        except Exception as e:
            print(f"[!] LLM unavailable: {e}")
            print("[!] Running in offline mode")
        
        # --- Initialize Memory ---
        memory = JarvisMemory()
        
        # --- Create Tool List ---
        all_tools = [
            get_os_version, get_cpu_usage, get_ram_usage,
            get_ip_address, check_internet_connection,
            list_files, read_file, write_file, delete_file,
            read_from_memory, write_to_memory, delete_from_memory,
            search_web, get_weather, get_news,
        ]
        
        # --- Initialize Offline Responder ---
        offline_responder = OfflineResponder(
            all_tools,
            logger=lambda msg: print(f"[Offline] {msg}")
        )
        
        # --- Initialize JARVIS Core ---
        jarvis = JarvisCore(
            persona=persona,
            memory=memory,
            tools=all_tools,
            user_profile=user_profile,
            ui_mode=False,
            llm_manager=llm_manager,
            offline_responder=offline_responder,
        )
        print("[✓] JARVIS Core initialized")
        
        # --- Initialize Voice Engine ---
        print("\nInitializing voice system...")
        
        def process_voice_input(text):
            """Callback when speech is recognized"""
            print(f"\n🎤 You: {text}")
            
            # Check for exit command
            if any(word in text.lower() for word in ['exit', 'quit', 'shutdown', 'goodbye']):
                print("\n[!] Shutdown command received")
                voice_engine.speak("Shutting down. Goodbye Sir.")
                voice_engine.stop()
                return
            
            # Process with JARVIS
            try:
                response = jarvis.get_response(text)
                response_text = response.get("text", "")
                provider = response.get("provider", "")
                
                print(f"💬 JARVIS [{provider}]: {response_text}")
                
                # Speak response
                voice_engine.speak(response_text)
            except Exception as e:
                print(f"[ERROR] Processing failed: {e}")
                traceback.print_exc()
        
        voice_engine = VoiceEngine(
            wake_word=None,  # No wake word - continuous listening
            transcript_callback=process_voice_input
        )
        
        print(f"[✓] Voice Engine: {voice_engine.tts_backend}")
        print(f"[✓] Microphone: Index {voice_engine.microphone_index}")
        
        # --- Start JARVIS ---
        print("\n" + "="*70)
        print("J.A.R.V.I.S. ONLINE")
        print("="*70)
        
        greeting = "Good to see you, Sir. All systems operational."
        print(f"💬 JARVIS: {greeting}")
        voice_engine.speak(greeting)
        
        # Update display
        try:
            from actuators.display import display
            display.clear()
            display.write_text("JARVIS Online", row=0, col=2)
            display.write_text("Listening...", row=1, col=3)
            display.show_face('neutral')
        except:
            pass
        
        print("\n🎤 Listening continuously... (Say 'exit' or 'shutdown' to quit)")
        print("   Press Ctrl+C to stop\n")
        
        # Start voice engine
        voice_engine.start()
        
        # Keep running
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n[!] Keyboard interrupt received")
    except Exception as e:
        print(f"\n[ERROR] Fatal error: {e}")
        traceback.print_exc()
    finally:
        # --- Cleanup ---
        print("\nShutting down...")
        
        # Stop voice
        if voice_engine:
            try:
                voice_engine.stop()
                print("[✓] Voice engine stopped")
            except Exception as e:
                print(f"[!] Voice cleanup error: {e}")
        
        # Stop sensors
        if sensor_manager:
            try:
                sensor_manager.stop()
                print("[✓] Sensors stopped")
            except Exception as e:
                print(f"[!] Sensor cleanup error: {e}")
        
        # Cleanup hardware
        if hardware_manager:
            try:
                hardware_manager.cleanup()
                print("[✓] Hardware cleaned up")
            except Exception as e:
                print(f"[!] Hardware cleanup error: {e}")
        
        print("\n" + "="*70)
        print("J.A.R.V.I.S. Shutdown Complete")
        print("="*70 + "\n")

if __name__ == "__main__":
    main()
