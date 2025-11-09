"""
Sensor Manager
Initializes and manages all connected sensors.
Provides a single point of access to sensor data.
"""
import time
import threading
import os
from sensors.dht import DHT
from sensors.mq3 import MQ3
from sensors.pir import PIR
from sensors.ultrasonic import Ultrasonic

class SensorManager:
    def __init__(self, motion_callback=None):
        print("Initializing Sensor Manager...")
        self.motion_callback = motion_callback
        self.sensor_status = {}
        
        # PIR motion sensor (defaults to BCM 17)
        pir_pin = int(os.getenv('PIR_PIN', '17'))
        try:
            print(f"Configuring PIR sensor on BCM {pir_pin}")
            self.pir_sensor = PIR(pin=pir_pin, on_motion_callback=self._pir_motion_wrapper)
            self.sensor_status['pir'] = True
            print("✓ PIR sensor initialized")
        except Exception as e:
            print(f"✗ PIR sensor failed: {e}")
            self.pir_sensor = None
            self.sensor_status['pir'] = False

        # Ultrasonic sensor (updated pins: 27=TRIG, 22=ECHO to avoid servo conflict)
        trig_pin = int(os.getenv('ULTRASONIC_TRIGGER_PIN', '27'))
        echo_pin = int(os.getenv('ULTRASONIC_ECHO_PIN', '22'))
        try:
            print(f"Configuring ultrasonic sensor (TRIG={trig_pin}, ECHO={echo_pin})")
            self.ultrasonic_sensor = Ultrasonic(trigger_pin=trig_pin, echo_pin=echo_pin)
            self.sensor_status['ultrasonic'] = True
            print("✓ Ultrasonic sensor initialized")
        except Exception as e:
            print(f"✗ Ultrasonic sensor failed: {e}")
            self.ultrasonic_sensor = None
            self.sensor_status['ultrasonic'] = False
        
        # MQ-3 sensor (DISABLED - requires ADC/MCP3008)
        # Set MQ3_ENABLED=true in environment to enable
        if os.getenv('MQ3_ENABLED', 'false').lower() in ('true', '1', 'yes'):
            try:
                self.mq3_sensor = MQ3(channel=int(os.getenv('MQ3_ADC_CHANNEL', '0')))
                self.sensor_status['mq3'] = True
                print("✓ MQ-3 sensor initialized")
            except Exception as e:
                print(f"✗ MQ-3 sensor failed: {e}")
                self.mq3_sensor = None
                self.sensor_status['mq3'] = False
        else:
            print("⊗ MQ-3 sensor disabled (requires ADC - set MQ3_ENABLED=true to enable)")
            self.mq3_sensor = None
            self.sensor_status['mq3'] = False
        
        # DHT11 sensor
        dht_pin = int(os.getenv('DHT_PIN', '4'))
        raw_type = os.getenv('DHT_TYPE', '11')
        digits_only = ''.join(ch for ch in raw_type if ch.isdigit())
        dht_type = digits_only if digits_only in ('11', '22') else '11'
        try:
            print(f"Configuring DHT sensor on BCM {dht_pin} (type DHT{dht_type})")
            self.dht_sensor = DHT(pin=dht_pin, sensor_type=f'DHT{dht_type}')
            # Test read to verify it's actually working
            test_temp = self.dht_sensor.read_temperature()
            if test_temp is not None:
                self.sensor_status['dht'] = True
                print(f"✓ DHT sensor initialized and working (type DHT{dht_type})")
            else:
                self.sensor_status['dht'] = False
                print("⚠ DHT sensor initialized but not reading (check wiring)")
        except Exception as e:
            print(f"✗ DHT sensor failed: {e}")
            self.dht_sensor = None
            self.sensor_status['dht'] = False

        self.last_motion_time = None
        self.is_monitoring = False
        self.monitoring_thread = None
        self._closed = False
        
        # Print summary
        working = sum(self.sensor_status.values())
        total = len(self.sensor_status)
        print(f"Sensor Manager ready: {working}/{total} sensors operational")

    # --- Motion Handling ---
    def _pir_motion_wrapper(self):
        self.last_motion_time = time.time()
        if self.motion_callback:
            try:
                self.motion_callback()
            except Exception as e:
                print(f"Motion callback error: {e}")

    def set_motion_callback(self, callback):
        """Assign or replace the motion callback at runtime."""
        self.motion_callback = callback

    def start(self):
        """
        Starts all continuous monitoring sensors.
        """
        print("Starting continuous sensor monitoring...")
        if self.pir_sensor:
            self.pir_sensor.start_monitoring()
        self.is_monitoring = True
        print("Sensor Manager started.")

    def stop(self):
        """
        Stops all continuous monitoring sensors.
        """
        if self.is_monitoring:
            print("Stopping sensor monitoring...")
            if self.pir_sensor:
                self.pir_sensor.stop_monitoring()
            self.is_monitoring = False
            print("Sensor Manager stopped.")
        self._close_passive_sensors()

    def _close_passive_sensors(self):
        if self._closed:
            return
        if self.mq3_sensor and hasattr(self.mq3_sensor, "close"):
            self.mq3_sensor.close()
        if self.dht_sensor and hasattr(self.dht_sensor, "close"):
            self.dht_sensor.close()
        self._closed = True

    def get_distance(self):
        """
        Returns the distance from the ultrasonic sensor in cm.
        """
        if not self.ultrasonic_sensor:
            return None
        try:
            return self.ultrasonic_sensor.measure_distance()
        except Exception as e:
            print(f"Error reading ultrasonic: {e}")
            return None

    def get_alcohol_level(self):
        """
        Returns the alcohol level from the MQ-3 sensor.
        """
        if not self.mq3_sensor:
            return None
        try:
            return self.mq3_sensor.read_alcohol_level()
        except Exception as e:
            print(f"Error reading MQ-3: {e}")
            return None
    
    def get_temperature(self):
        """
        Returns the temperature from the DHT sensor in Celsius.
        """
        if not self.dht_sensor:
            return None
        try:
            return self.dht_sensor.read_temperature()
        except Exception as e:
            print(f"Error reading DHT temperature: {e}")
            return None

    def get_humidity(self):
        """
        Returns the humidity from the DHT sensor as a percentage.
        """
        if not self.dht_sensor:
            return None
        try:
            return self.dht_sensor.read_humidity()
        except Exception as e:
            print(f"Error reading DHT humidity: {e}")
            return None

    def get_all_readings(self):
        """
        Returns a dictionary of all current sensor readings.
        """
        readings = {
            "distance_cm": self.get_distance(),
            "alcohol_level_mg_l": self.get_alcohol_level(),
            "temperature_c": self.get_temperature(),
            "humidity_percent": self.get_humidity(),
            "last_motion_timestamp": self.pir_sensor.last_motion_time,
        }
        return readings

    def close(self):
        self.stop()

def default_motion_callback():
    """
    A default callback function for motion detection.
    """
    print(f"MOTION DETECTED at {time.ctime()}")

if __name__ == '__main__':
    # Example of how to use the SensorManager
    manager = SensorManager(motion_callback=default_motion_callback)
    manager.start()

    print("Sensor manager is running. Getting readings every 2 seconds for 30 seconds.")
    try:
        for i in range(15):
            readings = manager.get_all_readings()
            print(f"--- Readings at second {i*2} ---")
            print(f"  Distance: {readings.get('distance_cm', 'N/A'):.1f} cm")
            print(f"  Alcohol: {readings.get('alcohol_level_mg_l', 'N/A'):.2f} mg/L")
            print(f"  Temp: {readings.get('temperature_c', 'N/A'):.1f}°C")
            print(f"  Humidity: {readings.get('humidity_percent', 'N/A'):.1f}%")
            time.sleep(2)
    except KeyboardInterrupt:
        print("Interrupted by user.")
    finally:
        manager.stop()
        # The HardwareManager will handle the final GPIO.cleanup()
        print("Cleanup complete.")
