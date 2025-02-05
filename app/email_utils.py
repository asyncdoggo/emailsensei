from html.parser import HTMLParser
from io import StringIO
import email
import imaplib


def set_credentials(username, password):
    """Sets the IMAP credentials. and check if the credentials are valid.

      Args:
        username: The Gmail username.
        password: The Gmail password.
      """
    try:
        imap_server = 'imap.gmail.com'
        imap_port = 993

        # Create an IMAP connection.
        imap_connection = imaplib.IMAP4_SSL(imap_server, imap_port)

        # Login to the IMAP server.
        imap_connection.login(username, password)
        return True
    
    except:
        return False


def fetch_emails_from_imap(username, password):
    """Fetches emails from IMAP with pagination.

      Args:
        username: The Gmail username.
        password: The Gmail password.
        page_number: The current page number.
        page_size: The number of emails to display per page.

      Returns:
        A list of email messages.
      """

    imap_server = 'imap.gmail.com'
    imap_port = 993

    # Create an IMAP connection.
    imap_connection = imaplib.IMAP4_SSL(imap_server, imap_port)

    # Login to the IMAP server.
    imap_connection.login(username, password)
    # print(f"{imap_connection.list()[1][0] = }")
    # Select the INBOX mailbox.
    imap_connection.select('INBOX', readonly=True)

    # Search for all unread emails.
    emails = imap_connection.search(None, 'X-GM-RAW "Category:Primary"', "UNSEEN")
    # Get the email IDs.

    email_ids = emails[1][0].decode().split(' ')
    # Get the email messages for the current page.
    imap_connection.close()

    email_ids.reverse()

    return email_ids

def decode_emails(email_ids, start_index, end_index, username, password):
    imap_server = 'imap.gmail.com'
    imap_port = 993

    # Create an IMAP connection.
    imap_connection = imaplib.IMAP4_SSL(imap_server, imap_port)
    imap_connection.login(username, password)
    imap_connection.select('INBOX', readonly=True)
    email_messages = []
    
    for email_id in email_ids[start_index:end_index]:
        email_message = imap_connection.fetch(email_id, '(RFC822)')[1][0][1]
        msg = email.message_from_bytes(
            email_message
        )
        email_subject = msg['subject']
        text, encoding = email.header.decode_header(msg['subject'])[0]
        if encoding:
            email_subject = text.decode(encoding)
        email_from = msg['from']
        email_content = ""

        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    email_content = part.get_payload(decode=True).decode('utf-8',
                                                                         errors='ignore')
                    break
        else:
            email_content = msg.get_payload(decode=True).decode('utf-8',
                                                                errors='ignore')

        # Extract Message-ID, In-Reply-To, and References headers
        message_id = msg.get("Message-ID", "")
        in_reply_to = msg.get("In-Reply-To", "")

        # Identify the thread or create a new one
        SingleEmail = {
            'Message ID': message_id,
            'from': email_from,
            'subject': email_subject,
            'content': email_content,
            'IsReply': bool(in_reply_to),  # Check if it's a reply
            'InReplyTo': in_reply_to,  # Add the ID of the parent message
            'StoreReplyThread': [],
            # 'summary': llm.summarize(email_content)
        }

        email_messages.append(SingleEmail)

    # Close the IMAP connection.
    imap_connection.close()

    return email_messages


class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = StringIO()

    def handle_data(self, d):
        self.text.write(d)

    def get_data(self):
        return self.text.getvalue()


def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()
