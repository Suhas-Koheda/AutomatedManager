import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly", "https://www.googleapis.com/auth/calendar", "https://www.googleapis.com/auth/gmail.readonly", 'https://www.googleapis.com/auth/gmail.modify']

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
            # Manually handle the Out-of-Band (OOB) flow for headless environments
            flow = InstalledAppFlow.from_client_secrets_file(
                creds_file,
                SCOPES,
                # This redirect_uri is crucial for the OOB flow
                redirect_uri='urn:ietf:wg:oauth:2.0:oob'
            )

            # Generate the authorization URL
            auth_url, _ = flow.authorization_url(prompt='consent')

            print('Please visit this URL to authorize this application:')
            print(auth_url)

            # Get the authorization code from the user
            code = input('Enter the authorization code: ')

            # Exchange the code for a token
            flow.fetch_token(code=code)
            creds = flow.credentials

        with open(token_file, "w") as token:
            token.write(creds.to_json())

    return creds