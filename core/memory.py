# H:/jarvis/core/memory.py (NEW FILE)

from langchain.memory import ConversationBufferWindowMemory


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