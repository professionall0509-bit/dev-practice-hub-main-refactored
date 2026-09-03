from database.db import get_connection


def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            gmail_id TEXT UNIQUE,
            company TEXT,
            role TEXT,
            status TEXT,
            sender TEXT,
            subject TEXT,
            body TEXT,
            received_date TEXT,
            confidence INTEGER,
            next_action TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def save_application(data):
    """Insert a new application row.

    Uses INSERT OR IGNORE on the UNIQUE gmail_id column, so re-saving
    the same email is a safe no-op instead of a duplicate row.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO applications(
            gmail_id, company, role, status, sender, subject,
            body, received_date, confidence, next_action
        )
        VALUES (?,?,?,?,?,?,?,?,?,?)
    """, (
        data.get("gmail_id"),
        data.get("company"),
        data.get("role"),
        data.get("status"),
        data.get("sender"),
        data.get("subject"),
        data.get("body"),
        data.get("received_date"),
        data.get("confidence"),
        data.get("next_action"),
    ))

    conn.commit()
    conn.close()


def get_all_applications():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM applications ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_by_status(status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM applications WHERE status=?", (status,))
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_total_count():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM applications")
    count = cursor.fetchone()[0]
    conn.close()
    return count


def application_exists(sender, subject):
    """Kept for backwards compatibility. Prefer application_exists_by_gmail_id."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COUNT(*) FROM applications WHERE sender=? AND subject=?",
        (sender, subject),
    )
    count = cursor.fetchone()[0]
    conn.close()
    return count > 0


def application_exists_by_gmail_id(gmail_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COUNT(*) FROM applications WHERE gmail_id=?", (gmail_id,)
    )
    count = cursor.fetchone()[0]
    conn.close()
    return count > 0
