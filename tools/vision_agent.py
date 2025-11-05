# H:/jarvis/tools/vision_agent.py (CORRECTED)

import base64, os, json
from io import BytesIO
import pyautogui
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from PIL import Image

# This tool uses its own powerful vision model instance
VISION_MODEL = "anthropic/claude-3-haiku:beta"

def _get_vision_llm():
    """Initializes the vision-capable LLM client."""
    return ChatOpenAI(
        model=VISION_MODEL,
        api_key=os.getenv("OPENROUTER_API_KEY"),
        base_url="https://openrouter.ai/api/v1",
        default_headers={"HTTP-Referer": "http://localhost", "X-Title": "Jarvis Vision"}
    )

def _encode_image(image: Image.Image) -> str:
    """Encodes a PIL image into a base64 string for the API."""
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

@tool
def perform_visual_task(task_description: str) -> str:
    """
    Performs complex, multi-step tasks on the graphical user interface.
    Use this for any task that requires visual understanding and a sequence of actions,
    like 'open whatsapp, find Naitik, and type a message'.

    Args:
        task_description (str): A clear, high-level description of the entire task to be performed.
    """
    vision_llm = _get_vision_llm()
    print(f"--- Vision Agent Activated. Goal: '{task_description}' ---")
    
    # We will loop, allowing the agent to perform multiple steps
    for i in range(5): # Limit to 5 steps to prevent infinite loops
        print(f"--- Vision Agent: Step {i+1} ---")
        screenshot = pyautogui.screenshot()
        encoded_screenshot = _encode_image(screenshot)
        
        prompt = [
            HumanMessage(
                content=[
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encoded_screenshot}"}},
                    {"type": "text", "text": f"""
                        You are a screen automation expert. Your high-level goal is: "{task_description}".
                        Analyze the screenshot and decide the single best action to perform right now to progress this goal.
                        Your available actions are: CLICK, TYPE, SCROLL, or FINISH.

                        - If you need to click on something, provide the x, y coordinates.
                        - If you need to type something, provide the text.
                        - If you need to scroll, provide a direction ('up' or 'down') and amount.
                        - If the overall goal is complete, respond with FINISH.

                        Respond ONLY with a JSON object. Examples:
                        {{"action": "CLICK", "x": 500, "y": 350, "reason": "Clicking the 'Login' button."}}
                        {{"action": "TYPE", "text": "Hello, world!", "reason": "Typing the message into the chat box."}}
                        {{"action": "SCROLL", "direction": "down", "amount": 500, "reason": "Scrolling to find the contact."}}
                        {{"action": "FINISH", "reason": "The message has been sent, the task is complete."}}
                    """},
                ]
            )
        ]
        
        response = vision_llm.invoke(prompt)
        try:
            action_plan = json.loads(response.content)
            print(f"--- Vision Agent Plan: {action_plan} ---")
            
            action_type = action_plan.get("action")
            if action_type == "CLICK":
                pyautogui.click(action_plan['x'], action_plan['y'])
            elif action_type == "TYPE":
                pyautogui.write(action_plan['text'], interval=0.05)
            elif action_type == "SCROLL":
                amount = action_plan['amount'] if action_plan['direction'] == 'up' else -action_plan['amount']
                pyautogui.scroll(amount)
            elif action_type == "FINISH":
                return f"Visual task completed successfully. Reason: {action_plan.get('reason')}"
            else:
                return "Vision agent returned an unknown action. Aborting."
        except Exception as e:
            return f"Error parsing or executing vision agent action: {e}"

    return "Vision agent could not complete the task within 5 steps. Aborting."

# <<< --- THIS FUNCTION WAS MISSING --- >>>
def get_vision_tools():
    """Returns a list of all vision tools in this module."""
    return [perform_visual_task]