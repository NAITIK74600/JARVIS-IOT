"""Greeting manager for Jarvis.

Generates human-like greeting scripts that coordinate spoken lines,
LCD display text, and status prompts. Designed to run lightweight so it
can be imported during startup without delaying the UI.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import random
from typing import List, Optional


@dataclass
class GreetingScript:
    """Container describing what Jarvis should say and show."""

    speech_lines: List[str] = field(default_factory=list)
    display_lines: List[str] = field(default_factory=list)
    status_line: str = "Ready for your commands."
    log_line: Optional[str] = None

    def speech_text(self) -> str:
        """Join speech lines into a single utterance."""
        return " ".join(line.strip() for line in self.speech_lines if line.strip())


class GreetingManager:
    """Builds varied greetings based on time of day and persona hints."""

    def __init__(self, user_name: str = "Sir", location_hint: str = "control room") -> None:
        self.user_name = user_name or "Sir"
        self.location_hint = location_hint or "control room"

    def _time_bucket(self) -> str:
        hour = datetime.now().hour
        if 5 <= hour < 12:
            return "morning"
        if 12 <= hour < 17:
            return "afternoon"
        if 17 <= hour < 22:
            return "evening"
        return "night"

    def _intro_line(self) -> str:
        bucket = self._time_bucket()
        opening_options = [
            f"Good {bucket}, {self.user_name}.",
            f"Happy {bucket}, {self.user_name}.",
            f"Greetings this {bucket}, {self.user_name}.",
        ]
        return random.choice(opening_options)

    def _status_line(self, system_status: Optional[str]) -> str:
        if system_status:
            return f"Systems check: {system_status}."
        status_options = [
            "All diagnostics report green lights.",
            "Core modules are synchronised and ready.",
            "Power, sensors, and communications are nominal.",
        ]
        return random.choice(status_options)

    def _ready_prompt(self) -> str:
        prompts = [
            "How shall we begin?",
            "Ready when you are.",
            "Give me the first directive when you're set.",
            "Standing by for your command.",
        ]
        return random.choice(prompts)

    def _display_lines(self, bucket: str) -> List[str]:
        top = f"Jarvis Online"
        bottom_options = [
            f"Good {bucket.title()}!",
            f"Hello {self.user_name}",
            "Standing by",
        ]
        bottom = random.choice(bottom_options)
        # Ensure 16 character max per LCD row.
        return [top[:16], bottom[:16]]

    def build_startup_greeting(self, system_status: Optional[str] = None) -> GreetingScript:
        bucket = self._time_bucket()
        intro = self._intro_line()
        status_line = self._status_line(system_status)
        prompt = self._ready_prompt()

        speech_lines = [
            intro,
            status_line,
            f"We are in the {self.location_hint}. {prompt}",
        ]

        log_line = f"{intro} {status_line} {prompt}".strip()
        display_lines = self._display_lines(bucket)

        return GreetingScript(
            speech_lines=speech_lines,
            display_lines=display_lines,
            status_line=f"Ready for instructions ({bucket}).",
            log_line=log_line,
        )

    def build_interactive_greeting(self) -> GreetingScript:
        bucket = self._time_bucket()
        intro = self._intro_line()
        followups = [
            "Would you like a status briefing or shall we start patrol?",
            "Do you want me to scan the area or fetch today's schedule?",
            "Shall I prepare the room summary or go straight to tasks?",
        ]
        follow = random.choice(followups)

        speech_lines = [intro, follow]
        log_line = f"{intro} {follow}".strip()
        display_lines = self._display_lines(bucket)

        return GreetingScript(
            speech_lines=speech_lines,
            display_lines=display_lines,
            status_line=f"Awaiting direction ({bucket}).",
            log_line=log_line,
        )