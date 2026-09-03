"""
Optional: export the SQLite job-tracker database to a Google Sheet.

This is the README's "Google Sheets sync" feature, but now decoupled
from the main pipeline instead of being a second, conflicting storage
system. SQLite (via main.py) is the source of truth; this script just
mirrors it into a sheet for easy viewing/sharing.

Requires:
  - SHEET_ID set in .env
  - A Google service-account JSON file, with edit access to that
    sheet, at the path in GOOGLE_SERVICE_ACCOUNT_FILE (.env)

Run:
    python sheets_sync.py
"""

import gspread
from google.oauth2.service_account import Credentials as ServiceCredentials

import config
from database.services import DatabaseService

SHEET_HEADERS = [
    "Company", "Role", "Status", "Confidence", "Next Action",
    "Received Date", "Subject", "Sender", "Gmail ID",
]


def get_worksheet():
    creds = ServiceCredentials.from_service_account_file(
        config.GOOGLE_SERVICE_ACCOUNT_FILE,
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ],
    )
    client = gspread.authorize(creds)
    spreadsheet = client.open_by_key(config.SHEET_ID)

    try:
        return spreadsheet.worksheet(config.SHEET_NAME)
    except gspread.WorksheetNotFound:
        ws = spreadsheet.add_worksheet(title=config.SHEET_NAME, rows=2000, cols=15)
        ws.append_row(SHEET_HEADERS)
        return ws


def sync():
    if not config.SHEET_ID:
        print("SHEET_ID not set in .env — skipping Sheets sync.")
        return

    db = DatabaseService()
    ws = get_worksheet()

    existing_ids = {row.get("Gmail ID") for row in ws.get_all_records()}
    applications = db.get_all()
    synced = 0

    for app in applications:
        if app["gmail_id"] in existing_ids:
            continue

        ws.append_row([
            app["company"], app["role"], app["status"],
            app["confidence"], app["next_action"], app["received_date"],
            app["subject"], app["sender"], app["gmail_id"],
        ])
        synced += 1

    print(f"Synced {synced} new row(s) to Google Sheets.")


if __name__ == "__main__":
    sync()
