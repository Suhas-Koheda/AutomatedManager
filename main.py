
from mail.mail_watcher import watch_gmail

from mail.mail_callback import email_callback

if __name__ == '__main__':
    print("Starting mail watcher...")
    watch_gmail(email_callback)