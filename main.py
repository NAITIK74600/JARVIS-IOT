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

# Provide a lightweight fallback `tool` decorator so code using `@tool` does not
# crash at import time if LangChain isn't available yet. When LangChain is
# imported later, its `tool` can replace this behavior for full integration.
from langchain.agents import tool

# --- Load environment variables from .env file ---
load_dotenv()
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
last_scan_result = None

# The old single servo instance is now replaced by the multi_servo_controller
# servo = None
# servo_lock = None

@tool
def scan_environment(_: str = "") -> str:
    """Performs a standard head sweep using the 'neck' servo to find the safest direction."""
    global last_scan_result
    neck_servo = multi_servo_controller.get_servo('neck')
    if not (neck_servo and sensor_manager):
        return "Scanning unavailable: Neck servo or sensor manager not detected."
    
    lock = multi_servo_controller.get_lock('neck')
    if not lock.acquire(blocking=False):
        return "Neck servo is busy. Try again shortly."
    
    try:
        scan = perform_scan(neck_servo, sensor_manager)
        last_scan_result = scan
        return human_readable_summary(scan)
    finally:
        lock.release()

@tool
def scan_environment_custom(params: str) -> str:
    """Perform a customized scan with the 'neck' servo. Input format: start,end,step (e.g. '40,140,20')."""
    global last_scan_result
    neck_servo = multi_servo_controller.get_servo('neck')
    if not (neck_servo and sensor_manager):
        return "Scanning unavailable: Neck servo or sensor manager not detected."
        
    lock = multi_servo_controller.get_lock('neck')
    if not lock.acquire(blocking=False):
        return "Neck servo is busy. Try again shortly."
        
    try:
        try:
            parts = [int(p.strip()) for p in params.split(',') if p.strip()]
            if len(parts) != 3:
                return "Invalid format. Use start,end,step (e.g. 40,140,20)"
            s, e, st = parts
            scan = perform_scan(neck_servo, sensor_manager, start_angle=s, end_angle=e, step=st)
            last_scan_result = scan
            return human_readable_summary(scan)
        except ValueError:
            return "Invalid numbers. Please provide three integers: start,end,step."
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


# --- Sensor Manager ---
import traceback as _traceback
try:
    from sensors.sensor_manager import SensorManager
    sensor_manager = SensorManager()
    sensor_manager.start()
except ImportError as _sensor_import_err:
    print("[ERROR] Sensor modules not found. Jarvis will run in limited mode. Please check your sensor wiring and Python dependencies.")
    print(_traceback.format_exc())
    sensor_manager = None
except Exception as _sensor_init_err:
    print(f"[ERROR] Failed to initialize sensors: {_sensor_init_err}\nThis may be due to missing hardware, incorrect pin configuration, or missing dependencies. See the troubleshooting section in the README.")
    print(_traceback.format_exc())
    sensor_manager = None


# --- J.A.R.V.I.S. Custom Tools ---
# --- Core Voice Engine ---
from core.voice_engine import VoiceEngine, list_audio_devices
from core.hardware_manager import hardware_manager
from core.llm_manager import LLMManager, ProviderUnavailable
from core.offline_responder import OfflineResponder
from tools.motor_tools import move_forward, move_backward, turn_left, turn_right, stop_moving


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

    def process_ui_queue(self):
        """Processes messages from the Jarvis core to update the UI."""
        try:
            while not self.ui_queue.empty():
                message_type, payload = self.ui_queue.get_nowait()
                if message_type == "log":
                    self.log_message(payload['msg'], payload.get('tag'))
                elif message_type == "status":
                    self.update_status(payload)
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

    def update_status(status):
        ui_queue.put(("status", status))

    try:
        # --- Initialize Display First ---
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
        from tools.ir_tools import ir_list_remotes, ir_list_commands, ir_send_command, ir_learn_command

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

        # --- Initialize Memory ---
        memory = JarvisMemory()

        # --- Tool Aggregation ---
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
            display_text, clear_display, show_face,
            ir_list_remotes, ir_list_commands, ir_send_command, ir_learn_command,
            move_forward, move_backward, turn_left, turn_right, stop_moving,
        ]
        all_tools.extend(all_robot_tools)

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

        # --- Voice Engine Initialization ---
        try:
            log("Initializing Voice Engine...\n")
            voice_engine = VoiceEngine(
                wake_word="jarvis",
                wake_word_activation_callback=jarvis.activate_listening,
                transcript_callback=jarvis.process_input
            )
            voice_engine.start()
            log("Voice Engine is running.\n", "info")
            update_status("Ready. Say 'Jarvis' to activate.")
        except Exception as e:
            log(f"Error initializing Voice Engine: {e}\n", "error")
            log("Continuing with text-only input.\n", "info")
            update_status("Ready (text-only).")

        # --- Main Execution Loop ---
        log(f"J.A.R.V.I.S. is online. Hello, {user_name}.\n", "jarvis")
        
        # Update display - System Ready
        try:
            from actuators.display import display
            display.clear()
            display.write_text("JARVIS Online", row=0, col=2)
            display.write_text("Ready", row=1, col=5)
            time.sleep(1)
            display.show_face('neutral')
        except:
            pass
        
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
                    if fallback_used:
                        log("Primary LLM unavailable, switched to fallback provider.\n", "info")

                    ready_status = (
                        f"Ready. Active model: {provider_name}"
                        if provider_name
                        else "Ready."
                    )
                    update_status(ready_status)

                    if voice_engine and response_text:
                        spoken = response_text
                        if fallback_used:
                            spoken = f"Switching to {provider_name}. {response_text}"
                        voice_engine.speak(spoken)
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