"""
Tools for interacting with Infrared (IR) devices.
"""
from langchain.tools import tool
from actuators.ir_emitter import IREmitter
import json
import os
import subprocess
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict

# Singleton instances
ir_emitter = IREmitter()

BASE_DIR = Path(__file__).resolve().parent.parent
IR_STORAGE_DIR = BASE_DIR / "data" / "ir_signals"
IR_STORAGE_DIR.mkdir(parents=True, exist_ok=True)
IR_METADATA_PATH = IR_STORAGE_DIR / "signals.json"

DEFAULT_IR_DEVICE = os.getenv("JARVIS_IR_DEVICE", "/dev/lirc0")
DEFAULT_IR_CARRIER = int(os.getenv("JARVIS_IR_CARRIER", "38000"))
DEFAULT_IR_DUTY = int(os.getenv("JARVIS_IR_DUTY", "33"))


def _slugify(name: str) -> str:
    cleaned = [c.lower() if c.isalnum() else "_" for c in name]
    slug = "".join(cleaned).strip("_")
    return slug or "signal"


class IRSignalStore:
    """Manage saving, listing, and replaying ad-hoc IR signals."""

    def __init__(self, device: str = DEFAULT_IR_DEVICE):
        self.device = device
        self.storage_dir = IR_STORAGE_DIR
        self.metadata_path = IR_METADATA_PATH
        self.default_carrier = DEFAULT_IR_CARRIER
        self.default_duty = DEFAULT_IR_DUTY
        self.lock = threading.Lock()
        self.signals: Dict[str, Dict[str, object]] = self._load_metadata()

    def _load_metadata(self) -> Dict[str, Dict[str, object]]:
        if not self.metadata_path.exists():
            return {}
        try:
            return json.loads(self.metadata_path.read_text())
        except Exception:
            return {}

    def _save_metadata(self) -> None:
        self.metadata_path.write_text(
            json.dumps(self.signals, indent=2, sort_keys=True)
        )

    def record_signal(self, friendly_name: str, timeout_s: int = 8) -> str:
        slug = _slugify(friendly_name)
        temp_path = self.storage_dir / f"{slug}.tmp"
        final_path = self.storage_dir / f"{slug}.ir"
        timeout_us = max(1, int(timeout_s * 1_000_000))

        with self.lock:
            if temp_path.exists():
                temp_path.unlink()

            print("\n" + "=" * 60)
            print(f" IR capture ready: {friendly_name}")
            print(" Point the remote at the sensor and press the button once.")
            print(f" Capture times out after about {timeout_s} seconds.")
            print("=" * 60 + "\n")

            cmd = [
                "ir-ctl",
                f"--device={self.device}",
                f"--receive={temp_path}",
                "--one-shot",
                f"--timeout={timeout_us}",
                "--mode2",
                "--measure-carrier",
            ]

            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    check=True,
                )
            except FileNotFoundError:
                return "ir-ctl command not found. Install the v4l-utils package and retry."
            except subprocess.CalledProcessError as exc:
                stderr = exc.stderr.strip() if exc.stderr else "Unknown error"
                return f"Failed to capture IR signal: {stderr}"

            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(result.stderr)

            if not temp_path.exists() or temp_path.stat().st_size == 0:
                if temp_path.exists():
                    temp_path.unlink()
                return "No IR signal detected. Please press the remote button and try again."

            raw_lines = temp_path.read_text().strip().splitlines()
            if not any(line.startswith("pulse") for line in raw_lines):
                temp_path.unlink()
                return "Captured data did not contain a valid IR pulse. Try again."

            carrier = None
            duty = None
            for line in raw_lines:
                parts = line.split()
                if len(parts) >= 3 and parts[0] == "#" and parts[1] == "carrier":
                    try:
                        carrier = int(parts[2])
                    except ValueError:
                        carrier = None
                if len(parts) >= 3 and parts[0] == "#" and parts[1] == "duty_cycle":
                    try:
                        duty = int(parts[2])
                    except ValueError:
                        duty = None

            if final_path.exists():
                final_path.unlink()
            temp_path.replace(final_path)

            self.signals[slug] = {
                "name": friendly_name,
                "file": final_path.name,
                "carrier": carrier,
                "duty_cycle": duty,
                "created_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
            }
            self._save_metadata()

        return f"Saved IR signal '{friendly_name}'."

    def send_signal(self, friendly_name: str) -> str:
        slug = _slugify(friendly_name)
        with self.lock:
            entry = self.signals.get(slug)

        if not entry:
            return f"No IR signal stored for '{friendly_name}'."

        file_path = self.storage_dir / entry.get("file", "")
        if not file_path.exists():
            return f"Saved IR waveform for '{friendly_name}' is missing. Re-record it."

        carrier = entry.get("carrier") or self.default_carrier
        duty = entry.get("duty_cycle") or self.default_duty

        cmd = [
            "ir-ctl",
            f"--device={self.device}",
            f"--send={file_path}",
            f"--carrier={carrier}",
            f"--duty-cycle={duty}",
        ]

        try:
            subprocess.run(cmd, capture_output=True, text=True, check=True)
        except FileNotFoundError:
            return "ir-ctl command not found. Install the v4l-utils package and retry."
        except subprocess.CalledProcessError as exc:
            stderr = exc.stderr.strip() if exc.stderr else "Unknown error"
            return f"Failed to send IR signal '{friendly_name}': {stderr}"

        return f"Firing IR signal '{friendly_name}'."

    def list_signals(self) -> str:
        with self.lock:
            if not self.signals:
                return "No IR signals saved yet."
            names = sorted(entry["name"] for entry in self.signals.values())
        return "Saved IR signals: " + ", ".join(names)

    def delete_signal(self, friendly_name: str) -> str:
        slug = _slugify(friendly_name)
        with self.lock:
            entry = self.signals.pop(slug, None)
            if entry is None:
                return f"No saved signal named '{friendly_name}'."
            self._save_metadata()

        file_path = self.storage_dir / entry.get("file", "")
        if file_path.exists():
            file_path.unlink()

        return f"Deleted IR signal '{friendly_name}'."


ir_signal_store = IRSignalStore()


# --- IR Emitter Tools ---

@tool("ir_list_remotes", return_direct=True)
def ir_list_remotes(_) -> str:
    """
    Lists all configured IR remote controls that Jarvis can use to send commands.
    """
    remotes = ir_emitter.list_remotes()
    if not remotes:
        return "No IR remotes are configured yet. Use `ir_learn_command` to add one."
    return "Available remotes: " + ", ".join(remotes)

@tool("ir_list_commands", return_direct=True)
def ir_list_commands(remote_name: str) -> str:
    """
    Lists the available commands for a specific IR remote.
    - remote_name (str): The name of the remote to query.
    """
    commands = ir_emitter.list_commands(remote_name)
    if not commands:
        return f"No commands found for remote '{remote_name}', or the remote does not exist."
    return f"Available commands for {remote_name}: " + ", ".join(commands)

@tool("ir_send_command", return_direct=True)
def ir_send_command(command_str: str) -> str:
    """
    Sends an IR command. The input must be a string with the remote name and the command name, separated by a comma.
    For example: 'TV, KEY_POWER'.
    """
    parts = command_str.split(",")
    if len(parts) != 2:
        return "Invalid format. Please provide the remote name and command, separated by a comma (e.g., 'TV, KEY_POWER')."

    remote_name = parts[0].strip()
    command_name = parts[1].strip()

    success, message = ir_emitter.send_once(remote_name, command_name)
    return message

@tool("ir_learn_command", return_direct=True)
def ir_learn_command(command_str: str) -> str:
    """
    Starts the interactive process to learn a new IR command. The input must be a string with the new remote name and command name, separated by a comma.
    For example: 'Stereo, KEY_MUTE'.
    This requires the user to be physically present to press the remote button.
    """
    parts = command_str.split(",")
    if len(parts) != 2:
        return "Invalid format. Please provide the remote name and command, separated by a comma (e.g., 'Stereo, KEY_MUTE')."

    remote_name = parts[0].strip()
    command_name = parts[1].strip()

    print("\n" + "=" * 50)
    print("  Starting IR Learning Mode via `irrecord`")
    print("  You must follow the prompts in this terminal.")
    print(f"  Learning command '{command_name}' for remote '{remote_name}'.")
    print("=" * 50 + "\n")

    success, message = ir_emitter.learn_command(remote_name, command_name)

    print("\n" + "=" * 50)
    print("  Exited IR Learning Mode")
    print(f"  Result: {message}")
    print("=" * 50 + "\n")

    return f"Learning process finished. Result: {message}"


@tool("ir_record_signal", return_direct=True)
def ir_record_signal(name: str) -> str:
    """Record an IR signal (e.g. car unlock, TV power) and store it under the spoken name."""
    if not name or not name.strip():
        return "Please provide a name for the IR signal you want to save."
    return ir_signal_store.record_signal(name.strip())


@tool("ir_send_saved_signal", return_direct=True)
def ir_send_saved_signal(name: str) -> str:
    """Replay a previously saved IR signal when the user asks to trigger it (e.g. 'unlock car jarvis')."""
    if not name or not name.strip():
        return "Please tell me which saved IR signal to send."
    return ir_signal_store.send_signal(name.strip())


@tool("ir_list_saved_signals", return_direct=True)
def ir_list_saved_signals(_: str = "") -> str:
    """List the names of saved IR signals so the user knows what can be triggered later."""
    return ir_signal_store.list_signals()


@tool("ir_delete_signal", return_direct=True)
def ir_delete_signal(name: str) -> str:
    """Delete a saved IR signal so it can be re-recorded or forgotten."""
    if not name or not name.strip():
        return "Please provide the name of the saved IR signal to delete."
    return ir_signal_store.delete_signal(name.strip())
