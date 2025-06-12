# Automated Manager

An automated system that watches your Gmail inbox and creates calendar events based on email content using Google's APIs and AI assistance.

## Features

- **Email Monitoring**: Continuously watches your Gmail inbox for new emails
- **Automated Event Creation**: Extracts event information from emails and creates calendar events
- **AI-Powered**: Uses Google's Gemini 1.5 Flash model to intelligently process email content
- **Duplicate Prevention**: Checks existing calendar events to avoid duplicates
- **Google Calendar Integration**: Creates and reads events in your Google Calendar

## Prerequisites

- Python 3.8+
- Google account with Gmail and Calendar access
- Google Cloud Platform project with Gmail and Calendar APIs enabled
- OAuth 2.0 Client ID credentials from GCP

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd AutomatedManager
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Place your Google Cloud Platform OAuth credentials file (`credentials.json`) in the root directory of the project.

## Configuration

1. **Authentication Setup**:
   - When you run the application for the first time, it will open a browser window for Google authentication
   - Grant the requested permissions to allow the application to access your Gmail and Calendar
   - A `token.json` file will be created to store your authentication tokens

2. **Permissions**:
   The application requires the following Google API scopes:
   - Gmail read access
   - Gmail modify access (to mark emails as read)
   - Calendar read access
   - Calendar write access

## Usage

### Running the Application

To start the application in the foreground:

```bash
python -m AutomatedManager.main
```

### Running in the Background

To run the application as a background process with logging, you have two options:

#### Option 1: Using nohup with stdout/stderr redirection

```bash
nohup python -m AutomatedManager.main > automated_manager.log 2>&1 &
```

This command will:
- Start the application in the background
- Redirect standard output and errors to `automated_manager.log`
- Return the process ID that you can use to monitor or stop the process

#### Option 2: Using the built-in logging feature (recommended)

```bash
nohup python -m AutomatedManager.main --log-to-file &
```

This command will:
- Start the application in the background with proper timestamp-based logging
- Create a log file in the `logs/` directory with format `automated_manager_YYYYMMDD_HHMMSS.log`
- Log both to the file and to stdout/stderr
- Return the process ID that you can use to monitor or stop the process

### Checking Logs

You can view the redirect logs in real-time using:

```bash
tail -f automated_manager.log
```

Or if using the built-in logging feature:

```bash
# Find the latest log file
ls -t logs/ | head -1
# View logs in real-time
tail -f logs/automated_manager_YYYYMMDD_HHMMSS.log
```

### Stopping the Background Process

1. Find the process ID:
   ```bash
   ps aux | grep AutomatedManager
   ```

2. Stop the process:
   ```bash
   kill <process-id>
   ```

## How It Works

1. The application authenticates with Google using OAuth 2.0
2. It starts watching your Gmail inbox for new messages
3. When a new email arrives, it's processed by the email callback function
4. The Gemini AI agent analyzes the email content to extract event details
5. The agent checks for existing events on the same date to avoid duplicates
6. If no duplicates are found, a new calendar event is created with the extracted information
7. The process continues running, monitoring for new emails

## Project Structure

- `main.py`: Entry point for the application
- `auth.py`: Handles Google API authentication
- `agent/agent.py`: Sets up the AI agent for processing emails
- `mail/mail_watcher.py`: Monitors Gmail inbox for new messages
- `mail/mail_callback.py`: Processes new emails when they arrive
- `calendar/create_event.py`: Creates new calendar events
- `calendar/read_calendar.py`: Reads existing calendar events

## Troubleshooting

- **Authentication Issues**: Delete the `token.json` file and restart the application to re-authenticate
- **API Rate Limits**: If you see errors about exceeding quota, reduce the check frequency or create a new GCP project
- **Missing Events**: Check the logs for any errors in email processing or event creation

## License

[Your License Information]

## Acknowledgments

- Built with LangChain and Google's Gemini API
- Uses Google Calendar and Gmail APIs
