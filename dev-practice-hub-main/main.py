"""
AI Job Tracker — main entry point.

This replaces the old `job_agent.py` (monolithic, Google-Sheets-only)
and `job_tracker.py` (SQLite-only, but broken) with a single working
pipeline:

    Gmail -> filter for job emails -> classify with LLM
          -> save to SQLite -> index in RAG vector store

Google Sheets is now a separate, optional export step — see
sheets_sync.py — so this script has one job and does it fully.

Run:
    python main.py
"""

from agents.email_agent import EmailAgent
from database.models import create_tables
from database.services import DatabaseService
from gmail.gmail_service import GmailService
from rag_memory import RAGMemory


def main():
    print("=" * 60)
    print("AI Job Tracker Started")
    print("=" * 60)

    create_tables()

    gmail = GmailService()
    db = DatabaseService()
    rag = RAGMemory()

    agent = EmailAgent(gmail_service=gmail, database_service=db)

    processed = agent.process_new_emails(max_results=100)

    for record in processed:
        rag.store_job(record)
        print(f"Saved: {record['company']} | {record['role']} | {record['status']}")

    print()
    print(f"Processed {len(processed)} new job emails.")
    print("Finished.")


if __name__ == "__main__":
    main()
