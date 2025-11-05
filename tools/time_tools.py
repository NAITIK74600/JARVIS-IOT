# H:/jarvis/tools/time_tools.py

from langchain_core.tools import tool
from datetime import datetime
import pytz

@tool
def get_current_time_and_date() -> str:
    """India Standard Time ke liye current date aur time return karta hai."""
    try:
        timezone = pytz.timezone('Asia/Kolkata')
        now = datetime.now(timezone)
        date = now.strftime("%A, %B %d, %Y")
        time_str = now.strftime("%I:%M %p")
        return f"Sir, abhi {date} hai aur samay {time_str} ho raha hai."
    except Exception as e: return f"Samay batane mein error: {e}"

def get_time_tools():
    """Sabhi time tools ki list return karta hai."""
    return [get_current_time_and_date]