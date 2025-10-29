"""
Database helper for onepaisa.
DB path defaults to ~/.onepaisa/onepaisa_db.sqlite but can be overridden with env var ONEPAISA_DB_PATH.
"""

from pathlib import Path
import sqlite3
import os

SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS accounts (
  id INTEGER PRIMARY KEY, name TEXT UNIQUE, type TEXT, currency TEXT, created_at TEXT
);
CREATE TABLE IF NOT EXISTS contacts (
  id INTEGER PRIMARY KEY, name TEXT, relation TEXT, tags TEXT, note TEXT, created_at TEXT
);
CREATE TABLE IF NOT EXISTS transactions (
  id INTEGER PRIMARY KEY, account_id INTEGER, date TEXT, amount REAL, category TEXT, merchant TEXT, note TEXT,
  tags TEXT, FOREIGN KEY(account_id) REFERENCES accounts(id)
);
CREATE TABLE IF NOT EXISTS loans (
  id INTEGER PRIMARY KEY, contact_id INTEGER, txn_id INTEGER, role TEXT, amount REAL, date TEXT, due_date TEXT,
  repaid_amount REAL DEFAULT 0, status TEXT DEFAULT 'open', note TEXT,
  FOREIGN KEY(contact_id) REFERENCES contacts(id), FOREIGN KEY(txn_id) REFERENCES transactions(id)
);
CREATE TABLE IF NOT EXISTS loan_payments (
  id INTEGER PRIMARY KEY, loan_id INTEGER, date TEXT, amount REAL, note TEXT,
  FOREIGN KEY(loan_id) REFERENCES loans(id)
);
"""


def get_db_path():
    env = os.environ.get("ONEPAISA_DB_PATH")
    if env:
        return Path(env).expanduser()
    base = Path.home() / ".onepaisa"
    base.mkdir(parents=True, exist_ok=True)
    return base / "onepaisa_db.sqlite"


def get_conn():
    db_path = get_db_path()
    first = not db_path.exists()
    conn = sqlite3.connect(str(db_path), detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    if first:
        conn.executescript(SCHEMA)
        conn.commit()
    return conn
