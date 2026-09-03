import sqlite3

import config


def get_connection():
    """Open a connection to the database configured in config.DATABASE_PATH.

    Reads config.DATABASE_PATH at call time (not import time) so tests
    can point it at a temporary file via monkeypatch.
    """
    conn = sqlite3.connect(config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn
