"""
Intelligent Mode Optimizer for JARVIS
Decides when to use offline vs online mode based on:
1. Command type (hardware/sensor vs complex queries)
2. API availability
3. Internet connectivity
4. Recent API failures
"""
import time
import requests
from typing import Tuple, Optional

class ModeOptimizer:
    """Optimizes offline/online mode switching"""
    
    def __init__(self):
        # Hardware/sensor related keywords (prefer offline safety execution)
        self.offline_keywords = [
            # Sensor commands
            'sensor', 'temperature', 'humidity', 'motion', 'distance',
            'ultrasonic', 'pir', 'dht', 'dht11', 'mq3', 'alcohol',

            # Hardware control / locomotion
            'servo', 'motor', 'move', 'turn', 'forward', 'backward',
            'left', 'right', 'stop', 'speed', 'angle', 'rotate',

            # Scanning and tracking
            'scan', 'track', 'face', 'follow', 'neck',

            # Direct hardware terms
            'gpio', 'pigpio', 'relay', 'fan', 'light'
        ]

        # Hinglish hardware keywords (keep emergency-focused words only)
        self.hinglish_offline = [
            'chalo', 'ruko', 'dekho', 'dikhao',
            'aage', 'peeche', 'daaye', 'baaye', 'band',
            'scan', 'karo', 'chalao', 'rok'
        ]

        # Safety triggers where offline reflexes should engage
        self.safety_keywords = [
            'collision', 'accident', 'hit the wall', 'hit wall', 'bump',
            'impact', 'crash', 'emergency stop', 'danger', 'protect', 'safety'
        ]

        # Online keywords (need cloud AI)
        self.online_keywords = [
            'weather', 'news', 'search', 'wikipedia', 'web',
            'translate', 'calculate', 'explain', 'why', 'how',
            'what is', 'who is', 'when did', 'where is',
            'tell me about', 'describe', 'analyze',
            'mausam', 'khabar', 'khoj', 'batao'
        ]
        
    # API status tracking
        self.api_failures = 0
        self.last_api_success = time.time()
        self.last_connectivity_check = 0
        self.is_online = True
        self.connectivity_cache_duration = 60  # Check every 60 seconds
        self.manual_mode: Optional[str] = None  # 'online', 'offline', or None for auto
        
    def should_use_offline(self, user_input: str) -> Tuple[bool, Optional[str]]:
        """
        Determine if command should use offline mode
        
        Returns:
            (should_use_offline, reason)
        """
        user_input_lower = user_input.lower()
        
        # Manual overrides
        if self.manual_mode == "online":
            return False, "manual online override"
        if self.manual_mode == "offline":
            return True, "manual offline override"

        # 1. Safety-first triggers (physical protection)
        for keyword in self.safety_keywords:
            if keyword in user_input_lower:
                return True, f"safety trigger detected: '{keyword}'"

        # 2. Hardware-focused commands stay local for low-latency control
        for keyword in self.offline_keywords + self.hinglish_offline:
            if keyword in user_input_lower:
                return True, f"hardware command detected: '{keyword}'"

        # 3. Check internet connectivity
        if not self._check_connectivity():
            return True, "no internet connection"

        # 4. Check if we have too many recent API failures
        if self.api_failures >= 3:
            if time.time() - self.last_api_success > 300:  # 5 minutes
                self.api_failures = 0
            else:
                return True, f"too many API failures ({self.api_failures})"

        # 5. Check if command explicitly needs online (weather, news, search)
        for keyword in self.online_keywords:
            if keyword in user_input_lower:
                return False, f"online required for: '{keyword}'"

        # Default preference: online conversations via Gemini
        return False, "online preferred for communication"
    
    def _check_connectivity(self) -> bool:
        """Check if internet is available (cached)"""
        now = time.time()
        
        # Use cached result if recent
        if now - self.last_connectivity_check < self.connectivity_cache_duration:
            return self.is_online
        
        # Test connectivity
        try:
            response = requests.get('https://www.google.com', timeout=3)
            self.is_online = response.status_code == 200
        except:
            self.is_online = False
        
        self.last_connectivity_check = now
        return self.is_online
    
    def record_api_success(self):
        """Record successful API call"""
        self.api_failures = 0
        self.last_api_success = time.time()
    
    def record_api_failure(self):
        """Record failed API call"""
        self.api_failures += 1
    
    def get_status(self) -> dict:
        """Get current mode optimizer status"""
        if self.manual_mode:
            mode_state = self.manual_mode
        elif self.api_failures >= 3 or not self.is_online:
            mode_state = "offline"
        else:
            mode_state = "auto"
        return {
            "online": self.is_online,
            "api_failures": self.api_failures,
            "last_success": time.time() - self.last_api_success,
            "mode": mode_state
        }
    
    def force_mode(self, mode: str):
        """Force offline or online mode"""
        mode = mode.lower()
        if mode == "offline":
            self.manual_mode = "offline"
        elif mode == "online":
            self.manual_mode = "online"
            self.api_failures = 0
            self.is_online = True
        elif mode == "auto":
            self.manual_mode = None
            self.api_failures = 0


# Global instance
_mode_optimizer = None

def get_mode_optimizer() -> ModeOptimizer:
    """Get global mode optimizer instance"""
    global _mode_optimizer
    if _mode_optimizer is None:
        _mode_optimizer = ModeOptimizer()
    return _mode_optimizer
