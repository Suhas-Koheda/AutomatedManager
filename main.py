from AutomatedManager.mail.mail_callback import email_callback
from AutomatedManager.mail.mail_watcher import watch_gmail

if __name__ == '__main__':
    print("Starting mail watcher...")
    watch_gmail(email_callback)