from datetime import datetime

from agent.agent import mailer_agent


def email_callback(new_emails):
    """Example callback function to process new emails."""
    print(f"\nNew emails received at {datetime.now()}:")
    for email in new_emails:
        print(email)
        mailer_agent.invoke({"input":f"""
        GUARDRAILS:
         NEVER DUPLICATE ANY EVENT ON THAT PARTICULAR DAY
         ----------------------------------------------
        Process the following email:
        {email}
        i have given you the contents of the email and you are asked to clean the email
        dont duplicate events 
        extract the required contents and create an event on that particular day of event 
        check for any other events on that day 
        if there are any other evets dont to anything
         if there are no events create an event with the details provided in the email 
         send me the link to the event created 
         You should and have to use tools not just get out easily
          you should also print a detailed response on what happened 
        """})