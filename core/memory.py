# H:/jarvis/core/memory.py (NEW FILE)

try:
    from langchain.memory import ConversationBufferWindowMemory
except ImportError:
    # LangChain 0.3+ moved memory to langchain-community
    try:
        from langchain_community.chat_message_histories import ChatMessageHistory
        from langchain_core.memory import BaseMemory
        # Simple fallback implementation
        class ConversationBufferWindowMemory(BaseMemory):
            def __init__(self, k=6, **kwargs):
                super().__init__()
                self.k = k
                self.chat_memory = ChatMessageHistory()
            
            def load_memory_variables(self, inputs):
                return {"chat_history": self.chat_memory.messages[-self.k*2:]}
            
            def save_context(self, inputs, outputs):
                self.chat_memory.add_user_message(inputs.get("input", ""))
                self.chat_memory.add_ai_message(outputs.get("output", ""))
            
            def clear(self):
                self.chat_memory.clear()
    except ImportError:
        # Final fallback - dummy implementation
        class ConversationBufferWindowMemory:
            def __init__(self, **kwargs):
                self.history = []
            
            def load_memory_variables(self, inputs):
                return {"chat_history": self.history}
            
            def save_context(self, inputs, outputs):
                self.history.append({"input": inputs, "output": outputs})
                if len(self.history) > 12:
                    self.history = self.history[-12:]
            
            def clear(self):
                self.history = []


class JarvisMemory(ConversationBufferWindowMemory):
    """Windowed conversational memory tuned for Jarvis."""

    def __init__(self, k: int = 6):
        super().__init__(
            k=k,
            memory_key="chat_history",
            input_key="input",
            output_key="output",
            return_messages=True,
        )


def get_memory(k: int = 6) -> JarvisMemory:
    """Backward compatible helper for legacy imports."""
    return JarvisMemory(k=k)