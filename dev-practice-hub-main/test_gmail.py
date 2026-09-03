"""
Previously this ran a real interactive OAuth flow against the leaked
credentials.json file — impossible to run in CI, and it leaned on a
secret that should never have been committed. This tests parse_message
directly against a fake Gmail API payload instead.
"""

from gmail.gmail_service import GmailService


def test_parse_message_extracts_fields():
    # Skip __init__ (which would try to authenticate) and test the
    # pure parsing logic directly.
    service = GmailService.__new__(GmailService)

    message = {
        "id": "msg-123",
        "payload": {
            "headers": [
                {"name": "Subject", "value": "Interview Invitation"},
                {"name": "From", "value": "hr@company.com"},
                {"name": "Date", "value": "Mon, 1 Sep 2026 10:00:00 +0000"},
            ],
            "body": {},
        },
    }

    parsed = service.parse_message(message)

    assert parsed["gmail_id"] == "msg-123"
    assert parsed["subject"] == "Interview Invitation"
    assert parsed["sender"] == "hr@company.com"


if __name__ == "__main__":
    test_parse_message_extracts_fields()
    print("PASS: test_gmail")
