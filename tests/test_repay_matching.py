from onepaisa.db import get_conn
from onepaisa.models import add_contact, create_loan, repay_contact_oldest_first


def test_repay_matches_oldest():
    conn = get_conn()
    add_contact(conn, "Bilal", "friend", [], "")
    # two loans
    create_loan(conn, 'Bilal', 'Wallet', 1000, 'you_lent', '2025-01-01')
    create_loan(conn, 'Bilal', 'Wallet', 2000, 'you_lent', '2025-02-01')
    res = repay_contact_oldest_first(conn, "Bilal", 1500, "2025-03-01")
    # oldest loan should be partially/fully repaid: 1000 applied then 500 applied to next
    assert res["applied"] == 1500
    # check outstanding for first loan is 0
    cur = conn.cursor()
    cur.execute("SELECT repaid_amount, status FROM loans WHERE id=1")
    r1 = cur.fetchone()
    assert r1["status"] == "closed"