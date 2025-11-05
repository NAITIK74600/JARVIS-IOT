from langchain.tools import tool

# Lazy initialization - don't create vision agent until actually needed
_vision_agent = None

def _get_vision_agent():
    """Lazy initialization of vision agent."""
    global _vision_agent
    if _vision_agent is None:
        try:
            from core.vision import get_vision_agent
            _vision_agent = get_vision_agent()
        except Exception as e:
            print(f"Warning: Vision agent initialization failed: {e}")
            _vision_agent = False  # Mark as failed so we don't retry
    return _vision_agent if _vision_agent is not False else None

@tool
def capture_image_and_describe(query: str) -> str:
    """
    Captures an image from the webcam and uses a vision model to describe it based on the user's query.
    Use this tool to answer questions about the user's surroundings, identify objects, or describe what is in front of the camera.
    Args:
        query (str): The user's question about what the camera sees.
    """
    vision_agent = _get_vision_agent()
    if not vision_agent:
        return "Vision agent is not available. Please configure GEMINI_API_KEY or GOOGLE_API_KEY."
    
    try:
        frame = vision_agent.capture_image()
        description = vision_agent.analyze_image(frame, query)
        return description
    except Exception as e:
        return f"An error occurred while using the vision tool: {e}"
    finally:
        if vision_agent:
            vision_agent.release_camera()

def get_vision_tools():
    """Returns a list of all vision-related tools."""
    return [capture_image_and_describe]
