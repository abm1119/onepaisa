from onepaisa.db import get_conn
from onepaisa.models import add_contact, create_loan, ask_agent


def test_ask_gave_borrowed():
    conn = get_conn()
    add_contact(conn, "Sara", "friend", [], "")
    create_loan(conn, "Sara", "Wallet", 3000, "you_lent", "2025-10-01")
    r = ask_agent(conn, "how much I gave others this month")
    assert "explanation" in r
    assert r["answer"] is not None