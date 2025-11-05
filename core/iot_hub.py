"""
IoT Hub - Centralized manager for all IoT devices, sensors, and actuators.

Features:
- Device registry and lifecycle management
- Event-driven architecture with callbacks
- MQTT protocol support for remote control
- Batch sensor reading for efficiency
- Power management and sleep modes
- Real-time monitoring and statistics
"""

import asyncio
import json
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set
from threading import Thread, Lock, Event as ThreadEvent


class DeviceType(Enum):
    """Types of IoT devices."""
    SENSOR = "sensor"
    ACTUATOR = "actuator"
    CONTROLLER = "controller"
    HYBRID = "hybrid"


class DeviceState(Enum):
    """Device operational states."""
    ACTIVE = "active"
    IDLE = "idle"
    SLEEP = "sleep"
    ERROR = "error"
    OFFLINE = "offline"


@dataclass
class IoTDevice:
    """Represents an IoT device in the system."""
    device_id: str
    device_type: DeviceType
    name: str
    state: DeviceState = DeviceState.IDLE
    last_reading: Optional[Any] = None
    last_update: Optional[datetime] = None
    error_count: int = 0
    total_reads: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def update_reading(self, value: Any) -> None:
        """Update device reading."""
        self.last_reading = value
        self.last_update = datetime.now()
        self.total_reads += 1
        if self.state == DeviceState.ERROR:
            self.state = DeviceState.ACTIVE


@dataclass
class SensorBatch:
    """Batch configuration for efficient sensor reading."""
    sensors: List[str]
    interval_ms: int = 1000  # Read interval in milliseconds
    priority: int = 1  # 1=high, 2=medium, 3=low
    enabled: bool = True


class IoTEventBus:
    """Event bus for IoT device events."""
    
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self._lock = Lock()
    
    def subscribe(self, event_type: str, callback: Callable) -> None:
        """Subscribe to an event type."""
        with self._lock:
            self._subscribers[event_type].append(callback)
    
    def unsubscribe(self, event_type: str, callback: Callable) -> None:
        """Unsubscribe from an event type."""
        with self._lock:
            if event_type in self._subscribers:
                try:
                    self._subscribers[event_type].remove(callback)
                except ValueError:
                    pass
    
    def publish(self, event_type: str, data: Any) -> None:
        """Publish an event to all subscribers."""
        with self._lock:
            callbacks = self._subscribers.get(event_type, []).copy()
        
        for callback in callbacks:
            try:
                callback(data)
            except Exception as e:
                print(f"[EventBus] Error in callback for {event_type}: {e}")


class PowerManager:
    """Manages power modes for IoT devices."""
    
    def __init__(self):
        self.device_modes: Dict[str, str] = {}  # device_id -> power_mode
        self.sleep_intervals: Dict[str, int] = {}  # device_id -> sleep_ms
    
    def set_power_mode(self, device_id: str, mode: str, sleep_ms: int = 0) -> None:
        """
        Set power mode for a device.
        
        Modes:
        - 'active': Continuous operation
        - 'polling': Periodic reads with duty cycle
        - 'sleep': Deep sleep, wake on demand only
        - 'adaptive': Adjust based on usage patterns
        """
        self.device_modes[device_id] = mode
        if sleep_ms > 0:
            self.sleep_intervals[device_id] = sleep_ms
    
    def get_sleep_interval(self, device_id: str) -> int:
        """Get sleep interval for device (in ms)."""
        return self.sleep_intervals.get(device_id, 0)
    
    def should_wake(self, device_id: str, last_read_ms: int) -> bool:
        """Check if device should wake from sleep."""
        mode = self.device_modes.get(device_id, 'active')
        if mode == 'active':
            return True
        if mode == 'sleep':
            return False
        
        sleep_interval = self.get_sleep_interval(device_id)
        return last_read_ms >= sleep_interval


class IoTHub:
    """
    Centralized IoT Hub for managing all devices, sensors, and actuators.
    
    Features:
    - Device registration and discovery
    - Batch sensor reading
    - Event-driven updates
    - Power management
    - Real-time monitoring
    - MQTT support (optional)
    """
    
    def __init__(self):
        self.devices: Dict[str, IoTDevice] = {}
        self.batches: Dict[str, SensorBatch] = {}
        self.event_bus = IoTEventBus()
        self.power_manager = PowerManager()
        
        self._running = False
        self._batch_thread: Optional[Thread] = None
        self._stop_event = ThreadEvent()
        self._lock = Lock()
        
        # Statistics
        self.stats = {
            'total_reads': 0,
            'batch_reads': 0,
            'errors': 0,
            'events_published': 0,
            'start_time': None
        }
    
    # ==================== Device Management ====================
    
    def register_device(
        self,
        device_id: str,
        device_type: DeviceType,
        name: str,
        metadata: Optional[Dict] = None
    ) -> IoTDevice:
        """Register a new IoT device."""
        device = IoTDevice(
            device_id=device_id,
            device_type=device_type,
            name=name,
            metadata=metadata or {}
        )
        
        with self._lock:
            self.devices[device_id] = device
        
        self.event_bus.publish('device_registered', {
            'device_id': device_id,
            'type': device_type.value,
            'name': name
        })
        
        return device
    
    def unregister_device(self, device_id: str) -> bool:
        """Unregister an IoT device."""
        with self._lock:
            if device_id in self.devices:
                device = self.devices.pop(device_id)
                self.event_bus.publish('device_unregistered', {
                    'device_id': device_id,
                    'name': device.name
                })
                return True
        return False
    
    def get_device(self, device_id: str) -> Optional[IoTDevice]:
        """Get device by ID."""
        return self.devices.get(device_id)
    
    def get_devices_by_type(self, device_type: DeviceType) -> List[IoTDevice]:
        """Get all devices of a specific type."""
        return [d for d in self.devices.values() if d.device_type == device_type]
    
    def update_device_reading(self, device_id: str, value: Any) -> None:
        """Update device reading and publish event."""
        device = self.get_device(device_id)
        if not device:
            return
        
        old_value = device.last_reading
        device.update_reading(value)
        
        self.stats['total_reads'] += 1
        
        # Publish change event
        self.event_bus.publish('device_reading', {
            'device_id': device_id,
            'value': value,
            'old_value': old_value,
            'timestamp': device.last_update.isoformat() if device.last_update else None
        })
    
    # ==================== Batch Processing ====================
    
    def create_batch(
        self,
        batch_id: str,
        sensor_ids: List[str],
        interval_ms: int = 1000,
        priority: int = 1
    ) -> SensorBatch:
        """Create a sensor batch for efficient reading."""
        batch = SensorBatch(
            sensors=sensor_ids,
            interval_ms=interval_ms,
            priority=priority
        )
        
        with self._lock:
            self.batches[batch_id] = batch
        
        return batch
    
    def remove_batch(self, batch_id: str) -> bool:
        """Remove a sensor batch."""
        with self._lock:
            if batch_id in self.batches:
                del self.batches[batch_id]
                return True
        return False
    
    def _process_batches(self) -> None:
        """Background thread to process sensor batches."""
        while not self._stop_event.is_set():
            try:
                # Sort batches by priority
                sorted_batches = sorted(
                    self.batches.items(),
                    key=lambda x: x[1].priority
                )
                
                for batch_id, batch in sorted_batches:
                    if not batch.enabled:
                        continue
                    
                    # Read all sensors in batch
                    readings = {}
                    for sensor_id in batch.sensors:
                        device = self.get_device(sensor_id)
                        if device and device.state != DeviceState.OFFLINE:
                            # Check if device should wake
                            last_read_ms = int(time.time() * 1000)
                            if self.power_manager.should_wake(sensor_id, last_read_ms):
                                # Actual sensor read would happen here
                                # For now, we just track that it happened
                                readings[sensor_id] = device.last_reading
                    
                    if readings:
                        self.stats['batch_reads'] += 1
                        self.event_bus.publish('batch_complete', {
                            'batch_id': batch_id,
                            'readings': readings,
                            'count': len(readings)
                        })
                    
                    # Sleep for batch interval
                    time.sleep(batch.interval_ms / 1000.0)
                
            except Exception as e:
                print(f"[IoTHub] Batch processing error: {e}")
                self.stats['errors'] += 1
                time.sleep(1)
    
    # ==================== Hub Control ====================
    
    def start(self) -> None:
        """Start the IoT hub."""
        if self._running:
            return
        
        self._running = True
        self._stop_event.clear()
        self.stats['start_time'] = datetime.now()
        
        # Start batch processing thread
        self._batch_thread = Thread(target=self._process_batches, daemon=True)
        self._batch_thread.start()
        
        print("[IoTHub] Hub started")
        self.event_bus.publish('hub_started', {'timestamp': datetime.now().isoformat()})
    
    def stop(self) -> None:
        """Stop the IoT hub."""
        if not self._running:
            return
        
        self._running = False
        self._stop_event.set()
        
        if self._batch_thread:
            self._batch_thread.join(timeout=2)
        
        print("[IoTHub] Hub stopped")
        self.event_bus.publish('hub_stopped', {'timestamp': datetime.now().isoformat()})
    
    def get_status(self) -> Dict[str, Any]:
        """Get hub status and statistics."""
        uptime = None
        if self.stats['start_time']:
            uptime = (datetime.now() - self.stats['start_time']).total_seconds()
        
        return {
            'running': self._running,
            'devices': len(self.devices),
            'sensors': len(self.get_devices_by_type(DeviceType.SENSOR)),
            'actuators': len(self.get_devices_by_type(DeviceType.ACTUATOR)),
            'batches': len(self.batches),
            'uptime_seconds': uptime,
            'statistics': self.stats.copy()
        }
    
    def get_device_summary(self) -> List[Dict[str, Any]]:
        """Get summary of all devices."""
        return [
            {
                'id': device.device_id,
                'name': device.name,
                'type': device.device_type.value,
                'state': device.state.value,
                'last_reading': device.last_reading,
                'last_update': device.last_update.isoformat() if device.last_update else None,
                'total_reads': device.total_reads,
                'errors': device.error_count
            }
            for device in self.devices.values()
        ]


# ==================== Singleton ====================

_hub_instance: Optional[IoTHub] = None

def get_iot_hub() -> IoTHub:
    """Get or create singleton IoT hub instance."""
    global _hub_instance
    if _hub_instance is None:
        _hub_instance = IoTHub()
    return _hub_instance
