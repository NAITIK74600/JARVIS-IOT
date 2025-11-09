"""
DHT Temperature and Humidity Sensor
Supports DHT11 and DHT22 sensors using adafruit_dht library
"""
import time
import board
import adafruit_dht


class DHT:
    """
    DHT sensor wrapper for JARVIS
    Provides temperature and humidity readings
    """
    
    def __init__(self, pin=4, sensor_type='DHT11'):
        """
        Initialize DHT sensor
        
        Args:
            pin (int): BCM GPIO pin number (default: 4)
            sensor_type (str): 'DHT11' or 'DHT22' (default: 'DHT11')
        """
        self.pin = pin
        self.sensor_type = sensor_type.upper()
        
        # Map BCM pin to board pin
        pin_map = {
            4: board.D4,
            17: board.D17,
            18: board.D18,
            22: board.D22,
            23: board.D23,
            24: board.D24,
            25: board.D25,
            27: board.D27,
        }
        
        if pin not in pin_map:
            raise ValueError(f"Pin {pin} not supported. Use one of: {list(pin_map.keys())}")
        
        board_pin = pin_map[pin]
        
        # Initialize the appropriate sensor
        if self.sensor_type == 'DHT11':
            self.device = adafruit_dht.DHT11(board_pin)
        elif self.sensor_type == 'DHT22':
            self.device = adafruit_dht.DHT22(board_pin)
        else:
            raise ValueError(f"Unsupported sensor type: {sensor_type}. Use 'DHT11' or 'DHT22'")
        
        print(f"DHT sensor initialized: {sensor_type} on BCM pin {pin}")
        
        # Cache for reducing sensor reads
        self._last_reading_time = 0
        self._cached_temp = None
        self._cached_humidity = None
        self._cache_duration = 2.0  # seconds
    
    def _read_sensor(self):
        """
        Internal method to read from sensor with caching
        Returns: (temperature_c, humidity_percent) or (None, None) on error
        """
        current_time = time.time()
        
        # Return cached values if recent enough
        if current_time - self._last_reading_time < self._cache_duration:
            return self._cached_temp, self._cached_humidity
        
        try:
            temperature_c = self.device.temperature
            humidity = self.device.humidity
            
            # Update cache if reading successful
            if temperature_c is not None and humidity is not None:
                self._cached_temp = temperature_c
                self._cached_humidity = humidity
                self._last_reading_time = current_time
                return temperature_c, humidity
            else:
                return None, None
                
        except RuntimeError as e:
            # DHT sensors often throw RuntimeError - this is normal
            # Return cached values if available, otherwise None
            if self._cached_temp is not None:
                return self._cached_temp, self._cached_humidity
            return None, None
        except Exception as e:
            print(f"DHT sensor error: {e}")
            return None, None
    
    def read_temperature(self):
        """
        Read temperature in Celsius
        Returns: float or None
        """
        temp, _ = self._read_sensor()
        return temp
    
    def read_humidity(self):
        """
        Read humidity percentage
        Returns: float or None
        """
        _, humidity = self._read_sensor()
        return humidity
    
    def read_both(self):
        """
        Read both temperature and humidity
        Returns: dict with 'temperature_c' and 'humidity_percent' keys
        """
        temp, humidity = self._read_sensor()
        return {
            'temperature_c': temp,
            'humidity_percent': humidity
        }
    
    def close(self):
        """Clean up sensor resources"""
        try:
            self.device.exit()
        except Exception:
            pass


# Test code
if __name__ == "__main__":
    print("DHT Sensor Test")
    print("Reading from DHT11 sensor on GPIO4... Press Ctrl+C to exit.")
    print()
    
    sensor = DHT(pin=4, sensor_type='DHT11')
    
    try:
        while True:
            temp = sensor.read_temperature()
            humidity = sensor.read_humidity()
            
            if temp is not None and humidity is not None:
                temp_f = temp * (9/5) + 32
                print(f"Temp: {temp_f:.1f}°F / {temp:.1f}°C    Humidity: {humidity:.0f}%")
            else:
                print("Failed to get reading. Trying again...")
            
            time.sleep(2.0)
            
    except KeyboardInterrupt:
        print("\nTest stopped by user")
    finally:
        sensor.close()
        print("Sensor closed")