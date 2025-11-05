"""
API Quota Monitoring and Management Tools
"""

from langchain.tools import tool


@tool
def get_api_quota_status(dummy: str = "") -> str:
    """
    Get current API quota usage statistics.
    
    Shows:
    - Daily quota used and remaining
    - Hourly quota used and remaining
    - Percentage of quota consumed
    - Offline vs API request ratio
    
    Args:
        dummy: Not used, exists for LangChain compatibility
    
    Returns:
        Formatted quota status report
    """
    try:
        from core.hybrid_router import get_router
        
        router = get_router()
        state = router.quota_manager.state
        
        # Calculate percentages
        daily_pct = (state.daily_used / state.daily_limit) * 100 if state.daily_limit > 0 else 0
        hourly_pct = (state.hourly_used / state.hourly_limit) * 100 if state.hourly_limit > 0 else 0
        
        # Offline vs API ratio
        total_requests = router.offline_count + router.api_count
        offline_pct = (router.offline_count / total_requests * 100) if total_requests > 0 else 0
        
        report = f"""
🔋 **API Quota Status Report**

**Daily Usage:**
- Used: {state.daily_used} / {state.daily_limit} requests ({daily_pct:.1f}%)
- Remaining: {state.daily_limit - state.daily_used} requests

**Hourly Usage:**
- Used: {state.hourly_used} / {state.hourly_limit} requests ({hourly_pct:.1f}%)
- Remaining: {state.hourly_limit - state.hourly_used} requests

**Optimization Stats:**
- Total requests: {total_requests}
- Offline: {router.offline_count} ({offline_pct:.1f}%)
- API: {router.api_count} ({100 - offline_pct:.1f}%)

**Cache Performance:**
- Cached responses: {len(router.cache)}
- Cache hits: {router.cache_hits}

**Status:** {'✅ Healthy' if daily_pct < 80 else '⚠️ High Usage' if daily_pct < 95 else '🔴 Critical'}
"""
        
        return report.strip()
        
    except ImportError:
        return "Hybrid router not available. API quota tracking disabled."
    except Exception as e:
        return f"Error retrieving quota status: {e}"


@tool
def reset_quota_tracking(dummy: str = "") -> str:
    """
    Reset API quota tracking counters (for testing purposes).
    
    CAUTION: This resets usage counters but does NOT reset actual API limits.
    Only use this if you want to clear the tracking data.
    
    Args:
        dummy: Not used, exists for LangChain compatibility
    
    Returns:
        Confirmation message
    """
    try:
        from core.hybrid_router import get_router
        
        router = get_router()
        
        # Reset tracking counters
        router.offline_count = 0
        router.api_count = 0
        router.cache_hits = 0
        router.cache.clear()
        
        # Save state
        router.quota_manager.save_state()
        
        return "✅ Quota tracking counters have been reset. Usage statistics cleared."
        
    except ImportError:
        return "Hybrid router not available."
    except Exception as e:
        return f"Error resetting quota tracking: {e}"


@tool
def set_offline_mode(enable: str = "true") -> str:
    """
    Force offline mode on/off to conserve API quota.
    
    When enabled, JARVIS will ONLY use offline processing, no API calls.
    When disabled, normal hybrid routing resumes.
    
    Args:
        enable: "true" to force offline, "false" to resume normal routing
    
    Returns:
        Confirmation message
    """
    try:
        from core.hybrid_router import get_router
        
        router = get_router()
        enable_bool = enable.lower() in ("true", "yes", "1", "on")
        
        router.force_offline = enable_bool
        
        if enable_bool:
            return "🔒 Forced offline mode ENABLED. No API calls will be made until disabled."
        else:
            return "🔓 Forced offline mode DISABLED. Hybrid routing resumed."
        
    except ImportError:
        return "Hybrid router not available."
    except Exception as e:
        return f"Error setting offline mode: {e}"
