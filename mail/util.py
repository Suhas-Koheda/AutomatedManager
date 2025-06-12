import base64
import quopri
import re
from email.header import decode_header

def get_sender(headers):
    """Extract sender from email headers with better encoding handling."""
    for header in headers:
        if header['name'].lower() == 'from':
            sender = header['value']
            try:
                decoded_parts = decode_header(sender)
                decoded_sender = []
                for part, encoding in decoded_parts:
                    if isinstance(part, bytes):
                        decoded_sender.append(part.decode(encoding or 'utf-8', errors='replace'))
                    else:
                        decoded_sender.append(part)
                return ''.join(decoded_sender)
            except:
                return sender
    return "Unknown sender"

def get_simple_email_body(payload, depth=0):
    """Extract plain text body from email payload with forwarded message support."""
    MAX_DEPTH = 3  # Prevent infinite recursion

    def decode_body(data):
        try:
            return base64.urlsafe_b64decode(data).decode('utf-8')
        except:
            try:
                return quopri.decodestring(data).decode('utf-8', errors='replace')
            except:
                return data

    def clean_forwarded_content(text):
        """Remove common forwarding markers and headers."""
        # Remove "Begin forwarded message" sections
        text = re.sub(r'-+\s*Begin forwarded message\s*-+.*?(\n\s*\n)', '', text, flags=re.DOTALL)
        # Remove quoted headers (From:, Date:, Subject:, etc.)
        text = re.sub(r'(?m)^(>|\s)*(From|Sent|To|Subject|Date):.*$', '', text)
        # Remove excessive newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()

    # Base case for recursion
    if depth > MAX_DEPTH:
        return "Max depth reached in forwarded message"

    # Check for multipart payload
    if 'parts' in payload:
        for part in payload['parts']:
            # Prefer text/plain but fallback to text/html if needed
            if part['mimeType'] in ['text/plain', 'text/html']:
                if 'body' in part and 'data' in part['body']:
                    body = decode_body(part['body']['data'])
                    if body.strip():
                        return clean_forwarded_content(body)

            # Handle nested forwarded messages (message/rfc822)
            elif part['mimeType'] == 'message/rfc822':
                if 'parts' in part:
                    nested_body = get_simple_email_body(part, depth+1)
                    if nested_body and nested_body != "No body content":
                        return clean_forwarded_content(nested_body)

    # Check direct body content
    if 'body' in payload and 'data' in payload['body']:
        body = decode_body(payload['body']['data'])
        if body.strip():
            return clean_forwarded_content(body)

    return "No body content"