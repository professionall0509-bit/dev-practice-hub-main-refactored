"""
AI JOB TRACKER CONFIG

All values that used to be hardcoded (API keys, sheet IDs, email
addresses) are now read from environment variables / a local .env
file. Copy .env.example to .env and fill in your own values —
.env is gitignored and should never be committed.
"""

import os

from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------
# Google Sheets (optional export target — see sheets_sync.py)
# ---------------------------------------------------------------
SHEET_ID = os.getenv("SHEET_ID", "")
SHEET_NAME = os.getenv("SHEET_NAME", "Jobs")

# ---------------------------------------------------------------
# Gmail
# ---------------------------------------------------------------
# Display label only — actual auth comes from the OAuth files below.
GMAIL_ACCOUNT_LABEL = os.getenv("GMAIL_ACCOUNT_LABEL", "")

GMAIL_CREDENTIALS_FILE = os.getenv("GMAIL_CREDENTIALS_FILE", "credentials.json")
GMAIL_TOKEN_FILE = os.getenv("GMAIL_TOKEN_FILE", "token.json")
GOOGLE_SERVICE_ACCOUNT_FILE = os.getenv(
    "GOOGLE_SERVICE_ACCOUNT_FILE", "service_account.json"
)

# ---------------------------------------------------------------
# Storage
# ---------------------------------------------------------------
DATABASE_PATH = os.getenv("DATABASE_PATH", "job_tracker.db")

# ---------------------------------------------------------------
# Scheduling
# ---------------------------------------------------------------
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL_MINUTES", "15"))

# ---------------------------------------------------------------
# Status keywords used as a fallback / hint alongside LLM classification
# ---------------------------------------------------------------
STATUS_KEYWORDS = {
    "applied": "Applied",
    "application received": "Applied",
    "under review": "Under Review",
    "shortlisted": "Shortlisted",
    "interview": "Interview",
    "assessment": "Assessment",
    "coding test": "Assessment",
    "online test": "Assessment",
    "offer": "Offer",
    "selected": "Offer",
    "rejected": "Rejected",
    "unfortunately": "Rejected",
    "profile viewed": "Profile Viewed",
    "resume viewed": "Resume Viewed",
    "contact details viewed": "Contact Viewed",
    "recruiter viewed": "Profile Viewed",
}

# Subjects/phrases we don't want to treat as job applications
IGNORE_SUBJECTS = [
    "security alert",
    "beware of fake",
    "newsletter",
    "jobs you might have missed",
    "recommended jobs",
    "weekly jobs",
    "daily jobs",
    "salary trends",
    "shared with you",
    "google account",
    "privacy",
]

# Sender domains to ignore completely
IGNORE_SENDERS = [
    "google.com",
    "youtube.com",
    "facebook.com",
    "instagram.com",
]
