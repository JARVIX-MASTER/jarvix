"""
Gmail Automation Feature for Jarvix Agent
Uses IMAP with App Password (no OAuth) to read, process, and categorize emails.
Supports: Interview detection, Payment reminders, Subscription alerts, Promotional filtering.
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
    "zoom interview", "teams interview", "google meet interview",
    # NEW: Additional strong keywords for better detection
    "assessment scheduled", "coding test scheduled", "coding challenge",
    "hiring challenge", "online assessment", "oa scheduled",
    "interview link", "meet link for interview", "calendar invite",
    "interview process", "interview panel", "interview with",
    "your interview is", "interview at", "interview on",
    "schedule your interview", "reschedule interview",
    "behavioral interview", "system design interview",
    "hr interview", "managerial interview", "final round",
    "aptitude test", "hackathon invite",
]

INTERVIEW_WEAK_KEYWORDS = [
    "interview", "recruiter", "hiring manager", "hr call", "screening call",
    "offer letter", "job offer", "congratulations on your application",
    # NEW: Additional weak keywords
    "assessment", "coding test", "hiring", "candidate", "application status",
    "shortlisted", "selected", "next steps", "next round",
    "talent acquisition", "recruitment", "position",
    "joining date", "onboarding",
]

# Keywords that indicate NOT an interview (false positive prevention)
INTERVIEW_EXCLUDE_KEYWORDS = [
    "unsubscribe", "newsletter", "daily digest", "weekly update", "marketing",
    "job alert", "new jobs", "jobs matching", "similar jobs", "recommended jobs",
    "job recommendations", "apply now", "save job", "easy apply"
]

# --- PAYMENT REMINDER KEYWORDS ---
PAYMENT_STRONG_KEYWORDS = [
    "payment due", "payment reminder", "bill due", "invoice due",
    "emi due", "emi payment", "installment due", "amount due",
    "pay by", "pay before", "payment overdue", "overdue payment",
    "electricity bill", "water bill", "gas bill", "phone bill",
    "credit card payment", "credit card bill", "credit card due",
    "loan payment", "loan emi", "insurance premium",
    "rent due", "rent reminder", "utility bill",
    "autopay failed", "payment failed", "payment declined",
    "minimum payment", "outstanding balance", "balance due",
]

PAYMENT_WEAK_KEYWORDS = [
    "payment", "invoice", "bill", "emi", "due date", "amount",
    "overdue", "outstanding", "reminder", "pay", "charge",
    "debit", "transaction", "receipt",
]

# --- SUBSCRIPTION ALERT KEYWORDS ---
SUBSCRIPTION_STRONG_KEYWORDS = [
    "subscription ending", "subscription expiring", "subscription expires",
    "subscription will end", "subscription cancelled", "subscription canceled",
    "auto-renewal", "auto renewal", "will be renewed", "renewing on",
    "renewal date", "renewal reminder", "upcoming renewal",
    "cancel before", "cancel by", "trial ending", "trial expires",
    "trial will end", "free trial ending", "trial period ending",
    "will be charged", "you will be billed", "billing cycle",
    "plan expires", "plan expiring", "membership expiring",
    "membership renewal", "membership ending",
    "subscription confirmation", "renewal confirmation",
    "downgrade notice", "plan change",
]

SUBSCRIPTION_WEAK_KEYWORDS = [
    "subscription", "renewal", "renew", "trial", "expire",
    "cancel", "billing", "plan", "membership", "premium",
    "upgrade", "downgrade",
]

# Date patterns for extracting dates from email text
DATE_PATTERNS = [
    # "12th Feb 2026", "2nd March 2026", "1st Jan 2026" (ordinals)
    r'\b(\d{1,2}(?:st|nd|rd|th)?\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4})\b',
    # "12/02/2026"
    r'\b(\d{1,2}/\d{1,2}/\d{4})\b',
    # "2026-02-12"
    r'\b(\d{4}-\d{2}-\d{2})\b',
    # "Monday, 12 Feb" or "Mon 12 Feb 2026"
    r'\b((?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)[a-z]*,?\s+\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*(?:\s+\d{4})?)\b',
    # "Feb 12, 2026", "February 12, 2026" (Month Day, Year — very common)
    r'\b((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4})\b',
    # "02-12-2026"
    r'\b(\d{1,2}-\d{1,2}-\d{4})\b',
]

TIME_PATTERNS = [
    r'\b(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)?)\b',
    r'\b(\d{1,2}\s*(?:AM|PM|am|pm))\b',
]

# IMAP search terms to help find interview emails more reliably
IMAP_INTERVIEW_SEARCH_SUBJECTS = [
    "interview", "assessment", "coding test", "hiring challenge",
    "shortlisted", "selected", "screening",
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
        """Extract text body from email message. Falls back to HTML if no plain text."""
        plain_body = ""
        html_body = ""
        
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                try:
                    payload = part.get_payload(decode=True)
                    if not payload:
                        continue
                    charset = part.get_content_charset() or 'utf-8'
                    decoded = payload.decode(charset, errors='ignore')
                    
                    if content_type == "text/plain" and not plain_body:
                        plain_body = decoded
                    elif content_type == "text/html" and not html_body:
                        html_body = decoded
                except:
                    pass
        else:
            try:
                payload = msg.get_payload(decode=True)
                if payload:
                    charset = msg.get_content_charset() or 'utf-8'
                    decoded = payload.decode(charset, errors='ignore')
                    content_type = msg.get_content_type()
                    if content_type == "text/html":
                        html_body = decoded
                    else:
                        plain_body = decoded
            except:
                pass
        
        # Prefer plain text; fall back to stripped HTML
        if plain_body:
            return plain_body[:5000]
        elif html_body:
            return self._strip_html(html_body)[:5000]
        return ""
    
    def _strip_html(self, html_text):
        """Strip HTML tags and decode entities to get readable text."""
        # Remove style and script blocks
        text = re.sub(r'<style[^>]*>.*?</style>', '', html_text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
        # Replace <br> and block tags with newlines
        text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
        text = re.sub(r'</(p|div|tr|li|h[1-6])>', '\n', text, flags=re.IGNORECASE)
        # Remove remaining tags
        text = re.sub(r'<[^>]+>', '', text)
        # Decode common HTML entities
        text = text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
        text = text.replace('&nbsp;', ' ').replace('&quot;', '"').replace('&#39;', "'")
        # Collapse whitespace
        text = re.sub(r'[ \t]+', ' ', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()
    
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
            r'href=["\']?(https?://["\'>\s]*unsubscribe["\'>\s]*)["\']?',
            r'(https?://[^\s<>"]+unsubscribe[^\s<>"]*)',
        ]
        for pattern in unsub_patterns:
            matches = re.findall(pattern, body, re.IGNORECASE)
            if matches:
                return matches[0]
        return None
    
    def _extract_dates_from_text(self, text):
        """Extract potential dates from email text."""
        found_dates = []
        for pattern in DATE_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    date_str = match.strip()
                    # Strip ordinal suffixes (1st, 2nd, 3rd, 4th etc.)
                    cleaned = re.sub(r'(\d+)(?:st|nd|rd|th)', r'\1', date_str)
                    # Remove day-of-week prefix if present
                    cleaned = re.sub(r'^(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)[a-z]*,?\s+', '', cleaned, flags=re.IGNORECASE)
                    
                    # Try many common date formats
                    for fmt in [
                        "%d %B %Y",       # 12 February 2026
                        "%d %b %Y",       # 12 Feb 2026
                        "%d/%m/%Y",       # 12/02/2026
                        "%Y-%m-%d",       # 2026-02-12
                        "%B %d, %Y",      # February 12, 2026
                        "%b %d, %Y",      # Feb 12, 2026
                        "%B %d %Y",       # February 12 2026
                        "%b %d %Y",       # Feb 12 2026
                        "%d-%m-%Y",       # 12-02-2026
                        "%d %b",          # 12 Feb (assume current/next year)
                        "%d %B",          # 12 February
                    ]:
                        try:
                            dt = datetime.strptime(cleaned.strip(), fmt)
                            # If year is 1900 (no year in format), assume current/next year
                            if dt.year == 1900:
                                now = datetime.now()
                                dt = dt.replace(year=now.year)
                                if dt < now:
                                    dt = dt.replace(year=now.year + 1)
                            if dt > datetime.now() - timedelta(days=1):  # Allow today's date too
                                found_dates.append(dt)
                            break
                        except:
                            continue
                except:
                    pass
        
        # Also try to find associated times
        times = re.findall('|'.join(TIME_PATTERNS), text, re.IGNORECASE)
        # Flatten if tuples
        flat_times = []
        for t in times:
            if isinstance(t, tuple):
                flat_times.append(next((x for x in t if x), ''))
            else:
                flat_times.append(t)
        
        return found_dates, [t for t in flat_times if t]
    
    def categorize_email(self, subject, body, sender):
        """
        Categorize an email based on content.
        Returns: 'promotional', 'interview', 'upcoming_interview',
                 'payment_reminder', 'subscription_alert', or 'general'
        
        Uses strict two-tier matching for interviews to reduce false positives.
        """
        combined_text = f"{subject} {body} {sender}".lower()
        subject_lower = subject.lower()
        
        # First check for exclusion keywords - if found, NOT an interview email
        has_exclude = any(kw in combined_text for kw in INTERVIEW_EXCLUDE_KEYWORDS)
        
        # Check promotional keywords
        promo_score = sum(1 for kw in PROMOTIONAL_KEYWORDS if kw in combined_text)
        
        # ── Interview detection ──
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
        elif weak_count >= 2 and not has_exclude:
            # Multiple weak keywords without exclusions = possible interview (lowered from 3)
            is_interview = True
        
        if is_interview:
            # Check for dates
            dates, times = self._extract_dates_from_text(f"{subject} {body}")
            if dates:
                return "upcoming_interview"
            return "interview"
        
        # ── Payment reminder detection ──
        payment_strong = any(kw in combined_text for kw in PAYMENT_STRONG_KEYWORDS)
        payment_weak = sum(1 for kw in PAYMENT_WEAK_KEYWORDS if kw in combined_text)
        
        if payment_strong or (payment_weak >= 3 and not has_exclude):
            return "payment_reminder"
        
        # ── Subscription alert detection ──
        sub_strong = any(kw in combined_text for kw in SUBSCRIPTION_STRONG_KEYWORDS)
        sub_weak = sum(1 for kw in SUBSCRIPTION_WEAK_KEYWORDS if kw in combined_text)
        
        if sub_strong or (sub_weak >= 3 and not has_exclude):
            return "subscription_alert"
        
        # Promotional detection (after other categories)
        if promo_score >= 2:
            return "promotional"
        
        return "general"
    
    def _fetch_email_ids(self, folder="INBOX", limit=50, unread_only=False, subject_search=None):
        """
        Fetch email IDs from IMAP with optional subject search.
        Returns a list of email ID bytes.
        """
        try:
            self.mail.select(folder)
            
            if subject_search:
                # Targeted IMAP search by subject keyword
                search_criteria = f'(SUBJECT "{subject_search}")'
            elif unread_only:
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
            return email_ids
        except Exception as e:
            print(f"Error fetching email IDs: {e}")
            return []
    
    def _parse_single_email(self, eid):
        """Parse a single email by its IMAP ID. Returns dict or None."""
        try:
            status, msg_data = self.mail.fetch(eid, "(RFC822)")
            if status != "OK":
                return None
            
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
            
            # Extract body (with HTML fallback)
            body = self._extract_body(msg)
            
            # Categorize
            category = self.categorize_email(subject, body, sender)
            
            # Get unsubscribe link for promotional emails
            unsub_link = None
            if category == "promotional":
                unsub_link = self._get_unsubscribe_link(msg, body)
            
            # Extract dates if applicable
            extracted_dates = []
            extracted_times = []
            if category in ["interview", "upcoming_interview", "payment_reminder", "subscription_alert"]:
                extracted_dates, extracted_times = self._extract_dates_from_text(f"{subject} {body}")
            
            return {
                "id": eid.decode() if isinstance(eid, bytes) else str(eid),
                "subject": subject[:200],
                "sender": sender,
                "date": date_formatted,
                "date_obj": date,
                "category": category,
                "body_preview": body[:500],
                "unsubscribe_link": unsub_link,
                "interview_dates": [d.strftime("%B %d, %Y") for d in extracted_dates],
                "interview_times": extracted_times[:3],
                "extracted_dates": [d.strftime("%B %d, %Y") for d in extracted_dates],
                "extracted_times": extracted_times[:3],
            }
        except Exception as e:
            print(f"Error parsing email {eid}: {e}")
            return None
    
    def fetch_emails(self, folder="INBOX", limit=50, unread_only=False):
        """
        Fetch recent emails from specified folder.
        Returns list of email dictionaries with parsed content.
        """
        if not self.connected and not self.connect():
            return None
        
        try:
            email_ids = self._fetch_email_ids(folder, limit, unread_only)
            
            emails = []
            for eid in email_ids:
                parsed = self._parse_single_email(eid)
                if parsed:
                    emails.append(parsed)
            
            return emails
            
        except Exception as e:
            print(f"❌ Error fetching emails: {e}")
            return None
        finally:
            self.disconnect()
    
    def get_all_categorized(self, limit=50):
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
            "payment_reminder": [],
            "subscription_alert": [],
            "general": []
        }
        
        for email_item in emails:
            category = email_item["category"]
            if category in categorized:
                categorized[category].append(email_item)
            else:
                categorized["general"].append(email_item)
        
        # Add summary
        categorized["summary"] = {
            "total": len(emails),
            "promotional": len(categorized["promotional"]),
            "interview": len(categorized["interview"]),
            "upcoming_interview": len(categorized["upcoming_interview"]),
            "payment_reminder": len(categorized["payment_reminder"]),
            "subscription_alert": len(categorized["subscription_alert"]),
            "general": len(categorized["general"])
        }
        
        return categorized
    
    def get_upcoming_interviews(self, limit=50):
        """
        Get emails containing upcoming interview dates.
        Uses both a broad scan AND targeted IMAP search for interview keywords.
        Returns list of interview-related emails with extracted dates.
        """
        if not self.connected and not self.connect():
            return None
        
        try:
            seen_ids = set()
            all_interview_emails = []
            
            # 1. Broad scan of recent emails
            email_ids = self._fetch_email_ids("INBOX", limit)
            for eid in email_ids:
                parsed = self._parse_single_email(eid)
                if parsed and parsed["category"] in ["interview", "upcoming_interview"]:
                    eid_str = parsed["id"]
                    if eid_str not in seen_ids:
                        seen_ids.add(eid_str)
                        all_interview_emails.append(parsed)
            
            # 2. Targeted IMAP subject search for interview keywords
            for search_term in IMAP_INTERVIEW_SEARCH_SUBJECTS:
                try:
                    targeted_ids = self._fetch_email_ids("INBOX", 30, subject_search=search_term)
                    for eid in targeted_ids:
                        eid_str = eid.decode() if isinstance(eid, bytes) else str(eid)
                        if eid_str not in seen_ids:
                            parsed = self._parse_single_email(eid)
                            if parsed and parsed["category"] in ["interview", "upcoming_interview"]:
                                seen_ids.add(eid_str)
                                all_interview_emails.append(parsed)
                except:
                    continue
            
            # Separate into with-dates and without-dates
            upcoming = [e for e in all_interview_emails if e.get("interview_dates")]
            recent = [e for e in all_interview_emails if not e.get("interview_dates")]
            
            return {
                "with_dates": upcoming,
                "recent_interviews": recent[:5]
            }
            
        except Exception as e:
            print(f"❌ Error fetching interviews: {e}")
            return None
        finally:
            self.disconnect()
    
    def get_promotional_emails(self, limit=30):
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
    
    def get_payment_reminders(self, limit=50):
        """
        Get emails related to upcoming payments, bills, and EMIs.
        Returns list of payment reminder emails with extracted due dates.
        """
        if not self.connected and not self.connect():
            return None
        
        try:
            seen_ids = set()
            payment_emails = []
            
            # 1. Broad scan
            email_ids = self._fetch_email_ids("INBOX", limit)
            for eid in email_ids:
                parsed = self._parse_single_email(eid)
                if parsed and parsed["category"] == "payment_reminder":
                    eid_str = parsed["id"]
                    if eid_str not in seen_ids:
                        seen_ids.add(eid_str)
                        payment_emails.append(parsed)
            
            # 2. Targeted IMAP search
            for term in ["payment", "invoice", "bill due", "emi", "overdue"]:
                try:
                    targeted_ids = self._fetch_email_ids("INBOX", 20, subject_search=term)
                    for eid in targeted_ids:
                        eid_str = eid.decode() if isinstance(eid, bytes) else str(eid)
                        if eid_str not in seen_ids:
                            parsed = self._parse_single_email(eid)
                            if parsed and parsed["category"] == "payment_reminder":
                                seen_ids.add(eid_str)
                                payment_emails.append(parsed)
                except:
                    continue
            
            # Extract amounts from body
            for em in payment_emails:
                body = em.get("body_preview", "")
                # Try to find monetary amounts
                amounts = re.findall(r'(?:₹|rs\.?|inr|usd|\$)\s*[\d,]+(?:\.\d{2})?', body, re.IGNORECASE)
                if not amounts:
                    amounts = re.findall(r'[\d,]+(?:\.\d{2})?\s*(?:₹|rs|inr|usd|\$)', body, re.IGNORECASE)
                em["amounts"] = amounts[:3] if amounts else []
            
            return {
                "payment_emails": payment_emails,
                "total": len(payment_emails)
            }
            
        except Exception as e:
            print(f"❌ Error fetching payment reminders: {e}")
            return None
        finally:
            self.disconnect()
    
    def get_subscription_alerts(self, limit=50):
        """
        Get emails related to subscription renewals, cancellations, and expiry.
        Returns list of subscription alert emails.
        """
        if not self.connected and not self.connect():
            return None
        
        try:
            seen_ids = set()
            sub_emails = []
            
            # 1. Broad scan
            email_ids = self._fetch_email_ids("INBOX", limit)
            for eid in email_ids:
                parsed = self._parse_single_email(eid)
                if parsed and parsed["category"] == "subscription_alert":
                    eid_str = parsed["id"]
                    if eid_str not in seen_ids:
                        seen_ids.add(eid_str)
                        sub_emails.append(parsed)
            
            # 2. Targeted IMAP search
            for term in ["subscription", "renewal", "trial ending", "expiring", "auto-renewal"]:
                try:
                    targeted_ids = self._fetch_email_ids("INBOX", 20, subject_search=term)
                    for eid in targeted_ids:
                        eid_str = eid.decode() if isinstance(eid, bytes) else str(eid)
                        if eid_str not in seen_ids:
                            parsed = self._parse_single_email(eid)
                            if parsed and parsed["category"] == "subscription_alert":
                                seen_ids.add(eid_str)
                                sub_emails.append(parsed)
                except:
                    continue
            
            return {
                "subscription_emails": sub_emails,
                "total": len(sub_emails)
            }
            
        except Exception as e:
            print(f"❌ Error fetching subscription alerts: {e}")
            return None
        finally:
            self.disconnect()


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
