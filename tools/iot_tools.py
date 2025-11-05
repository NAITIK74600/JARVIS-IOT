"""
IoT Management Tools for JARVIS

Provides LangChain tools for monitoring and controlling IoT devices.
"""

from langchain.tools import tool
from typing import Optional


@tool
def get_iot_status(dummy: str = "") -> str:
    """
    Get IoT Hub status and statistics.
    
    Shows:
    - Number of registered devices
    - Hub uptime
    - Total sensor reads
    - Batch processing stats
    - Event counts
    
    Args:
        dummy: Not used, exists for LangChain compatibility
    
    Returns:
        Formatted IoT hub status report
    """
    try:
        from core.iot_hub import get_iot_hub
        
        hub = get_iot_hub()
        status = hub.get_status()
        
        report = f"""
🌐 **IoT Hub Status Report**

**Hub State:** {'🟢 Running' if status['running'] else '🔴 Stopped'}
**Uptime:** {status.get('uptime_seconds', 0):.1f} seconds

**Registered Devices:**
- Total: {status['devices']}
- Sensors: {status['sensors']}
- Actuators: {status['actuators']}
- Active Batches: {status['batches']}

**Statistics:**
- Total Reads: {status['statistics']['total_reads']}
- Batch Reads: {status['statistics']['batch_reads']}
- Events Published: {status['statistics']['events_published']}
- Errors: {status['statistics']['errors']}
"""
        
        return report.strip()
        
    except ImportError:
        return "IoT Hub not available in this JARVIS installation."
    except Exception as e:
        return f"Error retrieving IoT status: {e}"


@tool
def get_iot_devices(dummy: str = "") -> str:
    """
    List all registered IoT devices with their current state.
    
    Shows for each device:
    - Device ID and name
    - Type (sensor/actuator)
    - Current state
    - Last reading
    - Total reads and errors
    
    Args:
        dummy: Not used, exists for LangChain compatibility
    
    Returns:
        Formatted list of all IoT devices
    """
    try:
        from core.iot_hub import get_iot_hub
        
        hub = get_iot_hub()
        devices = hub.get_device_summary()
        
        if not devices:
            return "No IoT devices registered."
        
        report = "🔌 **Registered IoT Devices:**\n\n"
        
        for device in devices:
            state_icon = {
                'active': '🟢',
                'idle': '🟡',
                'sleep': '😴',
                'error': '🔴',
                'offline': '⚫'
            }.get(device['state'], '⚪')
            
            report += f"{state_icon} **{device['name']}** (`{device['id']}`)\n"
            report += f"   Type: {device['type'].title()}\n"
            report += f"   State: {device['state'].upper()}\n"
            report += f"   Last Reading: {device['last_reading']}\n"
            report += f"   Total Reads: {device['total_reads']}\n"
            
            if device['errors'] > 0:
                report += f"   ⚠️ Errors: {device['errors']}\n"
            
            report += "\n"
        
        return report.strip()
        
    except ImportError:
        return "IoT Hub not available."
    except Exception as e:
        return f"Error listing devices: {e}"


@tool
def get_sensor_statistics(dummy: str = "") -> str:
    """
    Get detailed sensor manager statistics.
    
    Shows:
    - Optimized sensor manager stats
    - Read counts and error rates
    - Motion detection events
    - Batch processing efficiency
    - System uptime
    
    Args:
        dummy: Not used, exists for LangChain compatibility
    
    Returns:
        Detailed sensor statistics report
    """
    try:
        # Try to import from main.py context
        import sys
        if 'sensor_manager' in dir(sys.modules.get('__main__', {})):
            manager = sys.modules['__main__'].sensor_manager
            
            if hasattr(manager, 'get_statistics'):
                stats = manager.get_statistics()
                
                report = f"""
📊 **Sensor Manager Statistics**

**Performance:**
- Total Reads: {stats.get('total_reads', 0)}
- Batch Reads: {stats.get('batch_reads', 0)}
- Motion Events: {stats.get('motion_events', 0)}
- Errors: {stats.get('errors', 0)}
- Error Rate: {stats.get('error_rate', 0):.2%}

**Uptime:** {stats.get('uptime_seconds', 0):.1f} seconds
"""
                
                # Add IoT Hub stats if available
                if 'iot_hub' in stats:
                    hub_stats = stats['iot_hub']
                    report += f"""
**IoT Hub Integration:**
- Devices: {hub_stats.get('devices', 0)}
- Active Batches: {hub_stats.get('batches', 0)}
- Hub Uptime: {hub_stats.get('uptime_seconds', 0):.1f}s
"""
                
                return report.strip()
        
        return "Sensor manager not available or not started yet."
        
    except Exception as e:
        return f"Error retrieving sensor statistics: {e}"


@tool
def configure_power_mode(config: str) -> str:
    """
    Configure power management mode for IoT devices.
    
    Power modes:
    - 'active': Continuous operation (default)
    - 'polling': Periodic reads with duty cycle
    - 'sleep': Deep sleep, wake on demand only
    - 'adaptive': Adjust based on usage patterns
    
    Format: "device_id:mode:sleep_ms"
    Example: "dht:polling:5000" (DHT sensor, polling mode, 5s sleep)
    
    Args:
        config: Power configuration string
    
    Returns:
        Confirmation message
    """
    try:
        from core.iot_hub import get_iot_hub
        
        parts = config.split(':')
        if len(parts) < 2:
            return "Invalid format. Use: device_id:mode or device_id:mode:sleep_ms"
        
        device_id = parts[0]
        mode = parts[1]
        sleep_ms = int(parts[2]) if len(parts) > 2 else 0
        
        hub = get_iot_hub()
        hub.power_manager.set_power_mode(device_id, mode, sleep_ms)
        
        msg = f"✅ Power mode for '{device_id}' set to '{mode}'"
        if sleep_ms > 0:
            msg += f" with {sleep_ms}ms sleep interval"
        
        return msg
        
    except ImportError:
        return "IoT Hub not available."
    except Exception as e:
        return f"Error configuring power mode: {e}"


@tool
def create_sensor_batch(config: str) -> str:
    """
    Create a sensor batch for efficient reading.
    
    Batching reduces GPIO overhead by reading multiple sensors together.
    
    Format: "batch_id:sensor1,sensor2,sensor3:interval_ms:priority"
    Example: "env_batch:dht,mq3:2000:1" 
    (Environment batch with DHT and MQ-3, 2s interval, high priority)
    
    Priority: 1=high, 2=medium, 3=low
    
    Args:
        config: Batch configuration string
    
    Returns:
        Confirmation message
    """
    try:
        from core.iot_hub import get_iot_hub
        
        parts = config.split(':')
        if len(parts) < 3:
            return "Invalid format. Use: batch_id:sensor1,sensor2:interval_ms:priority"
        
        batch_id = parts[0]
        sensors = parts[1].split(',')
        interval_ms = int(parts[2])
        priority = int(parts[3]) if len(parts) > 3 else 1
        
        hub = get_iot_hub()
        hub.create_batch(batch_id, sensors, interval_ms, priority)
        
        return f"✅ Created batch '{batch_id}' with {len(sensors)} sensors ({interval_ms}ms interval, priority {priority})"
        
    except ImportError:
        return "IoT Hub not available."
    except Exception as e:
        return f"Error creating batch: {e}"


@tool
def get_device_reading(device_id: str) -> str:
    """
    Get the latest reading from a specific IoT device.
    
    Args:
        device_id: ID of the device (e.g., 'pir', 'ultrasonic', 'dht', 'mq3')
    
    Returns:
        Latest device reading and status
    """
    try:
        from core.iot_hub import get_iot_hub
        
        hub = get_iot_hub()
        device = hub.get_device(device_id)
        
        if not device:
            return f"Device '{device_id}' not found. Use get_iot_devices to see available devices."
        
        report = f"""
📡 **Device: {device.name}**

- ID: `{device.device_id}`
- Type: {device.device_type.value.title()}
- State: {device.state.value.upper()}
- Last Reading: {device.last_reading}
- Last Update: {device.last_update.isoformat() if device.last_update else 'Never'}
- Total Reads: {device.total_reads}
- Errors: {device.error_count}
"""
        
        return report.strip()
        
    except ImportError:
        return "IoT Hub not available."
    except Exception as e:
        return f"Error getting device reading: {e}"
