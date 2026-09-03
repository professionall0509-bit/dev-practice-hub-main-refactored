import os
import tempfile

import config
from database.models import create_tables, get_all_applications, save_application


def test_read_all_applications():
    with tempfile.TemporaryDirectory() as tmp_dir:
        original_path = config.DATABASE_PATH
        config.DATABASE_PATH = os.path.join(tmp_dir, "test.db")

        try:
            create_tables()
            save_application({
                "gmail_id": "read-001",
                "company": "Zoho",
                "role": "Backend Engineer",
                "status": "Applied",
                "sender": "jobs@zoho.com",
                "subject": "Thanks for applying",
                "body": "",
                "received_date": "2026-08-02",
                "confidence": 70,
                "next_action": "",
            })

            applications = get_all_applications()

            assert len(applications) == 1
            assert applications[0]["company"] == "Zoho"
            assert applications[0]["next_action"] == ""
        finally:
            config.DATABASE_PATH = original_path


if __name__ == "__main__":
    test_read_all_applications()
    print("PASS: test_read_database")
