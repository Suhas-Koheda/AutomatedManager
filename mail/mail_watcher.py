import time

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from AutomatedManager.auth import check_auth
from AutomatedManager.mail.mail_callback import email_callback
from AutomatedManager.mail.util import get_sender,get_simple_email_body


def watch_gmail(callback, check_interval=10):
    """
    Watch Gmail inbox for new messages and execute callback when new emails arrive.

    Args:
        callback (function): Function to call when new emails are detected.
                            Receives list of email dictionaries with sender and body.
        check_interval (int): How often to check for new emails (in seconds).
    """
    creds = check_auth()
    service = build('gmail', 'v1', credentials=creds)

    # Get the initial history ID by getting the most recent message
    try:
        # First get the latest message to get a valid historyId
        results = service.users().messages().list(
            userId='me',
            maxResults=1,
            labelIds=['INBOX']
        ).execute()

        if 'messages' in results and results['messages']:
            message = service.users().messages().get(
                userId='me',
                id=results['messages'][0]['id'],
                format='metadata',
                metadataHeaders=['from', 'subject']
            ).execute()
            last_history_id = message.get('historyId')
        else:
            # If no messages in inbox, start with current time
            last_history_id = str(int(time.time() * 1000))

    except HttpError as error:
        print(f"Initial setup error: {error}")
        # Fallback to current time if history ID can't be obtained
        last_history_id = str(int(time.time() * 1000))

    print(f"Gmail watcher started. Using history ID: {last_history_id}")

    while True:
        try:
            # Check for changes since last history ID
            history = service.users().history().list(
                userId='me',
                startHistoryId=last_history_id,
                labelId='INBOX'
            ).execute()

            if 'history' in history:
                # Process new messages
                messages = []
                for h in history['history']:
                    if 'messagesAdded' in h:
                        for msg in h['messagesAdded']:
                            message = service.users().messages().get(
                                userId='me',
                                id=msg['message']['id'],
                                format='full'
                            ).execute()

                            if 'payload' not in message:
                                continue

                            payload = message['payload']
                            headers = payload.get('headers', [])

                            messages.append({
                                "sender": get_sender(headers),
                                "body": get_simple_email_body(payload),
                                "id": msg['message']['id']
                            })

                if messages:
                    callback(messages)

                # Update the last history ID
                last_history_id = history['historyId']

            time.sleep(check_interval)

        except HttpError as error:
            if error.resp.status == 404:
                # History ID might be too old, get a new one
                print("History ID not found, getting new history ID...")
                results = service.users().messages().list(
                    userId='me',
                    maxResults=1,
                    labelIds=['INBOX']
                ).execute()
                if 'messages' in results and results['messages']:
                    message = service.users().messages().get(
                        userId='me',
                        id=results['messages'][0]['id'],
                        format='metadata'
                    ).execute()
                    last_history_id = message.get('historyId')
            else:
                print(f"An error occurred: {error}")
            time.sleep(30)  # Wait before retrying
        except Exception as e:
            print(f"Unexpected error: {e}")
            time.sleep(30)