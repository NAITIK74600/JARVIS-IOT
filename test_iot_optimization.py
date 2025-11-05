#!/usr/bin/env python3
"""
IoT System Optimization Test Suite

Tests:
1. IoT Hub device registration
2. Event bus functionality
3. Batch sensor reading
4. Power management
5. Performance improvements
"""

import sys
import time
from datetime import datetime


def test_iot_hub():
    """Test IoT Hub core functionality."""
    print("\n" + "="*60)
    print("TEST 1: IoT Hub Functionality")
    print("="*60)
    
    try:
        from core.iot_hub import get_iot_hub, DeviceType, DeviceState
        
        hub = get_iot_hub()
        
        # Test device registration
        print("\n--- Device Registration ---")
        device1 = hub.register_device(
            device_id='test_sensor_1',
            device_type=DeviceType.SENSOR,
            name='Test Temperature Sensor'
        )
        
        device2 = hub.register_device(
            device_id='test_actuator_1',
            device_type=DeviceType.ACTUATOR,
            name='Test Servo Motor'
        )
        
        if len(hub.devices) == 2:
            print("✅ PASS: Device registration")
        else:
            print(f"❌ FAIL: Expected 2 devices, got {len(hub.devices)}")
            return False
        
        # Test device reading update
        print("\n--- Device Reading Update ---")
        hub.update_device_reading('test_sensor_1', 25.5)
        
        device = hub.get_device('test_sensor_1')
        if device and device.last_reading == 25.5:
            print("✅ PASS: Reading update")
        else:
            print("❌ FAIL: Reading not updated correctly")
            return False
        
        # Test device by type query
        print("\n--- Device Filtering ---")
        sensors = hub.get_devices_by_type(DeviceType.SENSOR)
        actuators = hub.get_devices_by_type(DeviceType.ACTUATOR)
        
        if len(sensors) == 1 and len(actuators) == 1:
            print("✅ PASS: Device filtering by type")
        else:
            print(f"❌ FAIL: Filtering failed (sensors={len(sensors)}, actuators={len(actuators)})")
            return False
        
        # Cleanup
        hub.unregister_device('test_sensor_1')
        hub.unregister_device('test_actuator_1')
        
        print("\n📊 IoT Hub tests PASSED")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_event_bus():
    """Test event bus pub/sub system."""
    print("\n" + "="*60)
    print("TEST 2: Event Bus System")
    print("="*60)
    
    try:
        from core.iot_hub import IoTEventBus
        
        event_bus = IoTEventBus()
        events_received = []
        
        # Define callback
        def test_callback(data):
            events_received.append(data)
        
        # Subscribe
        event_bus.subscribe('test_event', test_callback)
        
        # Publish events
        event_bus.publish('test_event', {'value': 1})
        event_bus.publish('test_event', {'value': 2})
        event_bus.publish('other_event', {'value': 3})  # Should not be received
        
        time.sleep(0.1)  # Allow callbacks to execute
        
        if len(events_received) == 2:
            print("✅ PASS: Event subscription and publishing")
        else:
            print(f"❌ FAIL: Expected 2 events, got {len(events_received)}")
            return False
        
        # Unsubscribe
        event_bus.unsubscribe('test_event', test_callback)
        event_bus.publish('test_event', {'value': 4})
        
        time.sleep(0.1)
        
        if len(events_received) == 2:  # Should still be 2
            print("✅ PASS: Event unsubscription")
        else:
            print(f"❌ FAIL: Unsubscribe failed, got {len(events_received)} events")
            return False
        
        print("\n📊 Event Bus tests PASSED")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_batch_reading():
    """Test batch sensor reading."""
    print("\n" + "="*60)
    print("TEST 3: Batch Sensor Reading")
    print("="*60)
    
    try:
        from core.iot_hub import get_iot_hub, DeviceType
        
        hub = get_iot_hub()
        
        # Register test sensors
        for i in range(3):
            hub.register_device(
                device_id=f'batch_sensor_{i}',
                device_type=DeviceType.SENSOR,
                name=f'Batch Test Sensor {i}'
            )
        
        # Create batch
        batch = hub.create_batch(
            batch_id='test_batch',
            sensor_ids=['batch_sensor_0', 'batch_sensor_1', 'batch_sensor_2'],
            interval_ms=100,
            priority=1
        )
        
        if batch and batch.sensors == ['batch_sensor_0', 'batch_sensor_1', 'batch_sensor_2']:
            print("✅ PASS: Batch creation")
        else:
            print("❌ FAIL: Batch creation failed")
            return False
        
        # Test batch retrieval
        if 'test_batch' in hub.batches:
            print("✅ PASS: Batch registered")
        else:
            print("❌ FAIL: Batch not found")
            return False
        
        # Cleanup
        hub.remove_batch('test_batch')
        for i in range(3):
            hub.unregister_device(f'batch_sensor_{i}')
        
        print("\n📊 Batch Reading tests PASSED")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_power_management():
    """Test power management system."""
    print("\n" + "="*60)
    print("TEST 4: Power Management")
    print("="*60)
    
    try:
        from core.iot_hub import PowerManager
        
        pm = PowerManager()
        
        # Set power modes
        pm.set_power_mode('device1', 'active')
        pm.set_power_mode('device2', 'polling', sleep_ms=5000)
        pm.set_power_mode('device3', 'sleep', sleep_ms=10000)
        
        # Test mode retrieval
        if pm.device_modes['device1'] == 'active':
            print("✅ PASS: Active mode set")
        else:
            print("❌ FAIL: Active mode not set")
            return False
        
        # Test sleep interval
        if pm.get_sleep_interval('device2') == 5000:
            print("✅ PASS: Sleep interval set")
        else:
            print("❌ FAIL: Sleep interval incorrect")
            return False
        
        # Test wake logic
        if pm.should_wake('device1', 1000):  # Active always wakes
            print("✅ PASS: Active device wake logic")
        else:
            print("❌ FAIL: Active device should always wake")
            return False
        
        if not pm.should_wake('device3', 1000):  # Sleep never wakes
            print("✅ PASS: Sleep device wake logic")
        else:
            print("❌ FAIL: Sleep device should not wake")
            return False
        
        print("\n📊 Power Management tests PASSED")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_performance():
    """Test performance improvements."""
    print("\n" + "="*60)
    print("TEST 5: Performance Metrics")
    print("="*60)
    
    try:
        from core.iot_hub import get_iot_hub, DeviceType
        
        hub = get_iot_hub()
        
        # Register multiple devices
        print("\n--- Registering 10 devices ---")
        start = time.time()
        for i in range(10):
            hub.register_device(
                device_id=f'perf_device_{i}',
                device_type=DeviceType.SENSOR,
                name=f'Performance Test Device {i}'
            )
        registration_time = (time.time() - start) * 1000
        
        print(f"Registration time: {registration_time:.2f}ms")
        if registration_time < 100:  # Should be very fast
            print("✅ PASS: Fast device registration")
        else:
            print("⚠️  SLOW: Registration took longer than expected")
        
        # Test rapid reading updates
        print("\n--- Testing 100 rapid updates ---")
        start = time.time()
        for i in range(100):
            hub.update_device_reading('perf_device_0', i)
        update_time = (time.time() - start) * 1000
        
        print(f"Update time: {update_time:.2f}ms")
        if update_time < 500:  # Should handle 100 updates quickly
            print("✅ PASS: Fast reading updates")
        else:
            print("⚠️  SLOW: Updates took longer than expected")
        
        # Cleanup
        for i in range(10):
            hub.unregister_device(f'perf_device_{i}')
        
        print("\n📊 Performance tests PASSED")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all IoT tests."""
    print("╔" + "="*58 + "╗")
    print("║" + " "*10 + "JARVIS IoT SYSTEM TEST SUITE" + " "*20 + "║")
    print("╚" + "="*58 + "╝")
    
    results = []
    
    # Run all tests
    results.append(("IoT Hub Functionality", test_iot_hub()))
    results.append(("Event Bus System", test_event_bus()))
    results.append(("Batch Sensor Reading", test_batch_reading()))
    results.append(("Power Management", test_power_management()))
    results.append(("Performance Metrics", test_performance()))
    
    # Summary
    print("\n" + "="*60)
    print("FINAL SUMMARY")
    print("="*60)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name:.<40} {status}")
    
    total_passed = sum(1 for _, passed in results if passed)
    total_tests = len(results)
    
    print(f"\n{'Total:':<40} {total_passed}/{total_tests} test suites passed")
    
    if total_passed == total_tests:
        print("\n🎉 All IoT systems operational!")
        return 0
    else:
        print(f"\n⚠️  {total_tests - total_passed} test suite(s) failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
