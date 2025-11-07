#!/usr/bin/env python3
"""
Test all imports from main.py to find which one is failing
"""
import sys
import traceback

def test_import(module_name, from_list=None):
    """Test importing a module"""
    try:
        if from_list:
            for item in from_list:
                exec(f"from {module_name} import {item}")
            print(f"✅ from {module_name} import {', '.join(from_list)}")
        else:
            exec(f"import {module_name}")
            print(f"✅ import {module_name}")
        return True
    except Exception as e:
        print(f"❌ Error importing {module_name}: {e}")
        traceback.print_exc()
        return False

print("=" * 70)
print("TESTING JARVIS IMPORTS")
print("=" * 70)
print()

# Basic imports
print("Testing basic imports...")
test_import("os")
test_import("tkinter")
test_import("threading")
test_import("queue")
test_import("time")
print()

# Hardware imports
print("Testing hardware imports...")
test_import("actuators.multi_servo_controller", ["multi_servo_controller"])
test_import("sensors.sensor_manager", ["SensorManager"])
test_import("core.hardware_manager", ["hardware_manager"])
print()

# Core imports
print("Testing core imports...")
test_import("core.voice_engine", ["VoiceEngine", "list_audio_devices"])
test_import("core.llm_manager", ["LLMManager", "ProviderUnavailable"])
test_import("core.offline_responder", ["OfflineResponder"])
test_import("core.jarvis_core", ["JarvisCore"])
test_import("core.memory", ["JarvisMemory"])
test_import("core.persona", ["persona"])
test_import("user_profile", ["user_profile"])
print()

# Tool imports
print("Testing tool imports...")
test_import("tools.file_system_tools", ["list_files", "read_file", "write_file", "delete_file"])
test_import("tools.memory_tools", ["read_from_memory", "write_to_memory", "delete_from_memory"])
test_import("tools.system_tools", ["get_os_version", "get_cpu_usage", "get_ram_usage"])
test_import("tools.network_tools", ["get_ip_address", "check_internet_connection"])
test_import("tools.web_tools", ["search_web"])
test_import("tools.automation_tools", ["get_installed_apps", "launch_app"])
test_import("tools.calendar_tools", ["get_calendar_events", "create_calendar_event"])
test_import("tools.api_tools", ["get_weather", "get_news"])
test_import("tools.vision_tools", ["capture_image_and_describe"])
test_import("tools.display_tools", ["display_text", "clear_display", "show_face"])
test_import("tools.ir_tools", ["ir_list_remotes", "ir_list_commands", "ir_send_command", "ir_learn_command"])
test_import("tools.motor_tools", ["move_forward", "move_backward", "turn_left", "turn_right", "stop_moving"])
print()

# Navigation imports
print("Testing navigation imports...")
test_import("navigation.scanner", ["perform_scan", "human_readable_summary"])
test_import("navigation.face_tracker", ["get_face_tracker"])
test_import("navigation.person_follower", ["get_person_follower"])
print()

print("=" * 70)
print("IMPORT TEST COMPLETE")
print("=" * 70)
