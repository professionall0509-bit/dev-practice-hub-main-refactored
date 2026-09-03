import config
from agents.classifier_agent import ClassifierAgent

JOB_KEYWORDS = [
    "application",
    "applied",
    "thank you for applying",
    "job application",
    "career",
    "recruiter",
    "recruitment",
    "interview",
    "offer",
    "position",
    "candidate",
    "hiring",
    "resume",
    "cv",
]


class EmailAgent:
    """Fetches emails, filters for job-related ones, classifies them,
    and saves new records to the database.

    The original version of this file had broken indentation (a
    syntax error — the file couldn't even be imported) and referenced
    an undefined global `database`. Both are fixed here: gmail,
    database, and classifier are all passed in explicitly.
    """

    def __init__(self, gmail_service, database_service, classifier=None):
        self.gmail = gmail_service
        self.db = database_service
        self.classifier = classifier or ClassifierAgent()

    def fetch_emails(self, max_results=50):
        messages = self.gmail.get_latest_messages(max_results=max_results)

        emails = []
        for msg in messages:
            full = self.gmail.get_message_details(msg["id"])
            parsed = self.gmail.parse_message(full)
            emails.append(parsed)

        return emails

    def is_job_related(self, email):
        sender = (email.get("sender") or "").lower()

        if any(domain in sender for domain in config.IGNORE_SENDERS):
            return False

        text = f"{email.get('subject', '')} {email.get('body', '')}".lower()

        if any(phrase in text for phrase in config.IGNORE_SUBJECTS):
            return False

        return any(keyword in text for keyword in JOB_KEYWORDS)

    def process_new_emails(self, max_results=50):
        """Fetch, filter, classify, and persist new job-related emails.

        Returns the list of records that were newly saved (already-seen
        gmail_ids are skipped, so re-running is always safe).
        """
        emails = self.fetch_emails(max_results=max_results)
        processed = []

        for email in emails:
            if not self.is_job_related(email):
                continue

            if self.db.exists_by_gmail_id(email["gmail_id"]):
                continue

            classification = self.classifier.classify(email)

            record = {
                "gmail_id": email["gmail_id"],
                "company": classification.get("company", "Unknown"),
                "role": classification.get("role", "Unknown"),
                "status": classification.get("status", "Unknown"),
                "confidence": classification.get("confidence", 0),
                "next_action": classification.get("next_action", ""),
                "sender": email["sender"],
                "subject": email["subject"],
                "body": email["body"],
                "received_date": email["date"],
            }

            self.db.save(record)
            processed.append(record)

        return processed
