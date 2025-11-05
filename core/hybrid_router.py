"""
Hybrid Intelligence Router for JARVIS
Routes queries between offline processing and API calls based on:
- Task complexity
- API quota remaining
- Response time requirements
"""

import re
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Tuple, Optional
from dataclasses import dataclass, asdict


@dataclass
class APIQuotaState:
    """Tracks API usage to prevent quota exhaustion."""
    daily_limit: int = 1500  # Google AI Studio free tier
    hourly_limit: int = 60    # Rate limit
    
    today_usage: int = 0
    current_hour_usage: int = 0
    last_reset_date: str = ""
    last_reset_hour: str = ""
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)


class APIQuotaManager:
    """Manages API quota tracking and persistence."""
    
    QUOTA_FILE = "jarvis_api_quota.json"
    
    def __init__(self):
        self.state = self._load_state()
        self._check_reset()
    
    def _load_state(self) -> APIQuotaState:
        """Load quota state from file."""
        if os.path.exists(self.QUOTA_FILE):
            try:
                with open(self.QUOTA_FILE, 'r') as f:
                    data = json.load(f)
                    return APIQuotaState.from_dict(data)
            except Exception as e:
                print(f"[QuotaManager] Failed to load state: {e}")
        return APIQuotaState()
    
    def _save_state(self):
        """Save quota state to file."""
        try:
            with open(self.QUOTA_FILE, 'w') as f:
                json.dump(self.state.to_dict(), f, indent=2)
        except Exception as e:
            print(f"[QuotaManager] Failed to save state: {e}")
    
    def _check_reset(self):
        """Reset counters if day/hour has changed."""
        now = datetime.now()
        today = now.strftime("%Y-%m-%d")
        current_hour = now.strftime("%Y-%m-%d %H:00")
        
        if self.state.last_reset_date != today:
            self.state.today_usage = 0
            self.state.last_reset_date = today
            print(f"[QuotaManager] Daily quota reset: {self.state.daily_limit} requests available")
        
        if self.state.last_reset_hour != current_hour:
            self.state.current_hour_usage = 0
            self.state.last_reset_hour = current_hour
    
    def can_use_api(self) -> bool:
        """Check if API call is allowed within quota."""
        self._check_reset()
        return (self.state.today_usage < self.state.daily_limit and
                self.state.current_hour_usage < self.state.hourly_limit)
    
    def record_api_call(self):
        """Record an API call."""
        self.state.today_usage += 1
        self.state.current_hour_usage += 1
        self._save_state()
    
    def get_remaining_quota(self) -> Dict[str, int]:
        """Get remaining quota for display."""
        self._check_reset()
        return {
            "daily_remaining": self.state.daily_limit - self.state.today_usage,
            "hourly_remaining": self.state.hourly_limit - self.state.current_hour_usage,
            "daily_used": self.state.today_usage,
            "hourly_used": self.state.current_hour_usage
        }


class HybridIntelligenceRouter:
    """
    Routes queries intelligently between offline and API processing.
    Optimizes for speed, quota conservation, and response quality.
    """
    
    # Tasks that can be handled offline efficiently
    OFFLINE_PATTERNS = [
        # Time & date queries
        (r'\b(what|current|tell me the)\s+(time|date|day)\b', 'time'),
        (r'\bwhat\s+(is\s+)?(today|tomorrow|yesterday)\b', 'time'),
        
        # System commands
        (r'\b(cpu|memory|ram|disk)\s+(usage|status|info)\b', 'system'),
        (r'\bsystem\s+(info|status)\b', 'system'),
        
        # File operations
        (r'\b(list|show|read|open)\s+(file|files|folder)\b', 'file_system'),
        (r'\b(create|write|delete)\s+(file|folder)\b', 'file_system'),
        
        # Sensor readings
        (r'\b(temperature|humidity|distance|motion|sensor)\b', 'sensors'),
        (r'\bcheck\s+(sensors?|environment)\b', 'sensors'),
        
        # Robot control (direct commands)
        (r'\b(move|turn|rotate|stop)\s+(robot|forward|backward|left|right)\b', 'robot'),
        (r'\b(servo|motor)\s+(angle|position|speed)\b', 'robot'),
        (r'\bscan\s+(environment|area)\b', 'robot'),
        
        # Memory operations
        (r'\b(remember|recall|save|note)\s+(this|that)\b', 'memory'),
        
        # Simple calculations
        (r'\b\d+\s*[\+\-\*\/]\s*\d+', 'calculation'),
        (r'\bcalculate\s+', 'calculation'),
        
        # Greetings (can be offline)
        (r'\b(hello|hi|hey|good\s+(morning|afternoon|evening))\b', 'greeting'),
    ]
    
    # Keywords that indicate complex queries needing API
    API_REQUIRED_KEYWORDS = [
        'explain', 'why', 'how does', 'what is the meaning',
        'tell me about', 'describe', 'analyze', 'compare',
        'opinion', 'think', 'feel', 'recommend', 'suggest',
        'creative', 'write', 'compose', 'generate',
        'search', 'find information', 'look up', 'browse',
        'who is', 'what is', 'when is', 'where is',  # Questions
        'prime minister', 'president', 'capital',  # Current events/facts
        'weather', 'news', 'latest',  # Real-time info
        'play', 'youtube', 'video', 'song', 'music',  # Media playback
        'karke', 'karo', 'karna',  # Hindi action verbs indicating complex tasks
    ]
    
    def __init__(self, quota_manager: Optional[APIQuotaManager] = None):
        self.quota_manager = quota_manager or APIQuotaManager()
        self.response_cache: Dict[str, Tuple[str, datetime]] = {}
        self.cache_ttl = timedelta(hours=1)  # Cache responses for 1 hour
        
        # Tracking counters for statistics
        self.offline_count = 0
        self.api_count = 0
        self.cache_hits = 0
        self.force_offline = False  # Manual override flag
    
    def should_use_offline(self, user_input: str) -> Tuple[bool, str]:
        """
        Determine if query should be handled offline.
        
        Returns:
            (should_use_offline: bool, reason: str)
        """
        # Force offline if manually enabled
        if self.force_offline:
            return (True, "forced_offline_mode")
        
        user_input_lower = user_input.lower().strip()
        
        # Check cache first
        if user_input_lower in self.response_cache:
            cached_response, cached_time = self.response_cache[user_input_lower]
            if datetime.now() - cached_time < self.cache_ttl:
                self.cache_hits += 1
                return (True, "cached_response")
        
        # Check quota
        if not self.quota_manager.can_use_api():
            quota_info = self.quota_manager.get_remaining_quota()
            return (True, f"quota_exhausted (daily: {quota_info['daily_remaining']}, hourly: {quota_info['hourly_remaining']})")
        
        # Check if requires API (check this BEFORE checking offline patterns)
        for keyword in self.API_REQUIRED_KEYWORDS:
            if keyword in user_input_lower:
                self.api_count += 1
                return (False, f"api_required_complex_query")
        
        # Check if matches offline patterns
        for pattern, task_type in self.OFFLINE_PATTERNS:
            if re.search(pattern, user_input_lower, re.IGNORECASE):
                self.offline_count += 1
                return (True, f"offline_capable_{task_type}")
        
        # Default to API for quality (removed "short query" check that was too aggressive)
        self.api_count += 1
        return (False, "default_to_api_for_quality")
    
    def cache_response(self, user_input: str, response: str):
        """Cache a response for future use."""
        user_input_lower = user_input.lower().strip()
        self.response_cache[user_input_lower] = (response, datetime.now())
        
        # Keep cache size manageable
        if len(self.response_cache) > 100:
            # Remove oldest entries
            sorted_cache = sorted(
                self.response_cache.items(),
                key=lambda x: x[1][1]
            )
            self.response_cache = dict(sorted_cache[-50:])
    
    def get_cached_response(self, user_input: str) -> Optional[str]:
        """Get cached response if available and fresh."""
        user_input_lower = user_input.lower().strip()
        if user_input_lower in self.response_cache:
            response, cached_time = self.response_cache[user_input_lower]
            if datetime.now() - cached_time < self.cache_ttl:
                return response
        return None
    
    def record_api_usage(self):
        """Record that an API call was made."""
        self.quota_manager.record_api_call()
    
    def get_quota_status(self) -> str:
        """Get human-readable quota status."""
        quota = self.quota_manager.get_remaining_quota()
        return (f"API Quota: {quota['daily_remaining']}/{self.quota_manager.state.daily_limit} daily, "
                f"{quota['hourly_remaining']}/{self.quota_manager.state.hourly_limit} hourly")


# Singleton instance
_router_instance = None

def get_router() -> HybridIntelligenceRouter:
    """Get or create singleton router instance."""
    global _router_instance
    if _router_instance is None:
        _router_instance = HybridIntelligenceRouter()
    return _router_instance
