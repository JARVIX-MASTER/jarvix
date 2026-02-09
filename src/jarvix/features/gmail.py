"""
Gmail Automation Feature for Jarvix Agent
Uses IMAP with App Password (no OAuth) to read, process, and categorize emails.
"""

import imaplib
import email
from email.header import decode_header
from email.utils import parsedate_to_datetime
import os
import re
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# Gmail IMAP Settings
IMAP_SERVER = "imap.gmail.com"
IMAP_PORT = 993

# Email address and app password from environment
GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")

# Keywords for categorization
PROMOTIONAL_KEYWORDS = [
    "unsubscribe", "newsletter", "promotion", "discount", "sale", "offer",
    "deal", "coupon", "marketing", "advertisement", "subscribe", "weekly digest",
    "special offer", "limited time", "exclusive deal", "free shipping"
]

# STRICT interview keywords - require these specific terms for interview detection
# Using two tiers: strong keywords (high confidence) and weak keywords (need multiple)
INTERVIEW_STRONG_KEYWORDS = [
    "interview scheduled", "interview invitation", "interview confirmation",
    "phone screen", "technical interview", "onsite interview", "virtual interview",
    "interview round", "coding interview", "interview slot", "interview call",
    "shortlisted for interview", "selected for interview", "interview date",
    "zoom interview", "teams interview", "google meet interview"
]

INTERVIEW_WEAK_KEYWORDS = [
    "interview", "recruiter", "hiring manager", "hr call", "screening call",
    "offer letter", "job offer", "congratulations on your application"
]

# Keywords that indicate NOT an interview (false positive prevention)
INTERVIEW_EXCLUDE_KEYWORDS = [
    "unsubscribe", "newsletter", "daily digest", "weekly update", "marketing",
    "job alert", "new jobs", "jobs matching", "similar jobs", "recommended jobs",
    "job recommendations", "apply now", "save job", "easy apply"
]

# Date patterns for extracting interview dates
DATE_PATTERNS = [
    r'\b(\d{1,2}(?:st|nd|rd|th)?\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4})\b',
    r'\b(\d{1,2}/\d{1,2}/\d{4})\b',
    r'\b(\d{4}-\d{2}-\d{2})\b',
    r'\b((?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)[a-z]*,?\s+\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*)\b',
]

TIME_PATTERNS = [
    r'\b(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)?)\b',
    r'\b(\d{1,2}\s*(?:AM|PM|am|pm))\b',
]


class GmailClient:
    """Gmail IMAP client for reading and processing emails."""
    
    def __init__(self):
        self.mail = None
        self.connected = False
        
    def connect(self):
        """Establish secure IMAP connection to Gmail."""
        if not GMAIL_ADDRESS or not GMAIL_APP_PASSWORD:
            print("❌ Gmail credentials not found in .env")
            return False
            
        try:
            self.mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
            # Remove spaces from app password
            password = GMAIL_APP_PASSWORD.replace(" ", "")
            self.mail.login(GMAIL_ADDRESS, password)
            self.connected = True
            print(f"✅ Connected to Gmail: {GMAIL_ADDRESS}")
            return True
        except imaplib.IMAP4.error as e:
            print(f"❌ Gmail login failed: {e}")
            return False
        except Exception as e:
            print(f"❌ Gmail connection error: {e}")
            return False
    
    def disconnect(self):
        """Close IMAP connection."""
        if self.mail:
            try:
                self.mail.logout()
            except:
                pass
        self.connected = False
    
    def _decode_header_value(self, value):
        """Decode email header values (handles encoded subjects)."""
        if not value:
            return ""
        decoded_parts = decode_header(value)
        result = ""
        for part, charset in decoded_parts:
            if isinstance(part, bytes):
                result += part.decode(charset or 'utf-8', errors='ignore')
            else:
                result += part
        return result
    
    def _extract_body(self, msg):
        """Extract plain text body from email message."""
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == "text/plain":
                    try:
                        payload = part.get_payload(decode=True)
                        if payload:
                            charset = part.get_content_charset() or 'utf-8'
                            body = payload.decode(charset, errors='ignore')
                            break
                    except:
                        pass
        else:
            try:
                payload = msg.get_payload(decode=True)
                if payload:
                    charset = msg.get_content_charset() or 'utf-8'
                    body = payload.decode(charset, errors='ignore')
            except:
                pass
        return body[:5000]  # Limit body length
    
    def _get_unsubscribe_link(self, msg, body):
        """Extract unsubscribe link from email headers or body."""
        # Check List-Unsubscribe header first
        unsub_header = msg.get("List-Unsubscribe", "")
        if unsub_header:
            # Extract URL from header like <http://...> or <mailto:...>
            urls = re.findall(r'<(https?://[^>]+)>', unsub_header)
            if urls:
                return urls[0]
        
        # Search in body for unsubscribe links
        unsub_patterns = [
            r'href=["\']?(https?://[^"\'>\s]*unsubscribe[^"\'>\s]*)["\']?',
            r'(https?://[^\s<>"]+unsubscribe[^\s<>"]*)',
        ]
        for pattern in unsub_patterns:
            matches = re.findall(pattern, body, re.IGNORECASE)
            if matches:
                return matches[0]
        return None
    
    def _extract_dates_from_text(self, text):
        """Extract potential interview dates from email text."""
        found_dates = []
        for pattern in DATE_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    # Try parsing the date
                    date_str = match
                    # Attempt common formats
                    for fmt in ["%d %B %Y", "%d/%m/%Y", "%Y-%m-%d", "%d %b %Y"]:
                        try:
                            dt = datetime.strptime(date_str.strip(), fmt)
                            if dt > datetime.now():  # Only future dates
                                found_dates.append(dt)
                            break
                        except:
                            continue
                except:
                    pass
        
        # Also try to find associated times
        times = re.findall('|'.join(TIME_PATTERNS), text, re.IGNORECASE)
        
        return found_dates, times
    
    def categorize_email(self, subject, body, sender):
        """
        Categorize an email based on content.
        Returns: 'promotional', 'interview', 'upcoming_interview', or 'general'
        
        Uses strict two-tier matching for interviews to reduce false positives.
        """
        combined_text = f"{subject} {body} {sender}".lower()
        subject_lower = subject.lower()
        
        # First check for exclusion keywords - if found, NOT an interview email
        has_exclude = any(kw in combined_text for kw in INTERVIEW_EXCLUDE_KEYWORDS)
        
        # Check promotional keywords
        promo_score = sum(1 for kw in PROMOTIONAL_KEYWORDS if kw in combined_text)
        
        # STRICT Interview detection:
        # 1. Strong keyword in subject = definite interview
        # 2. Strong keyword in body = likely interview
        # 3. Multiple weak keywords = possible interview (only if no exclusions)
        
        strong_in_subject = any(kw in subject_lower for kw in INTERVIEW_STRONG_KEYWORDS)
        strong_in_body = any(kw in combined_text for kw in INTERVIEW_STRONG_KEYWORDS)
        weak_count = sum(1 for kw in INTERVIEW_WEAK_KEYWORDS if kw in combined_text)
        
        is_interview = False
        
        if strong_in_subject:
            # Strong keyword in subject = definitely interview
            is_interview = True
        elif strong_in_body and not has_exclude:
            # Strong keyword in body (and no exclusions) = likely interview
            is_interview = True
        elif weak_count >= 3 and not has_exclude:
            # Multiple weak keywords without exclusions = possible interview
            is_interview = True
        
        if is_interview:
            # Check for FUTURE dates only
            dates, times = self._extract_dates_from_text(body)
            if dates:
                return "upcoming_interview"
            return "interview"
        
        # Promotional detection (after interview, so interview emails aren't marked promo)
        if promo_score >= 2:
            return "promotional"
        
        return "general"
    
    def fetch_emails(self, folder="INBOX", limit=50, unread_only=False):
        """
        Fetch recent emails from specified folder.
        Returns list of email dictionaries with parsed content.
        """
        if not self.connected and not self.connect():
            return None
        
        try:
            self.mail.select(folder)
            
            # Search criteria
            if unread_only:
                search_criteria = "UNSEEN"
            else:
                search_criteria = "ALL"
            
            status, messages = self.mail.search(None, search_criteria)
            if status != "OK":
                return []
            
            email_ids = messages[0].split()
            # Get most recent emails
            email_ids = email_ids[-limit:] if len(email_ids) > limit else email_ids
            email_ids = email_ids[::-1]  # Newest first
            
            emails = []
            for eid in email_ids:
                try:
                    status, msg_data = self.mail.fetch(eid, "(RFC822)")
                    if status != "OK":
                        continue
                    
                    raw_email = msg_data[0][1]
                    msg = email.message_from_bytes(raw_email)
                    
                    # Parse email fields
                    subject = self._decode_header_value(msg.get("Subject", ""))
                    sender = self._decode_header_value(msg.get("From", ""))
                    date_str = msg.get("Date", "")
                    
                    # Parse date
                    try:
                        date = parsedate_to_datetime(date_str)
                        date_formatted = date.strftime("%b %d, %Y %I:%M %p")
                    except:
                        date_formatted = date_str[:24]
                        date = None
                    
                    # Extract body
                    body = self._extract_body(msg)
                    
                    # Categorize
                    category = self.categorize_email(subject, body, sender)
                    
                    # Get unsubscribe link for promotional emails
                    unsub_link = None
                    if category == "promotional":
                        unsub_link = self._get_unsubscribe_link(msg, body)
                    
                    # Extract interview dates if applicable
                    interview_dates = []
                    interview_times = []
                    if category in ["interview", "upcoming_interview"]:
                        interview_dates, interview_times = self._extract_dates_from_text(body)
                    
                    email_dict = {
                        "id": eid.decode(),
                        "subject": subject[:200],  # Truncate long subjects
                        "sender": sender,
                        "date": date_formatted,
                        "date_obj": date,
                        "category": category,
                        "body_preview": body[:500],
                        "unsubscribe_link": unsub_link,
                        "interview_dates": [d.strftime("%B %d, %Y") for d in interview_dates],
                        "interview_times": interview_times[:3],
                    }
                    emails.append(email_dict)
                    
                except Exception as e:
                    print(f"Error parsing email {eid}: {e}")
                    continue
            
            return emails
            
        except Exception as e:
            print(f"❌ Error fetching emails: {e}")
            return None
        finally:
            self.disconnect()
    
    def get_all_categorized(self, limit=30):
        """
        Fetch and categorize all recent emails.
        Returns dict with emails grouped by category.
        """
        emails = self.fetch_emails(limit=limit)
        if emails is None:
            return None
        
        categorized = {
            "promotional": [],
            "interview": [],
            "upcoming_interview": [],
            "general": []
        }
        
        for email_item in emails:
            category = email_item["category"]
            categorized[category].append(email_item)
        
        # Add summary
        categorized["summary"] = {
            "total": len(emails),
            "promotional": len(categorized["promotional"]),
            "interview": len(categorized["interview"]),
            "upcoming_interview": len(categorized["upcoming_interview"]),
            "general": len(categorized["general"])
        }
        
        return categorized
    
    def get_upcoming_interviews(self, limit=20):
        """
        Get emails containing upcoming interview dates.
        Returns list of interview-related emails with extracted dates.
        """
        emails = self.fetch_emails(limit=limit)
        if emails is None:
            return None
        
        upcoming = []
        for email_item in emails:
            if email_item["category"] in ["interview", "upcoming_interview"]:
                if email_item["interview_dates"]:
                    upcoming.append(email_item)
        
        # Also include recent interview emails even without dates
        interview_emails = [e for e in emails if e["category"] == "interview" and e not in upcoming]
        
        return {
            "with_dates": upcoming,
            "recent_interviews": interview_emails[:5]
        }
    
    def get_promotional_emails(self, limit=20):
        """
        Get promotional emails with unsubscribe links.
        Returns list of promotional emails.
        """
        emails = self.fetch_emails(limit=limit)
        if emails is None:
            return None
        
        promotional = [e for e in emails if e["category"] == "promotional"]
        
        # Separate those with unsubscribe links
        with_unsub = [e for e in promotional if e["unsubscribe_link"]]
        without_unsub = [e for e in promotional if not e["unsubscribe_link"]]
        
        return {
            "with_unsubscribe": with_unsub,
            "without_unsubscribe": without_unsub,
            "total": len(promotional)
        }


# Helper function for quick testing
def test_connection():
    """Test Gmail connection with configured credentials."""
    client = GmailClient()
    if client.connect():
        print("✅ Gmail connection successful!")
        client.disconnect()
        return True
    else:
        print("❌ Gmail connection failed!")
        return False


if __name__ == "__main__":
    # Quick test
    test_connection()
