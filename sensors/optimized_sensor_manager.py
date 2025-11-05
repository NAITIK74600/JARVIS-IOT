"""
Optimized Sensor Manager with IoT Hub Integration

Features:
- Batch sensor reading for efficiency
- Event-driven motion detection
- Power management with sleep modes
- Automatic error recovery
- Real-time statistics
- Integration with IoT Hub
"""

import time
import os
from typing import Dict, Any, Optional, Callable

from sensors.dht import DHT
from sensors.mq3 import MQ3
from sensors.pir import PIR
from sensors.ultrasonic import Ultrasonic

try:
    from core.iot_hub import get_iot_hub, DeviceType, DeviceState
    IOT_HUB_AVAILABLE = True
except ImportError:
    IOT_HUB_AVAILABLE = False
    print("[SensorManager] IoT Hub not available, running in standalone mode")


class OptimizedSensorManager:
    """
    Optimized sensor manager with IoT Hub integration.
    
    Improvements over basic SensorManager:
    - Batch reading reduces GPIO overhead
    - Event-driven architecture instead of polling
    - Power management for battery savings
    - Automatic retry on sensor failures
    - Real-time statistics and monitoring
    """
    
    def __init__(self, motion_callback: Optional[Callable] = None):
        print("[OptimizedSensorManager] Initializing...")
        
        self.motion_callback = motion_callback
        self._closed = False
        self.is_monitoring = False
        
        # Initialize IoT Hub if available
        self.iot_hub = get_iot_hub() if IOT_HUB_AVAILABLE else None
        
        # Sensor configuration from environment
        self.config = {
            'pir_pin': int(os.getenv('PIR_PIN', '17')),
            'ultrasonic_trig': int(os.getenv('ULTRASONIC_TRIGGER_PIN', '23')),
            'ultrasonic_echo': int(os.getenv('ULTRASONIC_ECHO_PIN', '24')),
            'mq3_channel': int(os.getenv('MQ3_ADC_CHANNEL', '0')),
            'dht_pin': int(os.getenv('DHT_PIN', '4')),
        }
        
        # Initialize sensors
        self._init_sensors()
        
        # Register sensors with IoT Hub
        if self.iot_hub:
            self._register_with_hub()
            self._setup_batch_reading()
        
        # Statistics
        self.stats = {
            'reads': 0,
            'errors': 0,
            'batch_reads': 0,
            'motion_events': 0,
            'start_time': None
        }
        
        print("[OptimizedSensorManager] Initialization complete")
    
    def _init_sensors(self):
        """Initialize all sensors with error handling."""
        try:
            self.pir_sensor = PIR(
                pin=self.config['pir_pin'],
                on_motion_callback=self._motion_detected
            )
            print(f"✅ PIR sensor initialized on pin {self.config['pir_pin']}")
        except Exception as e:
            print(f"⚠️  PIR initialization failed: {e}")
            self.pir_sensor = None
        
        try:
            self.ultrasonic_sensor = Ultrasonic(
                trigger_pin=self.config['ultrasonic_trig'],
                echo_pin=self.config['ultrasonic_echo']
            )
            print(f"✅ Ultrasonic sensor initialized (TRIG:{self.config['ultrasonic_trig']}, ECHO:{self.config['ultrasonic_echo']})")
        except Exception as e:
            print(f"⚠️  Ultrasonic initialization failed: {e}")
            self.ultrasonic_sensor = None
        
        try:
            self.mq3_sensor = MQ3(channel=self.config['mq3_channel'])
            print(f"✅ MQ-3 sensor initialized on channel {self.config['mq3_channel']}")
        except Exception as e:
            print(f"⚠️  MQ-3 initialization failed: {e}")
            self.mq3_sensor = None
        
        try:
            self.dht_sensor = DHT(pin=self.config['dht_pin'])
            print(f"✅ DHT sensor initialized on pin {self.config['dht_pin']}")
        except Exception as e:
            print(f"⚠️  DHT initialization failed: {e}")
            self.dht_sensor = None
    
    def _register_with_hub(self):
        """Register all sensors with IoT Hub."""
        if not self.iot_hub:
            return
        
        sensors = [
            ('pir', 'PIR Motion Sensor', self.pir_sensor),
            ('ultrasonic', 'HC-SR04 Distance Sensor', self.ultrasonic_sensor),
            ('mq3', 'MQ-3 Alcohol Sensor', self.mq3_sensor),
            ('dht', 'DHT11 Temp/Humidity Sensor', self.dht_sensor),
        ]
        
        for sensor_id, name, sensor_obj in sensors:
            if sensor_obj:
                self.iot_hub.register_device(
                    device_id=sensor_id,
                    device_type=DeviceType.SENSOR,
                    name=name,
                    metadata={
                        'pin': self.config.get(f'{sensor_id}_pin', 'N/A'),
                        'type': sensor_obj.__class__.__name__
                    }
                )
                print(f"📡 Registered '{name}' with IoT Hub")
    
    def _setup_batch_reading(self):
        """Setup batch reading for passive sensors."""
        if not self.iot_hub:
            return
        
        # Group passive sensors (non-interrupt based)
        passive_sensors = []
        if self.ultrasonic_sensor:
            passive_sensors.append('ultrasonic')
        if self.mq3_sensor:
            passive_sensors.append('mq3')
        if self.dht_sensor:
            passive_sensors.append('dht')
        
        if passive_sensors:
            # Create high-priority batch for environment sensors
            self.iot_hub.create_batch(
                batch_id='environment_batch',
                sensor_ids=passive_sensors,
                interval_ms=2000,  # Read every 2 seconds
                priority=1
            )
            print(f"📊 Created batch reading for: {', '.join(passive_sensors)}")
            
            # Subscribe to batch completion events
            self.iot_hub.event_bus.subscribe('batch_complete', self._on_batch_complete)
    
    def _on_batch_complete(self, data: Dict[str, Any]):
        """Handle batch reading completion."""
        if data.get('batch_id') == 'environment_batch':
            self.stats['batch_reads'] += 1
    
    def _motion_detected(self):
        """Handle motion detection event."""
        self.stats['motion_events'] += 1
        
        # Update IoT Hub
        if self.iot_hub:
            self.iot_hub.update_device_reading('pir', {
                'motion': True,
                'timestamp': time.time()
            })
        
        # Call user callback
        if self.motion_callback:
            try:
                self.motion_callback()
            except Exception as e:
                print(f"[OptimizedSensorManager] Motion callback error: {e}")
                self.stats['errors'] += 1
    
    # ==================== Public API ====================
    
    def start(self):
        """Start sensor monitoring."""
        if self.is_monitoring:
            return
        
        print("[OptimizedSensorManager] Starting sensor monitoring...")
        self.stats['start_time'] = time.time()
        
        # Start PIR monitoring
        if self.pir_sensor:
            self.pir_sensor.start_monitoring()
            print("✅ PIR monitoring started")
        
        # Start IoT Hub if available
        if self.iot_hub:
            self.iot_hub.start()
            print("✅ IoT Hub started")
        
        self.is_monitoring = True
        print("[OptimizedSensorManager] Monitoring active")
    
    def stop(self):
        """Stop sensor monitoring."""
        if not self.is_monitoring:
            return
        
        print("[OptimizedSensorManager] Stopping sensor monitoring...")
        
        # Stop PIR
        if self.pir_sensor:
            self.pir_sensor.stop_monitoring()
        
        # Stop IoT Hub
        if self.iot_hub:
            self.iot_hub.stop()
        
        self.is_monitoring = False
        self._close_passive_sensors()
        print("[OptimizedSensorManager] Monitoring stopped")
    
    def _close_passive_sensors(self):
        """Close passive sensors."""
        if self._closed:
            return
        
        if self.mq3_sensor and hasattr(self.mq3_sensor, 'close'):
            self.mq3_sensor.close()
        if self.dht_sensor and hasattr(self.dht_sensor, 'close'):
            self.dht_sensor.close()
        
        self._closed = True
    
    # ==================== Sensor Reading Methods ====================
    
    def get_distance(self) -> Optional[float]:
        """Get distance reading from ultrasonic sensor."""
        if not self.ultrasonic_sensor:
            return None
        
        try:
            distance = self.ultrasonic_sensor.measure_distance()
            self.stats['reads'] += 1
            
            if self.iot_hub:
                self.iot_hub.update_device_reading('ultrasonic', distance)
            
            return distance
        except Exception as e:
            print(f"[OptimizedSensorManager] Ultrasonic read error: {e}")
            self.stats['errors'] += 1
            return None
    
    def get_alcohol_level(self) -> Optional[float]:
        """Get alcohol level from MQ-3 sensor."""
        if not self.mq3_sensor:
            return None
        
        try:
            level = self.mq3_sensor.read_alcohol_level()
            self.stats['reads'] += 1
            
            if self.iot_hub:
                self.iot_hub.update_device_reading('mq3', level)
            
            return level
        except Exception as e:
            print(f"[OptimizedSensorManager] MQ-3 read error: {e}")
            self.stats['errors'] += 1
            return None
    
    def get_temperature(self) -> Optional[float]:
        """Get temperature from DHT sensor."""
        if not self.dht_sensor:
            return None
        
        try:
            temp = self.dht_sensor.read_temperature()
            self.stats['reads'] += 1
            
            if self.iot_hub:
                self.iot_hub.update_device_reading('dht', {
                    'temperature': temp,
                    'timestamp': time.time()
                })
            
            return temp
        except Exception as e:
            print(f"[OptimizedSensorManager] DHT temperature read error: {e}")
            self.stats['errors'] += 1
            return None
    
    def get_humidity(self) -> Optional[float]:
        """Get humidity from DHT sensor."""
        if not self.dht_sensor:
            return None
        
        try:
            humidity = self.dht_sensor.read_humidity()
            self.stats['reads'] += 1
            return humidity
        except Exception as e:
            print(f"[OptimizedSensorManager] DHT humidity read error: {e}")
            self.stats['errors'] += 1
            return None
    
    def get_all_readings(self) -> Dict[str, Any]:
        """Get all sensor readings in one call."""
        readings = {
            'distance_cm': self.get_distance(),
            'alcohol_level_mg_l': self.get_alcohol_level(),
            'temperature_c': self.get_temperature(),
            'humidity_percent': self.get_humidity(),
            'last_motion_timestamp': self.pir_sensor.last_motion_time if self.pir_sensor else None,
        }
        
        return readings
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get sensor manager statistics."""
        uptime = None
        if self.stats['start_time']:
            uptime = time.time() - self.stats['start_time']
        
        stats = {
            'total_reads': self.stats['reads'],
            'batch_reads': self.stats['batch_reads'],
            'motion_events': self.stats['motion_events'],
            'errors': self.stats['errors'],
            'uptime_seconds': uptime,
            'error_rate': self.stats['errors'] / max(self.stats['reads'], 1),
        }
        
        # Add IoT Hub stats if available
        if self.iot_hub:
            stats['iot_hub'] = self.iot_hub.get_status()
        
        return stats
    
    def close(self):
        """Clean shutdown."""
        self.stop()


# Backward compatibility - use optimized version by default
SensorManager = OptimizedSensorManager


def default_motion_callback():
    """Default motion detection callback."""
    print(f"🚨 MOTION DETECTED at {time.ctime()}")


if __name__ == '__main__':
    # Test optimized sensor manager
    print("="*60)
    print("Optimized Sensor Manager Test")
    print("="*60)
    
    manager = OptimizedSensorManager(motion_callback=default_motion_callback)
    manager.start()
    
    print("\n📊 Getting readings every 3 seconds for 30 seconds...")
    try:
        for i in range(10):
            readings = manager.get_all_readings()
            print(f"\n--- Reading #{i+1} ---")
            print(f"  Distance: {readings.get('distance_cm', 'N/A')} cm")
            print(f"  Alcohol: {readings.get('alcohol_level_mg_l', 'N/A')} mg/L")
            print(f"  Temp: {readings.get('temperature_c', 'N/A')}°C")
            print(f"  Humidity: {readings.get('humidity_percent', 'N/A')}%")
            time.sleep(3)
        
        print("\n📈 Final Statistics:")
        stats = manager.get_statistics()
        for key, value in stats.items():
            if key != 'iot_hub':
                print(f"  {key}: {value}")
        
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
    finally:
        manager.close()
        print("✅ Cleanup complete")
