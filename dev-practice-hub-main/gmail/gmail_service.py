import base64
import os
import pickle

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

import config

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


class GmailService:
    """Handles Gmail OAuth and message retrieval.

    Previously this class required the caller to build and pass in
    `creds`, but job_tracker.py called `GmailService()` with no
    arguments at all — a guaranteed TypeError. Auth is now handled
    internally, matching how the rest of the app constructs it.
    """

    def __init__(self, credentials_file=None, token_file=None):
        self.credentials_file = credentials_file or config.GMAIL_CREDENTIALS_FILE
        self.token_file = token_file or config.GMAIL_TOKEN_FILE
        self.service = build("gmail", "v1", credentials=self._get_credentials())

    def _get_credentials(self):
        creds = None

        if os.path.exists(self.token_file):
            with open(self.token_file, "rb") as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, SCOPES
                )
                creds = flow.run_local_server(port=0)

            with open(self.token_file, "wb") as token:
                pickle.dump(creds, token)

        return creds

    def get_latest_messages(self, max_results=20):
        results = self.service.users().messages().list(
            userId="me", maxResults=max_results
        ).execute()
        return results.get("messages", [])

    def get_message_details(self, message_id):
        return self.service.users().messages().get(
            userId="me", id=message_id, format="full"
        ).execute()

    def parse_message(self, message):
        headers = message.get("payload", {}).get("headers", [])

        subject = ""
        sender = ""
        date = ""

        for header in headers:
            name = header.get("name", "").lower()

            if name == "subject":
                subject = header.get("value", "")
            elif name == "from":
                sender = header.get("value", "")
            elif name == "date":
                date = header.get("value", "")

        body = self._extract_body(message.get("payload", {}))

        return {
            "gmail_id": message.get("id"),
            "subject": subject.strip(),
            "sender": sender.strip(),
            "date": date,
            "body": body,
        }

    def _extract_body(self, payload):
        if "parts" in payload:
            for part in payload["parts"]:
                mime = part.get("mimeType", "")
                data = part.get("body", {}).get("data")

                if mime == "text/plain" and data:
                    return base64.urlsafe_b64decode(data).decode(
                        "utf-8", errors="ignore"
                    )

                if "parts" in part:
                    nested = self._extract_body(part)
                    if nested:
                        return nested
        else:
            data = payload.get("body", {}).get("data")
            if data:
                return base64.urlsafe_b64decode(data).decode(
                    "utf-8", errors="ignore"
                )

        return ""
