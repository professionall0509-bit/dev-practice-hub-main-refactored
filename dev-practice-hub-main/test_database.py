"""
Previously this "test" saved a record and printed "Saved Successfully"
with no assertion at all. This uses a temporary database file so it's
isolated and actually checks the saved data comes back correctly.
"""

import os
import tempfile

import config
from database.models import create_tables, get_all_applications, save_application


def test_save_and_retrieve():
    with tempfile.TemporaryDirectory() as tmp_dir:
        original_path = config.DATABASE_PATH
        config.DATABASE_PATH = os.path.join(tmp_dir, "test.db")

        try:
            create_tables()
            save_application({
                "gmail_id": "test-001",
                "company": "TCS",
                "role": "GenAI Engineer",
                "status": "Interview",
                "sender": "jobs@tcs.com",
                "subject": "Interview Invitation",
                "body": "Congratulations",
                "received_date": "2026-07-31",
                "confidence": 98,
                "next_action": "Schedule Interview",
            })

            rows = get_all_applications()

            assert len(rows) == 1
            assert rows[0]["company"] == "TCS"
            assert rows[0]["status"] == "Interview"
        finally:
            config.DATABASE_PATH = original_path


if __name__ == "__main__":
    test_save_and_retrieve()
    print("PASS: test_database")
