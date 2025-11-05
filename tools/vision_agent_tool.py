# H:/jarvis/tools/vision_agent_tool.py (NEW FILE)

import base64
import os
from io import BytesIO
import pyautogui
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from PIL import Image

# This tool will use its OWN instance of an LLM, specifically a vision model.
# We choose a powerful and free multimodal model from OpenRouter.
VISION_MODEL = "anthropic/claude-3-haiku:beta" # Or "google/gemini-pro-vision"

def get_vision_llm():
    """Initializes the vision-capable LLM client."""
    return ChatOpenAI(
        model=VISION_MODEL,
        api_key=os.getenv("OPENROUTER_API_KEY"),
        base_url="https://openrouter.ai/api/v1",
        default_headers={
            "HTTP-Referer": "http://localhost",
            "X-Title": "Jarvis Vision"
        }
    )

def encode_image(image: Image.Image) -> str:
    """Encodes a PIL image into a base64 string."""
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

@tool
def control_screen(task: str) -> str:
    """
    Analyzes the current screen and performs a task based on visual context.
    Use this to click buttons, type in text fields, or interact with any UI element.
    Provide a clear, simple instruction. For example: 'Click the button that says Submit' or 'Type my name into the username field'.

    Args:
        task (str): The specific task to perform on the screen.
    """
    try:
        vision_llm = get_vision_llm()
        print(f"--- Vision Agent: Capturing screen for task: '{task}' ---")
        
        # 1. Take a screenshot
        screenshot = pyautogui.screenshot()
        encoded_screenshot = encode_image(screenshot)
        
        # 2. Send the screenshot and task to the vision model
        print("--- Vision Agent: Analyzing screen and planning action... ---")
        prompt = [
            HumanMessage(
                content=[
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{encoded_screenshot}"},
                    },
                    {
                        "type": "text",
                        "text": f"""
                        You are a screen automation expert. Your goal is to perform the user's task on the provided screenshot.
                        Analyze the screenshot and the user's task: "{task}".

                        Based on the task, decide on ONE single action to take: either "CLICK" or "TYPE".

                        If the action is "CLICK", identify the x, y coordinates of the center of the element to click.
                        If the action is "TYPE", identify the text to type.

                        Respond ONLY with a JSON object in the following format:
                        - For a click: {{"action": "CLICK", "x": <x_coordinate>, "y": <y_coordinate>}}
                        - For typing: {{"action": "TYPE", "text": "<text_to_type>"}}
                        - If you cannot determine the action: {{"action": "FAIL", "reason": "<your_reason>"}}

                        Do not provide any other text, explanation, or conversational filler. Only the JSON object.
                        """
                    },
                ]
            )
        ]
        
        response = vision_llm.invoke(prompt)
        action_plan = json.loads(response.content)

        # 3. Execute the planned action
        action_type = action_plan.get("action")
        if action_type == "CLICK":
            x, y = action_plan.get("x"), action_plan.get("y")
            print(f"--- Vision Agent: Executing CLICK at ({x}, {y}) ---")
            pyautogui.click(x, y)
            return f"Action complete: Clicked at coordinates ({x}, {y})."
        elif action_type == "TYPE":
            text_to_type = action_plan.get("text")
            print(f"--- Vision Agent: Executing TYPE with text: '{text_to_type}' ---")
            pyautogui.write(text_to_type, interval=0.05)
            return f"Action complete: Typed '{text_to_type}'."
        elif action_type == "FAIL":
            reason = action_plan.get("reason", "unknown")
            print(f"--- Vision Agent: Failed. Reason: {reason} ---")
            return f"I looked at the screen but could not complete the task. Reason: {reason}"
        else:
            return "Vision agent returned an invalid action. Please try again."

    except Exception as e:
        return f"An error occurred in the vision agent: {e}"

def get_vision_agent_tools():
    return [control_screen]