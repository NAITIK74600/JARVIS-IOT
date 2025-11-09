import os
import tkinter as tk
from tkinter import font, scrolledtext, END
import threading
import queue
import traceback
import time
import platform
import webbrowser
import faulthandler


from dotenv import load_dotenv
all_robot_tools = []
try:
    from tools.robot_tools import all_robot_tools
except ImportError as e:
    print(f"Warning: Could not import robot_tools: {e}")

all_sensor_tools = []
try:
    from tools.sensor_tools import all_sensor_tools
except ImportError as e:
    print(f"Warning: Could not import sensor_tools: {e}")

# Provide a lightweight fallback `tool` decorator so code using `@tool` does not
# crash at import time if LangChain isn't available yet. When LangChain is
# imported later, its `tool` can replace this behavior for full integration.
try:
    from langchain_core.tools import tool
except ImportError:
    try:
        from langchain.tools import tool
    except ImportError:
        # Fallback decorator if langchain not available
        def tool(func):
            return func

# --- Load environment variables from .env file ---
# Use absolute path so it works even when running with sudo
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(SCRIPT_DIR, '.env'))
faulthandler.enable()
# Note: faulthandler.register() for specific signals doesn't work well
# because enable() already handles SIGSEGV. We'll rely on enable() alone
# which writes to stderr by default.

# --- LLM and Tool-related Imports (LangChain) ---
# Deferred: heavy LangChain/transformers imports are done inside init_and_run_jarvis_core
# to avoid blocking startup or importing large ML libraries at module import time.

# --- Servo & Sensor Tools ---
from actuators.multi_servo_controller import multi_servo_controller
from navigation.scanner import perform_scan, human_readable_summary
from navigation.face_tracker import get_face_tracker
from navigation.person_follower import get_person_follower

last_scan_result = None
face_tracker = None
person_follower = None

# The old single servo instance is now replaced by the multi_servo_controller
# servo = None
# servo_lock = None

@tool
def scan_environment(_: str = "") -> str:
    """Scan the room/area/environment by moving the neck servo and using ultrasonic sensor to detect obstacles and find safe directions. Use this when asked to 'scan the room', 'scan the area', 'look around', or 'check for obstacles'."""
    global last_scan_result
    neck_servo = multi_servo_controller.get_servo('neck')
    
    # Check what's missing and provide specific feedback
    if not neck_servo:
        return "I cannot scan, Sir. The neck servo is not available."
    if not sensor_manager:
        return "I cannot scan, Sir. The ultrasonic sensor system is not initialized."
    
    lock = multi_servo_controller.get_lock('neck')
    if not lock.acquire(blocking=False):
        return "The neck servo is currently busy, Sir. Please try again in a moment."
    
    try:
        scan = perform_scan(neck_servo, sensor_manager)
        last_scan_result = scan
        return human_readable_summary(scan)
    except Exception as e:
        return f"Scan failed, Sir: {str(e)}"
    finally:
        lock.release()

@tool
def scan_environment_custom(params: str) -> str:
    """Perform a customized environmental scan with specific angles. Use when asked to scan a specific area or direction. Input format: start_angle,end_angle,step (e.g. '40,140,20' scans from 40° to 140° in 20° steps)."""
    global last_scan_result
    neck_servo = multi_servo_controller.get_servo('neck')
    
    # Check what's missing and provide specific feedback
    if not neck_servo:
        return "I cannot scan, Sir. The neck servo is not available."
    if not sensor_manager:
        return "I cannot scan, Sir. The ultrasonic sensor system is not initialized."
        
    lock = multi_servo_controller.get_lock('neck')
    if not lock.acquire(blocking=False):
        return "The neck servo is currently busy, Sir. Please try again in a moment."
        
    try:
        try:
            parts = [int(p.strip()) for p in params.split(',') if p.strip()]
            if len(parts) != 3:
                return "Invalid format, Sir. Please use: start,end,step (e.g. 40,140,20)"
            s, e, st = parts
            scan = perform_scan(neck_servo, sensor_manager, start_angle=s, end_angle=e, step=st)
            last_scan_result = scan
            return human_readable_summary(scan)
        except ValueError:
            return "Invalid numbers, Sir. Please provide three integers: start,end,step."
        except Exception as e:
            return f"Scan failed, Sir: {str(e)}"
    finally:
        lock.release()

@tool
def get_last_scan(_: str = "") -> str:
    """Return a summary of the most recent scan (angles, distances)."""
    if last_scan_result is None:
        return "No scans yet. Please run scan_environment first."
    d = last_scan_result.to_dict()
    samples_str = ', '.join(f"{a}:{dist:.0f}" if dist >= 0 else f"{a}:X" for a, dist in d['samples'])
    summary = d['summary']
    return (f"Samples[{samples_str}] | Best {summary.get('best_angle')} -> {summary.get('best_clearance_cm')}cm | "
            f"Avg {summary.get('average_distance_cm')}cm")


@tool
def track_face(_: str = "") -> str:
    """Start face tracking mode. JARVIS will use the camera and neck servo to track and follow faces. Use when asked to 'track face', 'track my face', 'follow my face', or 'look at me'."""
    global face_tracker
    
    # Initialize tracker if needed
    if face_tracker is None:
        face_tracker = get_face_tracker(multi_servo_controller)
    
    # Check if already tracking
    if face_tracker.is_tracking():
        return "Already tracking face. Say 'stop tracking' to stop."
    
    # Start tracking
    success = face_tracker.start_tracking()
    if success:
        return "Face tracking started. I will follow your face with my head. Say 'stop tracking' when done."
    else:
        return "Failed to start face tracking. Camera or neck servo may not be available."


@tool
def stop_face_tracking(_: str = "") -> str:
    """Stop face tracking mode. Use when asked to 'stop tracking', 'stop following face', or 'stop looking at me'."""
    global face_tracker
    
    if face_tracker is None or not face_tracker.is_tracking():
        return "Not currently tracking faces."
    
    face_tracker.stop_tracking()
    return "Face tracking stopped. I'm back to normal mode."


@tool
def follow_me(_: str = "") -> str:
    """Start follow me mode. JARVIS will follow you using sensors and motors. Use when asked to 'follow me', 'come with me', 'mere saath chalo', or 'follow karo'."""
    global person_follower
    
    # Initialize follower if needed
    if person_follower is None:
        from actuators.motor_controller import MotorController
        try:
            motors = MotorController()
        except:
            motors = None
        person_follower = get_person_follower(motors, sensor_manager, multi_servo_controller)
    
    # Check if already following
    if person_follower.is_following():
        return "Already following you. Say 'stop following' to stop."
    
    # Start following
    success = person_follower.start_following()
    if success:
        return "Follow me mode activated! I will maintain distance and follow you. Say 'stop following' when done."
    else:
        return "Failed to start follow mode. Motors or sensors may not be available."


@tool
def stop_following(_: str = "") -> str:
    """Stop follow me mode. Use when asked to 'stop following', 'stop', 'ruk jao', or 'theek hai'."""
    global person_follower
    
    if person_follower is None or not person_follower.is_following():
        return "Not currently following."
    
    person_follower.stop_following()
    return "Follow mode stopped. I'm staying in place now."


@tool
def get_tracking_status(_: str = "") -> str:
    """Check current tracking and following status."""
    global face_tracker, person_follower
    
    status = []
    
    if face_tracker and face_tracker.is_tracking():
        status.append("Face tracking: Active")
    else:
        status.append("Face tracking: Inactive")
    
    if person_follower and person_follower.is_following():
        status.append("Follow me: Active")
    else:
        status.append("Follow me: Inactive")
    
    return " | ".join(status)


@tool
def get_mode_status(_: str = "") -> str:
    """Get current offline/online mode status and API health."""
    try:
        from core.mode_optimizer import get_mode_optimizer
        optimizer = get_mode_optimizer()
        status = optimizer.get_status()
        
        mode_text = "🌐 Online" if status["mode"] == "auto" else "⚡ Offline"
        connectivity = "Connected" if status["online"] else "Disconnected"
        failures = status["api_failures"]
        
        return (f"Mode: {mode_text} | "
                f"Internet: {connectivity} | "
                f"API Failures: {failures} | "
                f"Last Success: {int(status['last_success'])}s ago")
    except Exception as e:
        return f"Mode optimizer not available: {e}"


@tool
def switch_mode(mode: str) -> str:
    """Force switch to offline, online, or auto mode. Use 'offline', 'online', or 'auto'."""
    try:
        from core.mode_optimizer import get_mode_optimizer
        optimizer = get_mode_optimizer()
        
        if mode.lower() not in ["offline", "online", "auto"]:
            return "Invalid mode. Use 'offline', 'online', or 'auto'."
        
        optimizer.force_mode(mode.lower())
        return f"Mode switched to {mode.lower()}. This will take effect on next command."
    except Exception as e:
        return f"Failed to switch mode: {e}"


# --- Sensor Manager ---
# Deferred initialization - will be created inside init_and_run_jarvis_core()
sensor_manager = None

# --- J.A.R.V.I.S. Custom Tools ---
# --- Core Voice Engine ---
from core.voice_engine import VoiceEngine, list_audio_devices
# Hardware manager - deferred import to avoid early GPIO initialization
hardware_manager = None
try:
    from core.llm_manager import LLMManager, ProviderUnavailable
except ImportError:
    LLMManager = None
    ProviderUnavailable = Exception
from core.offline_responder import OfflineResponder

# Motor tools - deferred import
try:
    from tools.motor_tools import move_forward, move_backward, turn_left, turn_right, stop_moving
except ImportError as e:
    print(f"[WARNING] Motor tools not available: {e}")
    # Create dummy tools
    @tool
    def move_forward(_: str = "") -> str:
        """Move forward (hardware not available)."""
        return "Motor hardware not available"
    @tool
    def move_backward(_: str = "") -> str:
        """Move backward (hardware not available)."""
        return "Motor hardware not available"
    @tool
    def turn_left(_: str = "") -> str:
        """Turn left (hardware not available)."""
        return "Motor hardware not available"
    @tool
    def turn_right(_: str = "") -> str:
        """Turn right (hardware not available)."""
        return "Motor hardware not available"
    @tool
    def stop_moving(_: str = "") -> str:
        """Stop moving (hardware not available)."""
        return "Motor hardware not available"


@tool
def get_current_system_time() -> str:
    """Returns the current date and time."""
    return time.strftime("%I:%M %p on %A, %B %d, %Y")

@tool
def open_webpage(url: str) -> str:
    """Opens a specified URL in the default web browser. Input should be a full URL."""
    try:
        webbrowser.open(url)
        return f"Opened {url} successfully."
    except Exception as e:
        return f"Failed to open {url}: {e}"

@tool
def set_servo_angle(servo_name: str, angle: int) -> str:
    """
    Sets a specific servo to a given angle.
    - servo_name (str): The name of the servo ('neck', 'arm_l', 'arm_r').
    - angle (int): The angle between 0 and 180 degrees.
    """
    try:
        angle = int(angle)
        if not (0 <= angle <= 180):
            return "Error: Angle must be between 0 and 180."
        
        multi_servo_controller.set_angle(servo_name, angle)
        return f"Servo '{servo_name}' set to {angle} degrees."
    except ValueError as e:
        return f"Error: {e}"
    except RuntimeError as e:
        return f"Error: {e}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

@tool
def calibrate_servo(servo_name: str) -> str:
    """Runs a calibration sweep on a specific servo ('neck', 'arm_l', 'arm_r')."""
    servo = multi_servo_controller.get_servo(servo_name)
    if not servo:
        return f"Servo '{servo_name}' not found."
    
    lock = multi_servo_controller.get_lock(servo_name)
    if not lock.acquire(blocking=False):
        return f"Servo '{servo_name}' is busy."
        
    try:
        servo.center()
        time.sleep(0.5)
        servo.sweep(step=45, delay=0.4)
        time.sleep(0.5)
        servo.center()
        return f"Calibration of servo '{servo_name}' complete."
    except Exception as e:
        return f"Calibration failed for '{servo_name}': {e}"
    finally:
        lock.release()

@tool
def get_environment_readings(_: str = "") -> str:
    """Return current temperature (C) and humidity (%) from the DHT sensor."""
    if not sensor_manager:
        return "Environment sensor not available. Please check DHT sensor wiring and restart Jarvis."
    try:
        t = sensor_manager.get_temperature()
        h = sensor_manager.get_humidity()
        if t is None or h is None:
            return "Failed to read environment sensor. Please check DHT sensor wiring and try again."
        return f"Temperature {t:.1f} °C, Humidity {h:.1f}%"
    except Exception as e:
        return f"Error reading environment sensor: {e}. Please check DHT sensor wiring and try again."

@tool
def get_all_sensor_readings(_: str = "") -> str:
    """Return a combined snapshot of all sensor readings (distance, alcohol, temp, humidity, last motion)."""
    if not sensor_manager:
        return "Sensor manager unavailable. Please check hardware and restart Jarvis."
    try:
        readings = sensor_manager.get_all_readings()
        if not readings:
            return "No readings available."
        def fmt(name, val, unit=""):
            if val is None:
                return f"{name}=N/A (check sensor)"
            if isinstance(val, float):
                # Choose formatting based on magnitude
                if abs(val) >= 100:
                    return f"{name}={val:.0f}{unit}"
                return f"{name}={val:.2f}{unit}" if unit else f"{name}={val:.2f}"
            return f"{name}={val}{unit}"
        parts = [
            fmt("distance_cm", readings.get("distance_cm"), "cm"),
            fmt("alcohol_level_mg_l", readings.get("alcohol_level_mg_l"), "mg/L"),
            fmt("temperature_c", readings.get("temperature_c"), "C"),
            fmt("humidity_percent", readings.get("humidity_percent"), "%"),
        ]
        lm = readings.get("last_motion_timestamp")
        if lm:
            age = time.time() - lm
            parts.append(f"last_motion={age:.0f}s_ago")
        else:
            parts.append("last_motion=none")
        return " | ".join(parts)
    except Exception as e:
        return f"Error gathering sensor readings: {e}. Please check all sensor connections and try again."

@tool
def legacy_scan_environment(_: str = "") -> str:
    """Deprecated alias for scan_environment. Use scan_environment instead."""
    return "This tool is deprecated. Use scan_environment instead."


class JarvisApp:
    def __init__(self, root):
        self.root = root
        self.root.title("J.A.R.V.I.S.")

        # --- Window Configuration ---
        w, h = 500, 650
        sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
        px, py = (sw // 2) - (w // 2), (sh // 2) - (h // 2)
        self.root.geometry(f"{w}x{h}+{px}+{py}")
        self.root.minsize(400, 500)

        # --- Styling ---
        self.bg_color = "#2E2E2E"
        self.text_area_bg = "#1E1E1E"
        self.entry_bg = "#3C3C3C"
        self.text_fg = "#E0E0E0"
        self.button_bg = "#007ACC"
        self.root.configure(bg=self.bg_color)

        # --- UI State and Fonts ---
        self.ui_queue = queue.Queue()
        self.main_font = font.Font(family="Monospace", size=10)
        self.bold_font = font.Font(family="Monospace", size=10, weight="bold")

        # --- Main Frame ---
        self.main_frame = tk.Frame(root, bg=self.bg_color)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # --- Scrolled Text Area for Logs ---
        self.log_area = scrolledtext.ScrolledText(
            self.main_frame,
            wrap=tk.WORD,
            bg=self.text_area_bg,
            fg=self.text_fg,
            font=self.main_font,
            state='disabled',
            relief=tk.FLAT,
            borderwidth=0
        )
        self.log_area.pack(pady=5, fill=tk.BOTH, expand=True)
        self.log_area.tag_config('error', foreground='red', font=self.bold_font)
        self.log_area.tag_config('info', foreground='cyan')
        self.log_area.tag_config('user', foreground='lightgreen', font=self.bold_font)
        self.log_area.tag_config('jarvis', foreground='lightblue', font=self.bold_font)
        self.log_area.tag_config('tool', foreground='yellow')

        # --- Input Frame ---
        self.input_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        self.input_frame.pack(fill=tk.X, pady=5)

        self.entry = tk.Entry(
            self.input_frame,
            bg=self.entry_bg,
            fg=self.text_fg,
            font=self.main_font,
            insertbackground=self.text_fg,
            relief=tk.FLAT,
            borderwidth=0
        )
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5)
        self.entry.bind("<Return>", self.send_message)

        self.send_button = tk.Button(
            self.input_frame,
            text="Send",
            command=self.send_message,
            bg=self.button_bg,
            fg=self.text_fg,
            relief=tk.FLAT,
            borderwidth=0
        )
        self.send_button.pack(side=tk.RIGHT, padx=(5, 0))

        # --- Status Bar ---
        self.status_bar = tk.Label(
            self.main_frame,
            text="Initializing...",
            font=self.main_font,
            bg=self.bg_color,
            fg=self.text_fg,
            anchor='w'
        )
        self.status_bar.pack(fill=tk.X)

        # --- Jarvis Core and Voice Engine ---
        self.jarvis_thread = None
        self.voice_engine = None
        self.jarvis_core = None
        self.user_input_queue = queue.Queue()

        # --- Start Processes ---
        self.root.after(100, self.process_ui_queue)
        self.start_jarvis_thread()

    def start_jarvis_thread(self):
        """Starts the main Jarvis logic in a separate thread to keep the UI responsive."""
        self.jarvis_thread = threading.Thread(target=init_and_run_jarvis_core, args=(self.ui_queue, self.user_input_queue), daemon=True)
        self.jarvis_thread.start()

    def send_message(self, event=None):
        """Handles sending a message from the UI to the Jarvis core."""
        user_input = self.entry.get().strip()
        if user_input:
            self.log_message(f"You: {user_input}\n", "user")
            self.user_input_queue.put(user_input)
            self.entry.delete(0, END)

    def log_message(self, message, tag=None):
        """Safely logs a message to the text area from any thread."""
        self.log_area.configure(state='normal')
        if tag:
            self.log_area.insert(END, message, tag)
        else:
            self.log_area.insert(END, message)
        self.log_area.configure(state='disabled')
        self.log_area.yview(END)

    def update_status(self, text):
        """Updates the status bar text."""
        self.status_bar.config(text=text)

    def update_voice_status(self, status):
        """Updates the UI based on voice engine status ('listening' or 'idle')."""
        if status == "listening":
            self.status_bar.config(text="Listening...", fg="cyan")
        else:
            self.status_bar.config(text="Ready", fg=self.text_fg)

    def process_ui_queue(self):
        """Processes messages from the Jarvis core to update the UI."""
        try:
            while not self.ui_queue.empty():
                message_type, payload = self.ui_queue.get_nowait()
                if message_type == "log":
                    self.log_message(payload['msg'], payload.get('tag'))
                elif message_type == "status":
                    self.update_status(payload)
                elif message_type == "voice_status":
                    self.update_voice_status(payload)
                elif message_type == "exit":
                    self.root.quit()
        finally:
            self.root.after(100, self.process_ui_queue)

def init_and_run_jarvis_core(ui_queue, user_input_queue):
    """
    Initializes and runs the main Jarvis logic loop.
    This function is executed in a separate thread.
    """
    jarvis = None
    voice_engine = None

    def log(msg, tag=None):
        ui_queue.put(("log", {"msg": msg, "tag": tag}))
        try:
            print(msg, end="", flush=True)
        except Exception:
            pass

    def update_status(status):
        ui_queue.put(("status", status))

    try:
        # --- Initialize Hardware Manager (GPIO) ---
        global hardware_manager
        try:
            from core.hardware_manager import hardware_manager as hw_mgr
            hardware_manager = hw_mgr
            log("Hardware manager initialized.\n", "info")
        except Exception as hw_err:
            log(f"Hardware manager init warning: {hw_err}\n", "warning")
            log("Running without GPIO hardware support.\n", "info")
            hardware_manager = None
        
        # --- Initialize Sensor Manager ---
        global sensor_manager
        try:
            from sensors.sensor_manager import SensorManager
            sensor_manager = SensorManager()
            sensor_manager.start()
            log("Sensor manager initialized.\n", "info")
            
            # Set the sensor manager reference for sensor tools
            try:
                from tools.sensor_tools import set_sensor_manager
                set_sensor_manager(sensor_manager)
            except ImportError:
                pass  # sensor_tools not available
                
        except ImportError as sensor_import_err:
            log(f"Sensor modules not found: {sensor_import_err}\n", "warning")
            log("Running without sensor support.\n", "info")
            sensor_manager = None
        except Exception as sensor_init_err:
            log(f"Sensor init warning: {sensor_init_err}\n", "warning")
            log("Running without sensor support.\n", "info")
            sensor_manager = None
        
        # --- Initialize Display ---
        try:
            from actuators.display import display
            display.clear()
            display.write_text("JARVIS", row=0, col=5)
            display.write_text("Booting...", row=1, col=3)
            log("Display initialized.\n", "info")
        except Exception as disp_err:
            log(f"Display init warning: {disp_err}\n", "warning")
        
        # --- Heavy Imports ---
        log("Loading core components...\n")
        from core.jarvis_core import JarvisCore
        from core.memory import JarvisMemory
        from core.persona import persona
        from core.greeting_manager import GreetingManager
        from user_profile import user_profile
        
        from tools.file_system_tools import list_files, read_file, write_file, delete_file
        from tools.memory_tools import read_from_memory, write_to_memory, delete_from_memory
        from tools.system_tools import get_os_version, get_cpu_usage, get_ram_usage
        from tools.network_tools import get_ip_address, check_internet_connection
        from tools.web_tools import search_web
        from tools.automation_tools import get_installed_apps, launch_app
        from tools.calendar_tools import get_calendar_events, create_calendar_event
        from tools.api_tools import get_weather, get_news
        from tools.vision_tools import capture_image_and_describe
        from tools.display_tools import display_text, clear_display, show_face
        
        # Try to import IR tools (optional - needs lirc library)
        try:
            from tools.ir_tools import (
                ir_list_remotes,
                ir_list_commands,
                ir_send_command,
                ir_learn_command,
                ir_record_signal,
                ir_send_saved_signal,
                ir_list_saved_signals,
                ir_delete_signal,
            )
            ir_tools_available = True
            log("IR remote control tools loaded.\n", "info")
        except ImportError as ir_err:
            log(f"IR tools not available (lirc not installed): {ir_err}\n", "warning")
            ir_tools_available = False
            # Create dummy tool functions so AgentExecutor still receives Tool instances
            @tool
            def ir_list_remotes(_: str = "") -> str:
                """List available IR remotes when IR support is disabled."""
                return "IR tools not available (lirc library not installed)"

            @tool
            def ir_list_commands(_: str = "") -> str:
                """List commands for an IR remote when IR support is disabled."""
                return "IR tools not available"

            @tool
            def ir_send_command(_: str = "") -> str:
                """Send an IR command placeholder when IR support is disabled."""
                return "IR tools not available"

            @tool
            def ir_learn_command(_: str = "") -> str:
                """Learn an IR command placeholder when IR support is disabled."""
                return "IR tools not available"

            @tool
            def ir_record_signal(_: str = "") -> str:
                """Record IR placeholder when IR support is disabled."""
                return "IR tools not available"

            @tool
            def ir_send_saved_signal(_: str = "") -> str:
                """Send saved IR placeholder when IR support is disabled."""
                return "IR tools not available"

            @tool
            def ir_list_saved_signals(_: str = "") -> str:
                """List saved IR placeholder when IR support is disabled."""
                return "IR tools not available"

            @tool
            def ir_delete_signal(_: str = "") -> str:
                """Delete saved IR placeholder when IR support is disabled."""
                return "IR tools not available"

        log("Components loaded.\n", "info")
        
        # Update display
        try:
            display.clear()
            display.write_text("Components", row=0, col=3)
            display.write_text("Loaded", row=1, col=5)
        except:
            pass

        # --- LLM Provider Management ---
        llm_manager = None
        offline_notice = None
        try:
            llm_manager = LLMManager()
            for warning in llm_manager.warnings:
                log(f"[LLM] {warning}\n", "info")
        except ProviderUnavailable as exc:
            offline_notice = str(exc)
            log(f"LLM initialisation failed: {offline_notice}\n", "error")
            log("Continuing in offline command mode.\n", "info")

        # --- User Profile ---
        user_name = user_profile.get("name", "Sir")
        greeting_manager = GreetingManager(
            user_name=user_name,
            location_hint=os.getenv("JARVIS_LOCATION", "control room"),
        )

        # --- Initialize Memory ---
        memory = JarvisMemory()

        # --- Tool Aggregation ---

        @tool
        def warm_welcome(_: str = "") -> str:
            """Deliver a friendly greeting sequence with voice and display."""
            script = greeting_manager.build_interactive_greeting()
            combined = script.speech_text()

            log(f"Jarvis {combined}\n", "jarvis")

            if voice_engine:
                for line in script.speech_lines:
                    try:
                        voice_engine.speak(line)
                    except Exception as speak_err:
                        log(f"Warm welcome speech error: {speak_err}\n", "warning")
                        break

            try:
                from actuators.display import display

                display.clear()
                for row, text in enumerate(script.display_lines[:2]):
                    text = text[:16]
                    col = max(0, (16 - len(text)) // 2)
                    display.write_text(text, row=row, col=col)
                try:
                    display.show_face("happy")
                except Exception:
                    pass
            except Exception as disp_err:
                log(f"Warm welcome display warning: {disp_err}\n", "warning")

            update_status(script.status_line)
            return combined or "Hello!"

        all_tools = [
            get_current_system_time, get_os_version, get_cpu_usage, get_ram_usage,
            open_webpage, search_web, get_ip_address, check_internet_connection,
            set_servo_angle, calibrate_servo, get_environment_readings, get_all_sensor_readings,
            scan_environment, scan_environment_custom, get_last_scan,
            capture_image_and_describe,
            list_files, read_file, write_file, delete_file,
            read_from_memory, write_to_memory, delete_from_memory,
            get_installed_apps, launch_app,
            get_calendar_events, create_calendar_event, get_weather, get_news,
            display_text, clear_display, show_face, warm_welcome,
            ir_list_remotes, ir_list_commands, ir_send_command, ir_learn_command,
            ir_record_signal, ir_send_saved_signal, ir_list_saved_signals, ir_delete_signal,
            move_forward, move_backward, turn_left, turn_right, stop_moving,
            track_face, stop_face_tracking, follow_me, stop_following, get_tracking_status,
            get_mode_status, switch_mode,
        ]
        all_tools.extend(all_robot_tools)
        all_tools.extend(all_sensor_tools)

        if os.getenv("JARVIS_DEBUG_TOOLS") == "1":
            try:
                from langchain_core.tools import BaseTool
                for tool_obj in all_tools:
                    if not isinstance(tool_obj, BaseTool):
                        log(f"[DEBUG] Non-BaseTool entry detected: {tool_obj}\n", "warning")
            except Exception as debug_exc:
                log(f"[DEBUG] Tool inspection failed: {debug_exc}\n", "warning")

        offline_logger = (lambda msg: log(f"[Offline] {msg}\n", "info")) if llm_manager is None else None
        offline_responder = OfflineResponder(all_tools, logger=offline_logger)

        # --- Initialize Jarvis Core ---
        jarvis = JarvisCore(
            persona=persona,
            memory=memory,
            tools=all_tools,
            user_profile=user_profile,
            ui_mode=True,
            llm_manager=llm_manager,
            offline_responder=offline_responder,
            status_callback=update_status,
        )
        if llm_manager:
            update_status(llm_manager.status_summary())
        else:
            status = "Offline mode ready."
            if offline_notice:
                status += f" ({offline_notice})"
            update_status(status)

        # --- Voice Callback Wrapper ---
        def voice_input_handler(transcript: str):
            """
            Wrapper for voice input that processes AND speaks the response.
            OPTIMIZED: Immediate audio feedback for faster perceived response.
            """
            try:
                log(f"You: {transcript}\n", "user")
                log(f"Processing: '{transcript}'\n", "info")
                update_status("Thinking...")
                
                # Show listening face on display
                try:
                    from tools.display_response import show_listening
                    show_listening()
                except:
                    pass
                
                # Quick acknowledgment for faster perceived response (optional)
                # Uncomment to add instant audio feedback:
                # if voice_engine and len(transcript.split()) > 3:
                #     voice_engine.speak("Processing")
                
                # Get response from JARVIS (this is the slow part - LLM API)
                response_payload = jarvis.process_input(transcript)
                response_text = response_payload.get("text", "")
                provider_name = response_payload.get("provider", "LLM")
                fallback_used = bool(response_payload.get("fallback_used"))

                label = f"[{provider_name}] " if provider_name else ""
                log(f"Jarvis {label}{response_text}\n", "jarvis")
                
                # Don't announce fallback - just work silently
                # if fallback_used:
                #     log("Primary LLM unavailable, switched to fallback provider.\n", "info")

                ready_status = f"Ready. Active model: {provider_name}" if provider_name else "Ready."
                update_status(ready_status)

                # Show response on display while speaking
                try:
                    from tools.display_response import show_speaking, show_response
                    show_speaking()
                    # Display response text in parallel with speech
                    import threading
                    display_thread = threading.Thread(
                        target=lambda: show_response(response_text, duration=8.0, scroll=True),
                        daemon=True
                    )
                    display_thread.start()
                except:
                    pass

                # SPEAK the response (TTS generation happens here)
                if voice_engine and response_text:
                    # Don't prefix with provider name in fallback
                    voice_engine.speak(response_text)
                    
            except Exception as e:
                error_msg = f"Error processing voice input: {e}"
                log(f"{error_msg}\n", "error")
                if voice_engine:
                    voice_engine.speak("Sorry Sir, I encountered an error processing that.")

        # --- Voice Engine Initialization ---
        try:
            log("Initializing Voice Engine...\n")
            voice_engine = VoiceEngine(
                wake_word=None,  # Continuous listening mode - no wake word needed
                wake_word_activation_callback=jarvis.activate_listening,
                transcript_callback=voice_input_handler  # Use wrapper that speaks responses
            )
            voice_engine.set_ui_update_callback(lambda status: ui_queue.put(("voice_status", status)))
            voice_engine.start()
            log("Voice Engine is running in continuous mode.\n", "info")
            update_status("Ready. Speak directly (no wake word needed).")
        except Exception as e:
            log(f"Error initializing Voice Engine: {e}\n", "error")
            log("Continuing with text-only input.\n", "info")
            update_status("Ready (text-only).")

        # --- Main Execution Loop ---
        startup_script = greeting_manager.build_startup_greeting()
        startup_text = startup_script.speech_text() or "Jarvis is online."
        log(f"Jarvis {startup_text}\n", "jarvis")

        if voice_engine:
            for line in startup_script.speech_lines:
                try:
                    voice_engine.speak(line)
                except Exception as speak_err:
                    log(f"Startup greeting speech error: {speak_err}\n", "warning")
                    break

        try:
            from actuators.display import display
            display.clear()
            for row, text in enumerate(startup_script.display_lines[:2]):
                text = text[:16]
                col = max(0, (16 - len(text)) // 2)
                display.write_text(text, row=row, col=col)
            try:
                display.show_face('happy')
            except Exception:
                pass
            time.sleep(1)
            try:
                display.show_face('neutral')
            except Exception:
                pass
            if not getattr(display, "simulation_mode", True):
                try:
                    display.start_idle_animation()
                except Exception:
                    pass
        except Exception as disp_err:
            log(f"Startup greeting display warning: {disp_err}\n", "warning")

        update_status(startup_script.status_line)
        
        while True:
            try:
                user_input = user_input_queue.get(timeout=1.0)
                if user_input:
                    log(f"Processing: '{user_input}'\n", "info")
                    update_status("Thinking...")
                    response_payload = jarvis.get_response(user_input)
                    response_text = response_payload.get("text", "")
                    provider_name = response_payload.get("provider", "LLM")
                    fallback_used = bool(response_payload.get("fallback_used"))

                    label = f"[{provider_name}] " if provider_name else ""
                    log(f"Jarvis {label}{response_text}\n", "jarvis")
                    # Don't announce fallback
                    # if fallback_used:
                    #     log("Primary LLM unavailable, switched to fallback provider.\n", "info")

                    ready_status = (
                        f"Ready. Active model: {provider_name}"
                        if provider_name
                        else "Ready."
                    )
                    update_status(ready_status)

                    if voice_engine and response_text:
                        # Don't prefix with provider name in fallback
                        voice_engine.speak(response_text)
            except queue.Empty:
                continue  # Loop continues, allows checking for other conditions if needed
            except KeyboardInterrupt:
                log("Shutdown signal received in main loop.\n", "info")
                break
            except Exception as e:
                error_info = traceback.format_exc()
                log(f"An unexpected error occurred in the main loop: {e}\n", "error")
                log(f"Traceback:\n{error_info}\n", "error")
                time.sleep(2)

    except Exception as e:
        # Catch errors during the entire initialization phase
        error_info = traceback.format_exc()
        log(f"Failed to initialize J.A.R.V.I.S. core: {e}\n", "error")
        log(f"Traceback:\n{error_info}\n", "error")
        update_status("Fatal Error. Check logs.")

    finally:
        # --- Universal Cleanup ---
        # CRITICAL: Cleanup order matters! Hardware that depends on GPIO/pigpio
        # must be cleaned BEFORE we tear down the underlying GPIO/pigpio systems.
        log("J.A.R.V.I.S. is shutting down...\n", "info")
        
        # Step 1: Stop voice engine (audio/speech)
        try:
            if voice_engine:
                voice_engine.stop()
                log("Voice engine stopped.\n", "info")
        except Exception as e:
            log(f"Error stopping voice engine: {e}\n", "error")
        
        # Step 2: Cleanup Jarvis core
        try:
            if jarvis:
                jarvis.cleanup()
                log("Jarvis core cleaned up.\n", "info")
        except Exception as e:
            log(f"Error cleaning up Jarvis core: {e}\n", "error")
        
        # Step 3: Stop sensors (uses GPIO)
        try:
            if sensor_manager:
                sensor_manager.stop()
                log("Sensors stopped.\n", "info")
        except Exception as e:
            log(f"Error stopping sensors: {e}\n", "error")
        
        # Step 4: Cleanup motor controller (uses GPIO/PWM)
        try:
            import sys as _sys
            if 'tools.motor_tools' in _sys.modules:
                _motor_tools = _sys.modules.get('tools.motor_tools')
                if _motor_tools is not None and hasattr(_motor_tools, 'motor_controller'):
                    try:
                        _motor_tools.motor_controller.cleanup()
                        log("Motor controller cleaned up.\n", "info")
                    except Exception as _m_e:
                        log(f"Motor controller cleanup warning: {_m_e}\n", "error")
        except Exception as e:
            log(f"Error cleaning up motor controller: {e}\n", "error")
        
        # Step 5: Cleanup display (uses GPIO/I2C)
        try:
            import sys as _sys
            if 'actuators.display' in _sys.modules:
                _display_mod = _sys.modules.get('actuators.display')
                if _display_mod is not None and hasattr(_display_mod, 'display'):
                    try:
                        _display_mod.display.cleanup()
                        log("Display cleaned up.\n", "info")
                    except Exception as _d_e:
                        log(f"Display cleanup warning: {_d_e}\n", "error")
        except Exception as e:
            log(f"Error cleaning up display: {e}\n", "error")
        
        # Step 6: Finally cleanup servos (closes pigpio connection)
        # Servos use pigpio, NOT RPi.GPIO, so they're independent
        try:
            multi_servo_controller.cleanup()
            log("Servos cleaned up.\n", "info")
        except Exception as e:
            log(f"Error cleaning up servos: {e}\n", "error")
        
        # Step 7: LAST - Cleanup GPIO (after all GPIO-using hardware is done)
        try:
            if hardware_manager:
                hardware_manager.cleanup()
                log("Hardware manager (GPIO) cleaned up.\n", "info")
        except Exception as e:
            log(f"Error cleaning up hardware manager: {e}\n", "error")
        
        log("J.A.R.V.I.S. has shut down.\n", "info")
        ui_queue.put(("exit", None))


def main():
    """Main function to create and run the Tkinter application."""
    root = tk.Tk()
    app = JarvisApp(root)
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\nShutdown requested by user.")
    finally:
        # The cleanup logic is now primarily in init_and_run_jarvis_core's finally block
        # but we ensure the app closes gracefully.
        if app.jarvis_thread and app.jarvis_thread.is_alive():
            # Ideally, we'd have a more graceful shutdown mechanism
            # For now, we rely on the daemon thread property
            pass
        print("Application closed.")

if __name__ == "__main__":
    main()