from core.hardware_manager import hardware_manager
import RPi.GPIO as GPIO
import time
import threading
import random
from collections import deque

class PIR:
    def __init__(self, pin, on_motion_callback=None, cooldown=2.0, debounce=0.05):
        """
        Enhanced PIR Motion Sensor with debouncing and motion history.
        
        Args:
            pin (int): GPIO pin number (BCM mode)
            on_motion_callback (callable): Function to call when motion detected
            cooldown (float): Minimum seconds between motion events (default: 2.0)
            debounce (float): Debounce time in seconds to filter noise (default: 0.05)
        """
        self.pin = pin
        self.on_motion_callback = on_motion_callback
        self.cooldown = cooldown
        self.debounce = debounce
        
        # Motion tracking
        self.last_motion_time = None
        self.motion_count = 0
        self.motion_history = deque(maxlen=100)  # Store last 100 motion events
        
        # State management
        self._running = False
        self._monitor_thread = None
        self._last_state = False
        self._state_change_time = time.time()
        
        self.simulation_mode = hardware_manager.simulation_mode

        if not self.simulation_mode:
            GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
            print(f"✅ PIR Motion Sensor initialized on GPIO {self.pin} (Physical Pin 11)")
            print(f"   Cooldown: {self.cooldown}s, Debounce: {self.debounce}s")
        else:
            print(f"PIR Motion Sensor initialized on pin {self.pin} (Simulation Mode)")

    def _monitor(self):
        """
        Enhanced monitoring method with debouncing and cooldown.
        """
        print("🔍 PIR monitoring started.")
        fallback_poll = False
        
        while self._running:
            if self.simulation_mode:
                time.sleep(random.randint(10, 20))
                motion_detected = True
            else:
                current_state = GPIO.input(self.pin) == GPIO.HIGH
                motion_detected = False
                
                # Debouncing: State must be stable for debounce duration
                if current_state != self._last_state:
                    self._state_change_time = time.time()
                    self._last_state = current_state
                
                # Check if state is stable and it's a rising edge (motion start)
                elif current_state and (time.time() - self._state_change_time) >= self.debounce:
                    # Check cooldown period
                    if self.last_motion_time is None or \
                       (time.time() - self.last_motion_time) >= self.cooldown:
                        motion_detected = True
                
                time.sleep(0.05)  # Poll every 50ms

            if motion_detected:
                current_time = time.time()
                self.last_motion_time = current_time
                self.motion_count += 1
                
                # Store motion event in history
                motion_event = {
                    'timestamp': current_time,
                    'time_str': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'count': self.motion_count
                }
                self.motion_history.append(motion_event)
                
                print(f"🚨 Motion detected #{self.motion_count} at {motion_event['time_str']}")
                
                if self.on_motion_callback:
                    try:
                        # Run callback in a separate thread to avoid blocking
                        threading.Thread(
                            target=self.on_motion_callback, 
                            daemon=True
                        ).start()
                    except Exception as e:
                        print(f"❌ Error in on_motion_callback: {e}")
            
            # In simulation mode, add delay
            if self.simulation_mode:
                time.sleep(1)

        print("🛑 PIR monitoring stopped.")

    def start_monitoring(self):
        """
        Starts monitoring for motion in a background thread.
        """
        if not self._running:
            self._running = True
            self._monitor_thread = threading.Thread(target=self._monitor, daemon=True)
            self._monitor_thread.start()
            print("✅ PIR monitoring thread started")

    def stop_monitoring(self):
        """
        Stops the motion monitoring thread.
        """
        if self._running:
            self._running = False
            print("⏹️  PIR monitoring stop signal sent.")
        thread = self._monitor_thread
        if thread and thread.is_alive():
            thread.join(timeout=2.0)
            if thread.is_alive():
                print("⚠️  Warning: PIR monitoring thread did not terminate within timeout.")
        self._monitor_thread = None
    
    def get_motion_stats(self):
        """
        Get motion detection statistics.
        
        Returns:
            dict: Statistics including total count, last motion time, and recent activity
        """
        recent_motions = [m for m in self.motion_history 
                         if time.time() - m['timestamp'] <= 300]  # Last 5 minutes
        
        return {
            'total_count': self.motion_count,
            'last_motion_time': self.last_motion_time,
            'last_motion_str': time.strftime('%H:%M:%S', 
                                            time.localtime(self.last_motion_time)) 
                              if self.last_motion_time else 'Never',
            'recent_5min': len(recent_motions),
            'is_active': self._running,
            'pin': self.pin
        }
    
    def get_motion_history(self, limit=10):
        """
        Get recent motion history.
        
        Args:
            limit (int): Maximum number of events to return
            
        Returns:
            list: Recent motion events
        """
        return list(self.motion_history)[-limit:]
    
    def reset_stats(self):
        """Reset motion statistics."""
        self.motion_count = 0
        self.motion_history.clear()
        print("📊 PIR statistics reset")
    
    def is_motion_detected(self):
        """
        Check if motion was detected recently (within cooldown period).
        
        Returns:
            bool: True if recent motion detected
        """
        if self.last_motion_time is None:
            return False
        return (time.time() - self.last_motion_time) < self.cooldown

    def close(self):
        """Clean up resources."""
        self.stop_monitoring()

if __name__ == '__main__':
    import random
    # Example usage with enhanced features
    def motion_alert():
        print(f"🔔 CALLBACK TRIGGERED: Motion detected in the area!")

    print("=" * 70)
    print("🚀 PIR SENSOR TEST - Enhanced Features")
    print("=" * 70)
    
    pir_sensor = PIR(pin=17, on_motion_callback=motion_alert, cooldown=2.0)
    pir_sensor.start_monitoring()

    try:
        print("\n📡 Monitoring for motion... (Press Ctrl+C to exit)")
        print("Move in front of the sensor to trigger detection\n")
        
        # Keep the main thread alive and show stats periodically
        while True:
            time.sleep(10)
            stats = pir_sensor.get_motion_stats()
            print(f"\n📊 Stats: {stats['total_count']} detections, "
                  f"Last: {stats['last_motion_str']}, "
                  f"Recent (5min): {stats['recent_5min']}")
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Exiting...")
        
        # Show final statistics
        stats = pir_sensor.get_motion_stats()
        history = pir_sensor.get_motion_history(5)
        
        print("\n" + "=" * 70)
        print("📊 FINAL STATISTICS")
        print("=" * 70)
        print(f"Total motions detected: {stats['total_count']}")
        print(f"Last motion: {stats['last_motion_str']}")
        print(f"Recent activity (5 min): {stats['recent_5min']}")
        
        if history:
            print(f"\n📜 Last {len(history)} events:")
            for event in history:
                print(f"   #{event['count']}: {event['time_str']}")
        
        print("=" * 70)
        
    finally:
        pir_sensor.stop_monitoring()
        # HardwareManager will handle GPIO.cleanup()
