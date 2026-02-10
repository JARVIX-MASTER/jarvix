"""
Test script for Gmail automation features.
Tests categorization, date parsing, and keyword matching WITHOUT requiring a Gmail connection.
Run: python test_gmail_features.py
"""

import sys
import os

# Add src to path so we can import gmail module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from jarvix.features.gmail import GmailClient

client = GmailClient()

passed = 0
failed = 0

def test(name, got, expected):
    global passed, failed
    if got == expected:
        print(f"  ✅ {name}")
        passed += 1
    else:
        print(f"  ❌ {name}")
        print(f"       Expected: {expected}")
        print(f"       Got:      {got}")
        failed += 1


# ───────── 1. Interview Detection ─────────
print("\n═══ Interview Detection ═══")

test("Strong keyword in subject",
     client.categorize_email("Interview Scheduled for SDE Role", "", "hr@company.com"),
     "interview")

test("Strong keyword in subject with date in body",
     client.categorize_email("Interview Scheduled for SDE Role",
                             "Your interview is on 15th March 2026 at 2:00 PM", "hr@company.com"),
     "upcoming_interview")

test("Technical interview in subject",
     client.categorize_email("Technical Interview Invitation",
                             "Please join us on Feb 20, 2026", "recruiter@tech.com"),
     "upcoming_interview")

test("Assessment scheduled (new keyword)",
     client.categorize_email("Assessment Scheduled - Online Coding Test",
                             "Complete your test by March 1, 2026", "hiring@startup.io"),
     "upcoming_interview")

test("Weak keywords (2 = match after fix)",
     client.categorize_email("Application Update",
                             "The recruiter wants to schedule an interview", "talent@co.com"),
     "interview")

test("Single weak keyword (not enough)",
     client.categorize_email("Application Update",
                             "Thank you for your interest in this position", "noreply@jobs.com"),
     "general")

test("Exclude keywords prevent false positive",
     client.categorize_email("New Jobs Matching Your Profile",
                             "interview tips and recruiter advice, apply now, easy apply", "noreply@linkedin.com"),
     "general")

test("Coding test in body (new strong keyword)",
     client.categorize_email("Action Required",
                             "Your coding test scheduled for March 5, 2026", "hr@company.com"),
     "upcoming_interview")


# ───────── 2. Date Parsing ─────────
print("\n═══ Date Parsing ═══")

dates, times = client._extract_dates_from_text("Your interview is on 15th March 2026 at 2:00 PM")
test("Ordinal date '15th March 2026'", len(dates) > 0, True)
test("Time extracted '2:00 PM'", any("2:00" in t for t in times), True)

dates2, _ = client._extract_dates_from_text("Please join us on Feb 20, 2026")
test("Month-Day-Year 'Feb 20, 2026'", len(dates2) > 0, True)

dates3, _ = client._extract_dates_from_text("Scheduled for 2026-03-12")
test("ISO format '2026-03-12'", len(dates3) > 0, True)

dates4, _ = client._extract_dates_from_text("Your test is on 12/03/2026")
test("DD/MM/YYYY '12/03/2026'", len(dates4) > 0, True)

dates5, _ = client._extract_dates_from_text("Meeting on February 28, 2026")
test("Full month 'February 28, 2026'", len(dates5) > 0, True)


# ───────── 3. Payment Reminder Detection ─────────
print("\n═══ Payment Reminder Detection ═══")

test("Payment due email",
     client.categorize_email("Payment Reminder: Bill Due",
                             "Your electricity bill of ₹2500 is due on March 5, 2026", "billing@utility.com"),
     "payment_reminder")

test("EMI due email",
     client.categorize_email("EMI Payment Due",
                             "Your loan EMI of Rs 15,000 is due on Feb 28", "alerts@bank.com"),
     "payment_reminder")

test("Credit card bill",
     client.categorize_email("Credit Card Bill Statement",
                             "Your credit card payment of $500 is due by March 10, 2026", "cards@bank.com"),
     "payment_reminder")

test("Invoice email",
     client.categorize_email("Invoice #12345",
                             "Amount due: ₹3,200. Payment reminder for your invoice.", "billing@saas.com"),
     "payment_reminder")


# ───────── 4. Subscription Alert Detection ─────────
print("\n═══ Subscription Alert Detection ═══")

test("Subscription ending",
     client.categorize_email("Your subscription is ending soon",
                             "Your premium plan expires on March 15, 2026", "noreply@streaming.com"),
     "subscription_alert")

test("Auto-renewal notice",
     client.categorize_email("Auto-Renewal Notice",
                             "Your subscription will be renewed on Feb 25, 2026. You will be charged $9.99", "billing@app.com"),
     "subscription_alert")

test("Trial ending",
     client.categorize_email("Your free trial is ending",
                             "Trial ending in 3 days. Cancel before March 1 to avoid charges", "noreply@saas.com"),
     "subscription_alert")

test("Membership renewal",
     client.categorize_email("Membership Renewal Reminder",
                             "Your annual membership is up for renewal on April 1, 2026", "support@club.com"),
     "subscription_alert")


# ───────── 5. Promotional Detection (unchanged) ─────────
print("\n═══ Promotional Detection ═══")

test("Promotional email with unsubscribe",
     client.categorize_email("50% OFF Sale - Limited Time!",
                             "Special offer just for you! Unsubscribe here.", "marketing@shop.com"),
     "promotional")

test("Newsletter",
     client.categorize_email("Weekly Newsletter",
                             "This week's digest. Unsubscribe from newsletter.", "news@blog.com"),
     "promotional")


# ───────── Summary ─────────
print(f"\n{'═'*40}")
print(f"Results: {passed} passed, {failed} failed, {passed+failed} total")
if failed == 0:
    print("🎉 All tests passed!")
else:
    print(f"⚠️  {failed} test(s) failed")
print(f"{'═'*40}")
