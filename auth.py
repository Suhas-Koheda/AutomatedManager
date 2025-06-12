import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


SCOPES=["https://www.googleapis.com/auth/calendar.readonly","https://www.googleapis.com/auth/calendar","https://www.googleapis.com/auth/gmail.readonly",'https://www.googleapis.com/auth/gmail.modify']

def check_auth():
    creds = None
    token_file = "token.json"
    creds_file = "credentials.json"

    if not os.path.exists(creds_file):
        raise FileNotFoundError(f"Credentials file not found at {creds_file}")

    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(creds_file, SCOPES)
            creds = flow.run_local_server(port=8088)
        with open(token_file, "w") as token:
            token.write(creds.to_json())

    return creds