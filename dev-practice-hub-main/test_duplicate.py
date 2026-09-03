"""
Previously this checked hardcoded sender/subject strings that never
existed in the database and just printed the (always-False) result.
This actually saves a record, confirms it's detected as existing, and
confirms saving it twice doesn't create a duplicate row.
"""

import os
import tempfile

import config
from database.models import (
    application_exists_by_gmail_id,
    create_tables,
    get_all_applications,
    save_application,
)


def test_duplicate_detection():
    with tempfile.TemporaryDirectory() as tmp_dir:
        original_path = config.DATABASE_PATH
        config.DATABASE_PATH = os.path.join(tmp_dir, "test.db")

        try:
            create_tables()

            record = {
                "gmail_id": "dup-test-001",
                "company": "Amazon",
                "role": "SDE",
                "status": "Applied",
                "sender": "hr@amazon.com",
                "subject": "Thanks for applying",
                "body": "",
                "received_date": "2026-08-01",
                "confidence": 80,
                "next_action": "",
            }

            assert application_exists_by_gmail_id("dup-test-001") is False

            save_application(record)
            assert application_exists_by_gmail_id("dup-test-001") is True

            # Saving the same gmail_id again must not create a second row
            save_application(record)
            assert len(get_all_applications()) == 1
        finally:
            config.DATABASE_PATH = original_path


if __name__ == "__main__":
    test_duplicate_detection()
    print("PASS: test_duplicate")
