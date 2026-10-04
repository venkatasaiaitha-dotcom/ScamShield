import imaplib
import email
from email.header import decode_header
import re
import html
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional

def clean_html(raw_html: str) -> str:
    """Strips HTML tags while preserving text and link destinations"""
    # Replace links with text + space + url
    text = re.sub(r'<a\s+(?:[^>]*?\s+)?href=["\']([^"\']*)["\'][^>]*>(.*?)</a>', r'\2 (\1)', raw_html, flags=re.IGNORECASE)
    # Replace breaks and paragraphs with newlines
    text = re.sub(r'<(?:br|p|div|tr)[^>]*>', '\n', text, flags=re.IGNORECASE)
    # Strip remaining tags
    text = re.sub(r'<[^>]+>', ' ', text)
    # Unescape HTML entities
    text = html.unescape(text)
    # Collapse multiple whitespaces/newlines
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n\s*\n+', '\n', text).strip()
    return text

def decode_mime_words(s: str) -> str:
    """Decodes MIME encoded header strings into standard utf-8 text"""
    if not s:
        return ""
    decoded_fragments = []
    for fragment, encoding in decode_header(s):
        if isinstance(fragment, bytes):
            try:
                decoded_fragments.append(fragment.decode(encoding or "utf-8", errors="replace"))
            except Exception:
                decoded_fragments.append(fragment.decode("latin-1", errors="replace"))
        else:
            decoded_fragments.append(str(fragment))
    return "".join(decoded_fragments)

class GmailService:
    IMAP_SERVER = "imap.gmail.com"
    IMAP_PORT = 993

    @classmethod
    def test_connection(cls, email_address: str, app_password: str) -> Tuple[bool, str]:
        """Verifies Gmail IMAP credentials"""
        clean_pwd = app_password.replace(" ", "").strip()
        try:
            mail = imaplib.IMAP4_SSL(cls.IMAP_SERVER, cls.IMAP_PORT)
            mail.login(email_address.strip(), clean_pwd)
            mail.select("INBOX", readonly=True)
            mail.logout()
            return True, "Successfully authenticated with Gmail IMAP."
        except imaplib.IMAP4.error as e:
            err_msg = str(e)
            if "Application-specific password required" in err_msg or "Invalid credentials" in err_msg:
                return False, "Authentication failed. For Gmail, you must generate a 16-character App Password at myaccount.google.com/apppasswords."
            return False, f"Gmail IMAP connection error: {err_msg}"
        except Exception as e:
            return False, f"Failed to connect to Gmail IMAP: {str(e)}"

    @classmethod
    def fetch_recent_messages(
        cls,
        email_address: str,
        app_password: str,
        max_emails: int = 5,
        unread_only: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Connects securely to Gmail via IMAP SSL, fetches the latest messages,
        and parses them into standard ScamShield message formats.
        """
        clean_pwd = app_password.replace(" ", "").strip()
        messages_fetched = []

        mail = imaplib.IMAP4_SSL(cls.IMAP_SERVER, cls.IMAP_PORT)
        try:
            mail.login(email_address.strip(), clean_pwd)
            mail.select("INBOX")

            # Search for unread emails or fallback to all recent emails
            search_criterion = "UNSEEN" if unread_only else "ALL"
            status, response = mail.search(None, search_criterion)

            email_ids = response[0].split()
            if not email_ids and unread_only:
                # If no unread, grab the latest emails to inspect
                status, response = mail.search(None, "ALL")
                email_ids = response[0].split()

            # Take the latest N emails (reverse order)
            target_ids = email_ids[-max_emails:] if len(email_ids) > max_emails else email_ids
            target_ids.reverse()

            for e_id in target_ids:
                status, msg_data = mail.fetch(e_id, "(RFC822)")
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])

                        # Extract Headers
                        raw_subject = msg.get("Subject", "(No Subject)")
                        subject = decode_mime_words(raw_subject)

                        raw_from = msg.get("From", "Unknown Sender")
                        sender = decode_mime_words(raw_from)

                        date_str = msg.get("Date", "")

                        # Extract Body
                        body_content = ""
                        if msg.is_multipart():
                            for part in msg.walk():
                                content_type = part.get_content_type()
                                content_disposition = str(part.get("Content-Disposition"))

                                if "attachment" not in content_disposition:
                                    if content_type == "text/plain":
                                        payload = part.get_payload(decode=True)
                                        if payload:
                                            body_content = payload.decode(errors="replace")
                                            break
                                    elif content_type == "text/html" and not body_content:
                                        payload = part.get_payload(decode=True)
                                        if payload:
                                            body_content = clean_html(payload.decode(errors="replace"))
                        else:
                            payload = msg.get_payload(decode=True)
                            if payload:
                                raw_text = payload.decode(errors="replace")
                                if msg.get_content_type() == "text/html":
                                    body_content = clean_html(raw_text)
                                else:
                                    body_content = raw_text

                        full_text = f"Subject: {subject}\n\n{body_content.strip()}"

                        messages_fetched.append({
                            "id": f"gmail-{e_id.decode()}",
                            "source": "GMAIL",
                            "sender": sender,
                            "recipient": email_address,
                            "content": full_text,
                            "timestamp": datetime.now().strftime("%I:%M %p"),
                            "metadata": {
                                "subject": subject,
                                "raw_date": date_str,
                                "gmail_message_id": e_id.decode()
                            }
                        })
        finally:
            try:
                mail.close()
                mail.logout()
            except Exception:
                pass

        return messages_fetched

gmail_service = GmailService()
