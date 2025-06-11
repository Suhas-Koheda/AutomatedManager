import os
import datetime

from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from httpx import HTTPError
from langchain_core.tools import tool

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

@tool
def read_calender(date: str) -> list:
    """Read the calendar using the Calendar API and return the events.
    Takes the date as input and returns a list of events for that date.
    Returns:
        list: A list of events from the calendar.
    """
    creds=None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=8080)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
        token.write(creds.to_json())

    try:
        service = build("calendar", "v3", credentials=creds)
        now=datetime.datetime.now(tz=datetime.timezone.utc).isoformat()
        print("Getting the upcoming 10 events")
        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=now,
                maxResults=10,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])

        if not events:
            print("No upcoming events found.")
            return ["No upcoming events found."]

        return events
    except HTTPError as e:
        print(f"An error occurred: {e}")
        return [f"An error occurred: {e}"]

print(read_calender("2023-10-01"))
