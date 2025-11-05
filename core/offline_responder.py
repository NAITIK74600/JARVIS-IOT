"""Lightweight rule-based responder for offline Jarvis operation."""
from __future__ import annotations

from typing import Callable, Dict, Iterable, Optional


class OfflineResponder:
    """Fallback handler that maps keyword intents to built-in tools.

    Parameters
    ----------
    tools : Iterable
        Collection of LangChain tools or plain callables exposed to Jarvis.
    logger : Optional[Callable[[str], None]]
        Callback used to emit informational messages to the UI/log.
    """

    def __init__(self, tools: Iterable, logger: Optional[Callable[[str], None]] = None) -> None:
        self._logger = logger
        self._tool_lookup: Dict[str, Callable] = {}
        for tool in tools:
            name = getattr(tool, "name", getattr(tool, "__name__", None))
            if not name:
                continue
            func = getattr(tool, "func", None)
            if callable(func):
                self._tool_lookup[name] = func
            elif callable(tool):
                self._tool_lookup[name] = tool
        self._log("Offline responder initialised with tools: " + ", ".join(sorted(self._tool_lookup)))

    # ------------------------------------------------------------------
    def _log(self, message: str) -> None:
        if self._logger:
            self._logger(message)

    def _call_tool(self, name: str, *args, **kwargs) -> Optional[str]:
        func = self._tool_lookup.get(name)
        if not func:
            return None
        try:
            return func(*args, **kwargs)
        except Exception as exc:  # pragma: no cover - hardware dependent
            return f"Error executing '{name}': {exc}"

    # ------------------------------------------------------------------
    def respond(self, user_input: str, reason: Optional[str] = None) -> Dict[str, object]:
        """Generate an offline response for a natural-language command."""

        text = user_input.lower().strip()
        response_text: Optional[str] = None

        # Environment & sensors
        if any(keyword in text for keyword in ("temperature", "humidity", "weather")):
            response_text = self._call_tool("get_environment_readings", "")
        elif "all sensor" in text or "sensor reading" in text or "sensor status" in text:
            response_text = self._call_tool("get_all_sensor_readings", "")
        elif "scan" in text and "last" not in text:
            response_text = self._call_tool("scan_environment", "")
        elif "last scan" in text:
            response_text = self._call_tool("get_last_scan", "")
        
        # Time & date
        elif "time" in text or "what time" in text or "clock" in text:
            response_text = self._call_tool("get_current_system_time")
        elif "date" in text or "today" in text or "what day" in text:
            response_text = self._call_tool("get_current_system_time")
        
        # Greetings & basic conversation
        elif any(text.startswith(greeting) for greeting in ("hello", "hi", "hey", "greetings")):
            response_text = "Hello! How may I assist you today?"
        elif "good morning" in text:
            response_text = "Good morning! Ready to serve."
        elif "good night" in text or "goodnight" in text:
            response_text = "Good night! Sleep well."
        elif "how are you" in text or "how r u" in text:
            response_text = "I'm functioning optimally, thank you for asking. How can I help you?"
        elif "thank you" in text or "thanks" in text:
            response_text = "You're welcome! Always happy to help."
        
        # System information
        elif "battery" in text or "power" in text:
            response_text = self._call_tool("get_battery_status")
        elif "network" in text or "wifi" in text or "internet" in text:
            response_text = self._call_tool("get_network_status")
        elif "system" in text and "info" in text:
            response_text = self._call_tool("get_system_info")
        
        # Robot control
        elif "look" in text and ("left" in text or "right" in text or "up" in text or "down" in text):
            if "left" in text:
                response_text = self._call_tool("look_left")
            elif "right" in text:
                response_text = self._call_tool("look_right")
            elif "up" in text:
                response_text = self._call_tool("look_up")
            elif "down" in text:
                response_text = self._call_tool("look_down")
        elif "center" in text or "neutral" in text or "reset" in text:
            response_text = self._call_tool("reset_position")
        
        # Math operations
        elif "what is" in text or "calculate" in text or "compute" in text:
            # Simple math extraction
            import re
            math_match = re.search(r'(\d+)\s*([+\-*/])\s*(\d+)', text)
            if math_match:
                a, op, b = int(math_match.group(1)), math_match.group(2), int(math_match.group(3))
                result = {'+': a+b, '-': a-b, '*': a*b, '/': a/b if b != 0 else "undefined"}
                response_text = f"{a} {op} {b} = {result.get(op, 'error')}"

        if not response_text:
            response_text = (
                "I'm running in offline mode. I can help with: sensors, time/date, greetings, "
                "system info, robot control, basic math. For complex tasks, I need API access."
            )

        if reason:
            response_text = f"{reason}\n{response_text}"

        return {
            "text": response_text,
            "provider": "Offline",
            "fallback_used": True,
            "raw": {"mode": "offline"},
        }
