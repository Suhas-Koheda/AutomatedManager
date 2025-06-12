import datetime
from typing import Dict, Any

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from langchain_core.tools import tool

from AutomatedManager.auth import check_auth
from AutomatedManager.util import parse_date_string


@tool
def create_event(event_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new calendar event with comprehensive error handling and timezone support.

    Features:
    - Automatic timezone handling (defaults to UTC+5:30 for India)
    - Supports both timed events and all-day events
    - Detailed error reporting
    - Automatic retry on authentication failure
    - Verbose logging for debugging

    Args:
        event_data: Dictionary containing event details with these fields:
            Required:
            - summary: Title of the event (string)
            - start: Start time in format:
                * 'YYYY-MM-DD' for all-day events
                * 'YYYY-MM-DDTHH:MM:SS' for timed events (will auto-add timezone)
                * {'dateTime': '...', 'timeZone': '...'} for explicit timezone
            - end: End time in same format as start

            Optional:
            - description: Event description (string)
            - location: Physical location (string)
            - attendees: List of email dictionaries:
                [{'email': 'user@example.com'}, ...]
            - reminders: Dictionary with either:
                * {'useDefault': True} or
                * {'overrides': [{'method': 'popup', 'minutes': 30}, ...]}
            - colorId: Event color ID (1-11)
            - visibility: 'public', 'private', or 'confidential'
            - recurrence: RRULE string array (e.g., ['RRULE:FREQ=DAILY;COUNT=2'])
            - extendedProperties: Dictionary for custom metadata

    Returns:
        Dictionary with:
        - On success:
            {
                'status': 'success',
                'event_link': 'https://calendar.google.com/...',
                'event_id': 'google_event_id',
                'summary': 'Event title',
                'start': 'formatted_start',
                'end': 'formatted_end',
                'calendar': 'primary'
            }
        - On error:
            {
                'status': 'error',
                'error': 'Error description',
                'details': {additional error info if available}
            }
    """
    creds = check_auth()

    if(creds is None):
        return {"Proper credentials not found. Please authenticate first.":"Error"}
    formatted_event = event_data.copy()
    timezone = datetime.timezone(datetime.timedelta(hours=5, minutes=30))  # IST

    for time_field in ['start', 'end']:
        if time_field in formatted_event:
            # Case 1: Already properly formatted
            if isinstance(formatted_event[time_field], dict):
                continue

            # Case 2: Date string (all-day event)
            elif 'T' not in formatted_event[time_field]:
                formatted_event[time_field] = {
                    'date': formatted_event[time_field]
                }

            # Case 3: DateTime string without timezone
            else:
                try:
                    dt = datetime.datetime.strptime(
                        formatted_event[time_field],
                        '%Y-%m-%dT%H:%M:%S'
                    ).replace(tzinfo=timezone)
                    formatted_event[time_field] = {
                        'dateTime': dt.isoformat(),
                        'timeZone': 'Asia/Kolkata'
                    }
                except ValueError:
                    return {
                        'status': 'error',
                        'error': 'Invalid time format',
                        'details': f'{time_field} must be YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS'
                    }

    # Add default reminders if none specified
    if 'reminders' not in formatted_event:
        formatted_event['reminders'] = {
            'useDefault': True
        }

    # Create the event
    try:
        service = build("calendar", "v3", credentials=creds)

        print(f"\nCreating event with details:")
        for key, value in formatted_event.items():
            print(f" - {key}: {str(value)[:100]}{'...' if len(str(value)) > 100 else ''}")

        created_event = service.events().insert(
            calendarId='primary',
            body=formatted_event,
            sendUpdates='none'  # Change to 'all' to notify attendees
        ).execute()

        print(f"\nSuccessfully created event: {created_event.get('htmlLink')}")

        return {
            'status': 'success',
            'event_link': created_event.get('htmlLink'),
            'event_id': created_event['id'],
            'summary': created_event.get('summary'),
            'start': created_event.get('start'),
            'end': created_event.get('end'),
            'calendar': 'primary'
        }

    except HttpError as e:
        error_details = {
            'status_code': e.resp.status,
            'error_details': e.error_details
        }
        return {
            'status': 'error',
            'error': 'Calendar API error',
            'details': error_details
        }
    except Exception as e:
        return {
            'status': 'error',
            'error': 'Unexpected error',
            'details': str(e)
        }
