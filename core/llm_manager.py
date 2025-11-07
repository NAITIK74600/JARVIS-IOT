"""Centralised management of Jarvis language model (Google Gemini only with multi-key support)."""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Iterable, List, Optional

from langchain_core.language_models.chat_models import BaseChatModel

try:  # Gemini
    from langchain_google_genai import ChatGoogleGenerativeAI
except ImportError:  # pragma: no cover - dependency injected via requirements
    ChatGoogleGenerativeAI = None  # type: ignore


class ProviderUnavailable(RuntimeError):
    """Raised when no LLM provider can be initialised."""


@dataclass(frozen=True)
class LLMProvider:
    name: str
    client: BaseChatModel
    description: str
    api_key_index: int = 0  # Track which API key this provider uses

    @property
    def speakable_status(self) -> str:
        """Short human-friendly status phrase used in voice/UI messaging."""
        key_label = f" (Key #{self.api_key_index + 1})" if self.api_key_index > 0 else ""
        return f"Responding with {self.name}{key_label}."


class LLMManager:
    """Initialises and manages multiple Google Gemini providers with different API keys."""

    DEFAULT_GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    def __init__(self) -> None:
        self._providers: List[LLMProvider] = []
        self._warnings: List[str] = []
        self._initialise_providers()
        if not self._providers:
            raise ProviderUnavailable(
                "No LLM provider available. Set GOOGLE_API_KEY in .env file."
            )
        self._active: LLMProvider = self._providers[0]

    # ------------------------------------------------------------------
    # Provider initialisation helpers
    # ------------------------------------------------------------------
    def _initialise_providers(self) -> None:
        """Load all available Gemini API keys and create providers for each."""
        gemini_providers = self._load_all_gemini_keys()
        self._providers.extend(gemini_providers)

    def _load_all_gemini_keys(self) -> List[LLMProvider]:
        """Load multiple Gemini API keys (GOOGLE_API_KEY, GOOGLE_API_KEY_2, etc.)"""
        providers = []
        
        # Try to load primary key and numbered keys
        for i in range(10):  # Support up to 10 keys
            if i == 0:
                key_name = "GOOGLE_API_KEY"
            else:
                key_name = f"GOOGLE_API_KEY_{i + 1}"
            
            api_key = os.getenv(key_name)
            if not api_key or api_key.startswith("your_"):
                continue  # Skip placeholder or missing keys
            
            provider = self._create_gemini_provider(api_key, i)
            if provider:
                providers.append(provider)
        
        if not providers:
            self._warnings.append("No valid GOOGLE_API_KEY found in .env file.")
        else:
            self._warnings.append(f"Loaded {len(providers)} Gemini API key(s) for rotation.")
        
        return providers

    def _create_gemini_provider(self, api_key: str, key_index: int) -> Optional[LLMProvider]:
        """Create a single Gemini provider with the given API key."""
        if ChatGoogleGenerativeAI is None:
            if key_index == 0:  # Only warn once
                self._warnings.append(
                    "langchain-google-genai is missing; install dependencies to use Gemini."
                )
            return None
        
        try:
            client = ChatGoogleGenerativeAI(
                model=self.DEFAULT_GEMINI_MODEL,
                temperature=0.4,
                google_api_key=api_key,
                convert_system_message_to_human=True,
            )
            
            key_label = f" #{key_index + 1}" if key_index > 0 else ""
            return LLMProvider(
                name=f"Gemini{key_label}",
                client=client,
                description=f"Google Gemini '{self.DEFAULT_GEMINI_MODEL}' (Key {key_index + 1})",
                api_key_index=key_index,
            )
        except Exception as exc:  # pragma: no cover - network/auth errors
            self._warnings.append(f"Failed to initialise Gemini key #{key_index + 1}: {exc}")
            return None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    @property
    def primary(self) -> LLMProvider:
        return self._providers[0]

    @property
    def providers(self) -> List[LLMProvider]:
        return list(self._providers)

    @property
    def warnings(self) -> List[str]:
        return list(self._warnings)

    def current(self) -> LLMProvider:
        return self._active

    def set_active(self, provider: LLMProvider) -> None:
        if provider not in self._providers:
            raise ValueError("Provider not managed by this LLMManager")
        self._active = provider

    def iter_providers(self, preferred: Optional[LLMProvider] = None) -> Iterable[LLMProvider]:
        """Yield providers in preference order, starting with *preferred* when given."""
        seen: set[int] = set()
        if preferred:
            yield preferred
            seen.add(id(preferred))
        for provider in self._providers:
            if id(provider) not in seen:
                yield provider

    def status_summary(self) -> str:
        active = self._active.name
        total_keys = len(self._providers)
        if total_keys > 1:
            return f"Active LLM: {active} ({total_keys} keys loaded)"
        return f"Active LLM: {active}"