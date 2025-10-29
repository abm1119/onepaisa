from onepaisa.db import get_conn
from onepaisa.models import (
    add_contact,
    create_loan,
    repay_contact_oldest_first,
    compute_contact_summary,
)


def test_lend_and_repay():
    conn = get_conn()
    add_contact(conn, "Ali", "friend", [], "")
    create_loan(conn, "Ali", "Wallet", 5000, "you_lent", "2025-10-01")
    res = repay_contact_oldest_first(conn, "Ali", 2000, "2025-10-02")
    summary = compute_contact_summary(conn, "Ali")
    assert summary["lent_open"] == 3000
    assert res["applied"] == 2000