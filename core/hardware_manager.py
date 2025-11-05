"""Minimal Hardware Manager

Provides a single location to expose a `simulation_mode` flag for code that
previously depended on centralized GPIO initialization. We intentionally do
NOT globally set up or clean up RPi.GPIO here anymore because the servo has
been migrated to `pigpio` (which manages its own daemon) and other sensors
either simulate or manage their own lightweight setup.

If RPi.GPIO cannot be imported (e.g. running on a dev machine), we enter
simulation mode so higher‑level logic can still execute without crashing.
"""

from dataclasses import dataclass
import os

try:
	import RPi.GPIO as GPIO  # type: ignore
except Exception:  # pragma: no cover
	GPIO = None

@dataclass
class HardwareManager:
	simulation_mode: bool = False

	def __post_init__(self):
		# Explicit override via environment
		force_sim = os.getenv('FORCE_SIMULATION')
		if force_sim and force_sim not in ('0', 'false', 'False', 'no', 'NO'):
			self.simulation_mode = True
			print('[HardwareManager] FORCE_SIMULATION active.')
			return
		if GPIO is None:
			self.simulation_mode = True
			return
		# Attempt to set BCM mode if not already set
		try:
			current_mode = GPIO.getmode()
			if current_mode is None:
				GPIO.setmode(GPIO.BCM)
				print("[HardwareManager] GPIO mode set to BCM.")
		except Exception:
			self.simulation_mode = True
			return

	def cleanup(self):
		"""Clean up GPIO resources when running on real hardware."""
		if GPIO is None or self.simulation_mode:
			return
		try:
			GPIO.cleanup()
			print("[HardwareManager] GPIO cleanup complete.")
		except Exception as exc:  # pragma: no cover - hardware dependent
			print(f"[HardwareManager] GPIO cleanup warning: {exc}")

# Export singleton
hardware_manager = HardwareManager()

