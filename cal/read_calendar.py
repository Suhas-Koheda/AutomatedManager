import datetime

from langchain_core.tools import tool
from googleapiclient.discovery import build

from util import parse_date_string
from auth import check_auth

@tool
def read_calendar(date_str: str) -> list:
    """Read cal events within a date range with enhanced debugging."""
    try:
        date, days_before, days_after = parse_date_string(date_str)
    except Exception as e:
        return [{"error": f"Invalid date format: {str(e)}. Use YYYY-MM-DD/before=X/after=Y"}]

    creds = check_auth()

    if creds is None:
        return ["Proper credentials not found. Please authenticate first."]


    try:
        service = build("cal", "v3", credentials=creds)
        all_events = []

        tz = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
        try:
            central_date = datetime.datetime.strptime(date, "%Y-%m-%d").replace(tzinfo=tz)
        except ValueError:
            return [{"error": "Invalid date format. Please use YYYY-MM-DD"}]

        start_date = (central_date - datetime.timedelta(days=days_before)).replace(
            hour=0, minute=0, second=0, microsecond=0)
        end_date = (central_date + datetime.timedelta(days=days_after + 1)).replace(
            hour=0, minute=0, second=0, microsecond=0)

        print(f"\nSearching events from {start_date.date()} to {end_date.date()-datetime.timedelta(days=1)}")

        try:
            calendar_list = service.calendarList().list(
                minAccessRole="reader",
                showHidden=True
            ).execute()
            calendars = calendar_list.get('items', [])
            print(f"\nFound {len(calendars)} calendars:")
            for cal in calendars:
                print(f" - {cal.get('summary', 'Unnamed')} (ID: {cal['id']})")
        except Exception as e:
            print(f"\nError getting calendars: {e}")
            calendars = []

        calendars.insert(0, {'id': 'primary', 'summary': 'Primary Calendar'})

        for calendar in calendars:
            calendar_id = calendar['id']
            calendar_name = calendar.get('summary', 'Unnamed Calendar')
            print(f"\nChecking cal: {calendar_name} ({calendar_id})")

            try:
                events_result = service.events().list(
                    calendarId=calendar_id,
                    timeMin=start_date.isoformat(),
                    timeMax=end_date.isoformat(),
                    singleEvents=True,
                    orderBy="startTime",
                    showDeleted=False
                ).execute()

                events = events_result.get('items', [])
                print(f"Found {len(events)} events in {calendar_name}")

                for event in events:
                    # Skip cancelled events
                    if event.get('status') == 'cancelled':
                        continue

                    start = event.get('start', {})
                    end = event.get('end', {})

                    event_date = start.get('dateTime', start.get('date'))
                    if not event_date:
                        continue

                    formatted_event = {
                        'summary': event.get('summary', 'No title'),
                        'start': start,
                        'end': end,
                        'cal': calendar_name,
                        'date': event_date[:10],
                        'description': event.get('description', '')[:100] + '...' if event.get('description') else '',
                        'location': event.get('location', ''),
                        'status': event.get('status', 'confirmed')
                    }
                    all_events.append(formatted_event)

                    if 'thug life' in formatted_event['summary'].lower():
                        print("\nFOUND THUG LIFE EVENT:")
                        print(formatted_event)

            except Exception as e:
                print(f"\nError accessing cal {calendar_name}: {e}")
                continue

        if not all_events:
            return [{
                'summary': f'No events found between {start_date.date()} and {end_date.date()-datetime.timedelta(days=1)}',
                'date_range': {
                    'start': start_date.date().isoformat(),
                    'end': (end_date.date()-datetime.timedelta(days=1)).isoformat()
                },
                'calendars_checked': len(calendars),
                'note': 'Try expanding the date range or check if the event exists in another cal'
            }]

        all_events.sort(key=lambda x: x['date'])

        # Debug output
        print("\nAll found events:")
        for event in all_events:
            print(f"{event['date']} - {event['summary']} ({event['calendar']})")

        return all_events

    except Exception as e:
        return [{"error": f"Calendar API error: {str(e)}"}]