"""DHT sensor abstraction with dual backend support.

Primary backend: legacy Adafruit_DHT (fast retry helper) 
Fallback backend: CircuitPython adafruit_dht (works when legacy cannot detect platform)

Environment variables:
  DHT_TYPE=11|22 selects DHT11 or DHT22 (default 11)
  DHT_BACKEND=legacy|circuitpython forces backend choice (optional)

Notes:
  The legacy library sometimes raises RuntimeError("Unknown platform.") on certain
  Python or OS combinations. In that case we transparently fall back.
"""

from core.hardware_manager import hardware_manager
import random
import os
import time

try:
    import Adafruit_DHT  # Legacy backend
    _HAVE_LEGACY = True
except Exception as e:  # noqa: BLE001 - broad to allow fallback
    Adafruit_DHT = None
    _HAVE_LEGACY = False
    _LEGACY_IMPORT_ERROR = e

_HAVE_CIRCUITPY = False
_CIRCUITPY_IMPORT_ERROR = None
try:
    import adafruit_dht  # type: ignore
    import board  # type: ignore
    _HAVE_CIRCUITPY = True
except Exception as e:  # noqa: BLE001
    _CIRCUITPY_IMPORT_ERROR = e

def _select_board_pin(bcm_pin: int):
    """Map BCM pin number to board pin object for CircuitPython if possible.

    For most Raspberry Pi boards, board.D{pin} where pin is the BCM number exists.
    We attempt dynamic attribute access; if it fails we raise to allow simulation fallback.
    """
    attr = f"D{bcm_pin}"
    if hasattr(board, attr):  # type: ignore
        return getattr(board, attr)  # type: ignore
    # Some older naming might just be board.D4 etc; if not present we raise.
    raise AttributeError(f"board does not expose attribute {attr} for BCM pin {bcm_pin}")

class DHT:
    """
    A class to interact with a DHT11 or DHT22 temperature and humidity sensor.
    """
    def __init__(self, pin, sensor_type=None):
        """
        Initializes the DHT sensor.

        Args:
            pin (int): The BCM GPIO pin number the sensor's data line is connected to.
            sensor_type (str): The type of sensor, either 'DHT11' or 'DHT22'.
        """
        self.pin = pin
        self.simulation_mode = hardware_manager.simulation_mode

        # Determine target sensor type string (normalize) for both backends
        env_type = os.getenv('DHT_TYPE') if sensor_type is None else None
        chosen = sensor_type or env_type or '11'
        if isinstance(chosen, (int,)):
            chosen = str(chosen)
        chosen_l = str(chosen).strip().lower()
        if chosen_l in ('dht22', '22'):
            self.type_str = '22'
        else:
            self.type_str = '11'

        # Backend selection preference
        forced_backend = os.getenv('DHT_BACKEND')
        self.backend = None  # 'legacy' | 'circuitpython'
        self._cp_sensor = None

        if self.simulation_mode:
            self.backend = 'simulation'
        else:
            # Attempt legacy first unless forced circuitpython
            if forced_backend and forced_backend.lower() == 'circuitpython':
                self._init_circuitpython()
            else:
                if _HAVE_LEGACY:
                    try:
                        self._init_legacy()
                    except Exception:
                        # Legacy failed; try circuitpython if available or fallback to simulation
                        if forced_backend and forced_backend.lower() == 'legacy':
                            print('[DHT] Forced legacy backend failed - entering simulation mode.')
                            self.backend = 'simulation'
                        else:
                            if _HAVE_CIRCUITPY:
                                print('[DHT] Legacy backend failed, attempting CircuitPython fallback...')
                                try:
                                    self._init_circuitpython()
                                except Exception as ce:  # noqa: BLE001
                                    print(f'[DHT] CircuitPython fallback failed: {ce}. Using simulation mode.')
                                    self.backend = 'simulation'
                            else:
                                print('[DHT] Legacy backend failed & CircuitPython not available. Using simulation mode.')
                                self.backend = 'simulation'
                else:
                    if _HAVE_CIRCUITPY:
                        self._init_circuitpython()
                    else:
                        print('[DHT] No backend libraries available; using simulation mode.')
                        self.backend = 'simulation'

        print(f"[DHT] Initialized backend={self.backend} type=DHT{self.type_str} pin={self.pin}")

    def _init_legacy(self):
        if not _HAVE_LEGACY:
            raise RuntimeError(f'Legacy Adafruit_DHT import failed: {_LEGACY_IMPORT_ERROR}')
        if self.type_str == '22':
            self.sensor_type = Adafruit_DHT.DHT22
        else:
            self.sensor_type = Adafruit_DHT.DHT11
        # Test a single quick read to detect unknown platform error early
        try:
            Adafruit_DHT.read(self.sensor_type, self.pin)
        except RuntimeError as re:
            # Propagate to trigger fallback logic
            raise re
        self.backend = 'legacy'

    def _init_circuitpython(self):
        if not _HAVE_CIRCUITPY:
            raise RuntimeError(f'CircuitPython DHT import failed: {_CIRCUITPY_IMPORT_ERROR}')
        board_pin = _select_board_pin(self.pin)
        dht_cls = adafruit_dht.DHT22 if self.type_str == '22' else adafruit_dht.DHT11
        # Use use_pulseio False for Pi (less resource heavy)
        self._cp_sensor = dht_cls(board_pin, use_pulseio=False)
        self.backend = 'circuitpython'

    def _read(self):
        if self.simulation_mode or self.backend == 'simulation':
            temp = random.uniform(20, 25)
            humidity = random.uniform(40, 60)
            return humidity, temp
        if self.backend == 'legacy':
            humidity, temperature = Adafruit_DHT.read_retry(self.sensor_type, self.pin)
            return humidity, temperature
        if self.backend == 'circuitpython':
            # CircuitPython library sometimes raises RuntimeError for checksum or timing errors -> retry a few times
            last_err = None
            for _ in range(5):
                try:
                    temperature = self._cp_sensor.temperature
                    humidity = self._cp_sensor.humidity
                    if humidity is not None and temperature is not None:
                        return humidity, temperature
                except RuntimeError as e:  # transient
                    last_err = e
                    time.sleep(0.5)
            # If still failing, surface the last error but avoid crash by simulation fallback
            print(f"[DHT] CircuitPython backend read failures, last error: {last_err}. Returning None values.")
            return None, None
        # Should not reach
        return None, None

    def read_temperature(self):
        """Returns the temperature in Celsius."""
        _, temperature = self._read()
        if self.simulation_mode:
            print(f"[SIM] DHT on pin {self.pin} read temperature: {temperature:.1f}°C")
        return temperature

    def read_humidity(self):
        """Returns the humidity as a percentage."""
        humidity, _ = self._read()
        if self.simulation_mode:
            print(f"[SIM] DHT on pin {self.pin} read humidity: {humidity:.1f}%")
        return humidity

    def read_environment(self):
        """Return (temperature_c, humidity_percent) tuple."""
        h, t = self._read()
        return t, h

    def close(self):
        """Release any hardware resources held by the backend."""
        if self.backend == 'circuitpython' and self._cp_sensor is not None:
            try:
                self._cp_sensor.exit()
                print("[DHT] CircuitPython backend released.")
            except Exception as exc:
                print(f"[DHT] Warning: Failed to release CircuitPython backend: {exc}")
            finally:
                self._cp_sensor = None

# Example usage
if __name__ == '__main__':
    # Use BCM pin 25 as specified in the connection guide
    dht_sensor = DHT(pin=25, sensor_type='DHT11')
    
    for i in range(5):
        temp = dht_sensor.read_temperature()
        humidity = dht_sensor.read_humidity()
        
        if temp is not None and humidity is not None:
            print(f"Reading {i+1}: Temperature={temp}°C, Humidity={humidity}%")
        else:
            print(f"Reading {i+1}: Failed to get reading.")
        
        time.sleep(2)
