
# Required libraries:
# pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib

import os.path
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Define the scope for the Gmail API. 'readonly' is best practice for reading emails.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_gmail_service():
    """
    Authenticates with the Gmail API and returns a service object.
    Handles the OAuth 2.0 flow, creating a token.json file for future use.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens.
    # It's created automatically when the authorization flow completes for the first time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"Failed to refresh token: {e}")
                # If refresh fails, force re-authentication
                creds = None
        
        if not creds:
            # Make sure credentials.json is present
            if not os.path.exists('credentials.json'):
                print("Error: credentials.json not found. Please download it from the Google Cloud Console.")
                return None
            
            # Start the OAuth flow to get new credentials
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            # Use run_local_server which is robust for desktop/Pi environments
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
            print("Token file created successfully.")

    try:
        # Build the Gmail API service object
        service = build('gmail', 'v1', credentials=creds)
        return service
    except HttpError as error:
        print(f'An error occurred while building the service: {error}')
        return None

def get_unread_emails(max_results=5):
    """
    Fetches the most recent unread emails from the inbox.

    Args:
        max_results (int): The maximum number of unread emails to return.

    Returns:
        list: A list of dictionaries, each containing the 'id', 'sender', and 'subject' of an email.
              Returns an empty list if no unread emails are found or an error occurs.
    """
    service = get_gmail_service()
    if not service:
        return []

    try:
        # Search for unread messages in the INBOX
        results = service.users().messages().list(
            userId='me', 
            labelIds=['INBOX', 'UNREAD'], 
            maxResults=max_results
        ).execute()
        
        messages = results.get('messages', [])
        
        if not messages:
            print("No unread emails found.")
            return []

        email_list = []
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id'], format='metadata').execute()
            headers = msg['payload']['headers']
            
            # Extract sender and subject from headers
            subject = next((i['value'] for i in headers if i['name'] == 'Subject'), '')
            sender = next((i['value'] for i in headers if i['name'] == 'From'), '')
            
            email_list.append({
                'id': message['id'],
                'sender': sender,
                'subject': subject
            })
            
        return email_list

    except HttpError as error:
        print(f'An error occurred while fetching emails: {error}')
        return []

def read_email_body(message_id):
    """
    Reads the plain text body content of a specific email.

    Args:
        message_id (str): The ID of the email to read.

    Returns:
        str: The plain text body of the email, or an empty string if not found or an error occurs.
    """
    service = get_gmail_service()
    if not service:
        return ""

    try:
        message = service.users().messages().get(userId='me', id=message_id, format='full').execute()
        payload = message.get('payload', {})
        parts = payload.get('parts', [])

        # The body can be in the main payload or in parts for multipart messages
        if 'data' in payload['body']:
            data = payload['body']['data']
            return base64.urlsafe_b64decode(data).decode('utf-8')
        
        # If it's a multipart message, find the plain text part
        if parts:
            for part in parts:
                if part['mimeType'] == 'text/plain' and 'data' in part['body']:
                    data = part['body']['data']
                    return base64.urlsafe_b64decode(data).decode('utf-8')
        
        return "Could not find plain text body for this email."

    except HttpError as error:
        print(f'An error occurred while reading the email body: {error}')
        return ""

# --- Example Usage ---
if __name__ == '__main__':
    print("--- Checking for unread emails ---")
    
    # Get a list of unread emails
    unread_emails = get_unread_emails(max_results=3)
    
    if unread_emails:
        print(f"Found {len(unread_emails)} unread emails:")
        for email_info in unread_emails:
            print(f"\n  ID: {email_info['id']}")
            print(f"  From: {email_info['sender']}")
            print(f"  Subject: {email_info['subject']}")
        
        # Choose the first email from the list to read its body
        first_email_id = unread_emails[0]['id']
        print(f"\n--- Reading the body of the first email (ID: {first_email_id}) ---")
        
        email_body = read_email_body(first_email_id)
        
        if email_body:
            # Print a snippet of the body
            print("\nEmail Body Snippet:")
            print("-" * 20)
            print(email_body[:500] + "..." if len(email_body) > 500 else email_body)
            print("-" * 20)
        else:
            print("Could not retrieve the email body.")
            
    else:
        print("\nNo new messages to display.")
