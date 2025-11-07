"""Core conversational engine coordinating tools, memory, and LLM providers."""
from __future__ import annotations

import traceback
from typing import Callable, Dict, Optional

try:
    from langchain.agents import AgentExecutor, create_tool_calling_agent
except ImportError:
    # LangChain 0.3+ moved these to langchain_core
    try:
        from langchain_core.agents import AgentExecutor
        from langchain.agents import create_tool_calling_agent
    except ImportError:
        # Fallback for even newer versions
        from langchain_core.runnables import RunnablePassthrough as AgentExecutor
        create_tool_calling_agent = None

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from typing import TYPE_CHECKING

from core.llm_manager import LLMManager, LLMProvider

if TYPE_CHECKING:
    from core.offline_responder import OfflineResponder
else:
    try:
        from core.offline_responder import OfflineResponder
    except ImportError:  # pragma: no cover - optional in legacy builds
        OfflineResponder = None  # type: ignore

try:
    from core.hybrid_router import get_router
except ImportError:
    get_router = None  # type: ignore

try:
    from core.personality_engine import get_personality_enhancer
except ImportError:
    get_personality_enhancer = None  # type: ignore

try:
    from core.mode_optimizer import get_mode_optimizer
except ImportError:
    get_mode_optimizer = None  # type: ignore


class JarvisCore:
    """High level orchestrator for tool-augmented conversations."""

    def __init__(
        self,
        persona,
        memory,
        tools,
        user_profile,
        ui_mode: bool = False,
        llm_manager: Optional[LLMManager] = None,
        offline_responder: Optional["OfflineResponder"] = None,
        status_callback: Optional[Callable[[str], None]] = None,
    ) -> None:
        self.persona = persona
        self.memory = memory
        self.tools = tools
        self.user_profile = user_profile
        self.ui_mode = ui_mode
        self.status_callback = status_callback

        self.llm_manager = llm_manager
        self._current_provider: Optional[LLMProvider] = None
        self._prompt = None
        self.agent_executor: Optional[AgentExecutor] = None
        self.offline_responder = offline_responder
        
        # Initialize hybrid router and personality engine
        self.hybrid_router = get_router() if get_router else None
        self.personality = get_personality_enhancer() if get_personality_enhancer else None
        
        # Initialize mode optimizer for intelligent offline/online switching
        self.mode_optimizer = get_mode_optimizer() if get_mode_optimizer else None

        if self.llm_manager and self.llm_manager.providers:
            self._build_agent(self.llm_manager.primary)
        elif self.offline_responder:
            self._announce_status("Offline mode active.")

    # ------------------------------------------------------------------
    # Agent construction & helpers
    # ------------------------------------------------------------------
    def _build_agent(self, provider: LLMProvider) -> None:
        self._current_provider = provider
        self._prompt = self._create_prompt(provider_name=provider.name)
        self.agent_executor = AgentExecutor(
            agent=create_tool_calling_agent(provider.client, self.tools, self._prompt),
            tools=self.tools,
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=self._handle_parsing_errors,
        )
        if self.llm_manager:
            self.llm_manager.set_active(provider)
        self._announce_status(provider.speakable_status)

    def _create_prompt(self, provider_name: Optional[str] = None):
        system_prompt = self.persona.get_prompt()
        
        # Enhance prompt with personality engine if available
        if self.personality:
            system_prompt = self.personality.get_enhanced_system_prompt(system_prompt)
        
        if provider_name:
            system_prompt += f"\n\n[Active model: {provider_name}]"
        return ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )

    def _handle_parsing_errors(self, error: Exception) -> str:
        error_str = str(error)
        print(f"Agent Parsing Error: {error_str}")
        if "Could not parse tool input" in error_str:
            return (
                "I ran into a tool formatting issue while executing that request. "
                "Please rephrase or try again."
            )
        return f"I encountered an error: {error_str}. Please try again."

    def _announce_status(self, message: str) -> None:
        if self.status_callback:
            self.status_callback(message)

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------
    def get_response(self, user_input: str) -> Dict[str, object]:
        """Main entrypoint to generate a response from user text."""
        
        # Check personality engine for protection/interception
        if self.personality:
            personality_result = self.personality.process_input(user_input)
            if personality_result and personality_result.get("intercept"):
                # Owner protection or praise - return immediately
                return {
                    "text": personality_result["response"],
                    "provider": "personality_engine",
                    "fallback_used": False,
                    "raw": {"reason": personality_result.get("reason", "personality_intercept")},
                }
        
        # Use mode optimizer for intelligent offline/online decision
        should_use_offline = False
        offline_reason = None
        
        if self.mode_optimizer:
            # Check if we should use offline mode
            should_use_offline, offline_reason = self.mode_optimizer.should_use_offline(user_input)
            
            if should_use_offline and self.offline_responder:
                self._announce_status(f"⚡ Offline mode: {offline_reason}")
                offline_result = self.offline_responder.respond(user_input, reason=offline_reason)
                return {
                    **offline_result,
                    "mode": "offline",
                    "offline_reason": offline_reason
                }
        
        # Check if we should use offline mode via hybrid router (fallback)
        if not should_use_offline and self.hybrid_router:
            should_use_offline, offline_reason = self.hybrid_router.should_use_offline(user_input)
            if should_use_offline and self.offline_responder:
                self._announce_status(f"Using offline mode ({offline_reason})...")
                offline_result = self.offline_responder.respond(user_input, reason=f"Offline-first: {offline_reason}")
                return {
                    **offline_result,
                    "quota_saved": True,
                    "offline_reason": offline_reason
                }

        # Try online mode with LLM
        if self.agent_executor and self.llm_manager:
            errors = []
            for provider in self.llm_manager.iter_providers(self._current_provider):
                try:
                    if provider is not self._current_provider:
                        self._build_agent(provider)
                    
                    self._announce_status(f"🌐 Online mode: Using {provider.name}...")
                    response = self.agent_executor.invoke({"input": user_input})
                    output_text = response.get("output", "I seem to be at a loss for words.")
                    
                    # Record successful API usage
                    if self.mode_optimizer:
                        self.mode_optimizer.record_api_success()
                    if self.hybrid_router:
                        self.hybrid_router.record_api_usage()
                    
                    return {
                        "text": output_text,
                        "provider": provider.name,
                        "fallback_used": provider is not self.llm_manager.primary,
                        "mode": "online",
                        "raw": response,
                    }
                except Exception as exc:  # pragma: no cover - runtime/tool errors
                    errors.append((provider.name, exc))
                    print(f"LLM provider '{provider.name}' failed: {exc}\n{traceback.format_exc()}")
                    
                    # Record API failure
                    if self.mode_optimizer:
                        self.mode_optimizer.record_api_failure()
                    
                    continue

            # All online providers failed - respond with degraded message instead of conversational offline mode
            error_message = "; ".join(f"{name}: {err}" for name, err in errors) or "No providers available"
            self._announce_status("⚠️ Unable to reach online intelligence providers.")
            return {
                "text": (
                    "I'm unable to reach Gemini or any backup models right now. "
                    "Protective safety routines are still active locally, but conversational "
                    "answers will resume once connectivity is restored."
                ),
                "provider": "system",
                "fallback_used": True,
                "mode": "degraded",
                "raw": {"errors": [f"{name}: {str(err)}" for name, err in errors]},
            }

        # No online mode available - use offline
        if self.offline_responder:
            return self.offline_responder.respond(user_input, reason="Operating in offline mode (no API configured)")

        raise RuntimeError("No response path available (LLM and offline responder missing)")

    def activate_listening(self) -> None:
        print("Jarvis activated, listening for command...")
        self._announce_status("Listening...")

    def process_input(self, transcript: str) -> Dict[str, object]:
        print(f"Processing transcript: {transcript}")
        
        # Show listening face on display
        try:
            from actuators.display import display
            display.show_face('listening')
        except:
            pass
        
        response = self.get_response(transcript)
        print(f"Jarvis[{response['provider']}] response: {response['text']}")
        
        # Show speaking on display
        try:
            from actuators.display import display
            display.clear()
            display.write_text("Speaking...", row=0, col=3)
        except:
            pass
        
        return response

    def cleanup(self) -> None:
        """Release runtime resources and reset state."""
        self._announce_status("Shutting down...")
        try:
            if hasattr(self.memory, "clear"):
                self.memory.clear()
        except Exception as exc:  # pragma: no cover - defensive
            print(f"JarvisCore cleanup warning: {exc}")
        self.agent_executor = None
        self._current_provider = None
