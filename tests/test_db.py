from onepaisa.db import get_conn


def test_db_creation():
    conn = get_conn()
    assert conn is not None
    # check if tables exist
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='loans'")
    assert cur.fetchone() is not None