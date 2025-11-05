# H:/jarvis/tools/calendar_tools.py (NEW FILE)
import os.path, datetime as dt
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from langchain_core.tools import tool

SCOPES = ["https://www.googleapis.com/auth/calendar"]
CREDENTIALS_FILE = "credentials.json"
TOKEN_FILE = "calendar_token.json" # Use a separate token file

def _get_calendar_service():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "w") as token: token.write(creds.to_json())
    return build("calendar", "v3", credentials=creds)

@tool
def list_upcoming_events(max_results: int = 10) -> str:
    """Lists the next upcoming events from your Google Calendar."""
    try:
        service = _get_calendar_service()
        now = dt.datetime.utcnow().isoformat() + "Z"
        events_result = service.events().list(
            calendarId="primary", timeMin=now, maxResults=max_results,
            singleEvents=True, orderBy="startTime"
        ).execute()
        events = events_result.get("items", [])
        if not events: return "No upcoming events found."
        summaries = []
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            summaries.append(f"- {event['summary']} (at {start})")
        return "Upcoming events:\n" + "\n".join(summaries)
    except Exception as e: return f"Error accessing calendar: {e}"

# Aliases for backward compatibility
get_calendar_events = list_upcoming_events

@tool
def create_calendar_event(summary: str, start_time: str, end_time: str, description: str = "") -> str:
    """
    Creates a new event in Google Calendar.
    Args:
        summary: Event title
        start_time: Start time in ISO format (e.g., '2024-01-01T10:00:00')
        end_time: End time in ISO format
        description: Optional event description
    """
    try:
        service = _get_calendar_service()
        event = {
            'summary': summary,
            'description': description,
            'start': {'dateTime': start_time, 'timeZone': 'UTC'},
            'end': {'dateTime': end_time, 'timeZone': 'UTC'},
        }
        event = service.events().insert(calendarId='primary', body=event).execute()
        return f"Event created: {event.get('htmlLink')}"
    except Exception as e:
        return f"Error creating calendar event: {e}"
    
def get_calendar_tools():
    return [list_upcoming_events, create_calendar_event]