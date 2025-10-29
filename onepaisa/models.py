"""
High-level models and business logic for onepaisa CLI.
"""

from datetime import date
import json



def today_iso():
    return date.today().isoformat()


# Accounts


def ensure_account(conn, name: str):
    cur = conn.cursor()
    cur.execute("SELECT id FROM accounts WHERE name=?", (name,))
    r = cur.fetchone()
    if r:
        return r[0]
    cur.execute(
        "INSERT INTO accounts(name,type,currency,created_at) VALUES(?,?,?,?)",
        (name, "checking", "PKR", today_iso()),
    )
    conn.commit()
    return cur.lastrowid


# Contacts


def add_contact(conn, name: str, relation: str = "other", tags=None, note: str = ""):
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO contacts(name,relation,tags,note,created_at) VALUES(?,?,?,?,?)",
        (name, relation, json.dumps(tags or []), note or "", today_iso()),
    )
    conn.commit()
    return cur.lastrowid


def list_contacts(conn):
    cur = conn.cursor()
    return cur.execute("SELECT * FROM contacts ORDER BY name").fetchall()


# Transactions


def add_transaction(
    conn,
    account: str,
    amount: float,
    date_str: str = None,
    category: str = None,
    merchant: str = None,
    note: str = None,
    tags=None,
):
    acc_id = ensure_account(conn, account)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO transactions(account_id,date,amount,category,merchant,note,tags) VALUES(?,?,?,?,?,?,?)",
        (
            acc_id,
            date_str or today_iso(),
            float(amount),
            category or "",
            merchant or "",
            note or "",
            json.dumps(tags or []),
        ),
    )
    conn.commit()
    return cur.lastrowid


# Loans (lend/borrow)


def create_loan(
    conn,
    contact_name: str,
    account: str,
    amount: float,
    role: str,
    date_str: str = None,
    due_date: str = None,
    note: str = None,
):
    cur = conn.cursor()
    cur.execute("SELECT id FROM contacts WHERE name=?", (contact_name,))
    r = cur.fetchone()
    if not r:
        raise ValueError(f"Contact not found: {contact_name}")
    contact_id = r[0]
    # sign: you_lent => money out (negative), you_borrowed => money in (positive)
    signed = -float(amount) if role == "you_lent" else float(amount)
    txn_id = add_transaction(
        conn,
        account,
        signed,
        date_str,
        category=("lend" if role == "you_lent" else "borrow"),
        merchant=contact_name,
        note=note,
        tags=[role],
    )
    cur.execute(
        "INSERT INTO loans(contact_id,txn_id,role,amount,date,due_date,note) VALUES(?,?,?,?,?,?,?)",
        (
            contact_id,
            txn_id,
            role,
            float(amount),
            date_str or today_iso(),
            due_date,
            note or "",
        ),
    )
    conn.commit()
    return cur.lastrowid


def get_open_loans(conn, contact_id: int):
    cur = conn.cursor()
    return cur.execute(
        "SELECT * FROM loans WHERE contact_id=? AND status='open' ORDER BY date ASC",
        (contact_id,),
    ).fetchall()


def apply_repayment_to_loan(
    conn, loan_row, amount: float, date_str: str = None, note: str = None
):
    cur = conn.cursor()
    loan_id = loan_row["id"]
    open_amount = loan_row["amount"] - (loan_row["repaid_amount"] or 0.0)
    apply_amt = min(open_amount, amount)
    cur.execute(
        "INSERT INTO loan_payments(loan_id,date,amount,note) VALUES(?,?,?,?)",
        (loan_id, date_str or today_iso(), apply_amt, note or "repayment"),
    )
    new_repaid = (loan_row["repaid_amount"] or 0.0) + apply_amt
    new_status = "closed" if abs(new_repaid - loan_row["amount"]) < 1e-9 else "open"
    cur.execute(
        "UPDATE loans SET repaid_amount=?, status=? WHERE id=?",
        (new_repaid, new_status, loan_id),
    )
    # add transaction for cash flow: if you_lent then repayment is inflow (+); if you_borrowed repayment is outflow (-)
    sign = 1.0 if loan_row["role"] == "you_lent" else -1.0
    add_transaction(
        conn,
        "Wallet",
        sign * apply_amt,
        date_str,
        category="loan_payment",
        merchant=f"repay:{loan_id}",
        note=f"repayment for loan {loan_id}",
    )
    conn.commit()
    return apply_amt


def repay_contact_oldest_first(
    conn, contact_name: str, amount: float, date_str: str = None, note: str = None
):
    cur = conn.cursor()
    cur.execute("SELECT id FROM contacts WHERE name=?", (contact_name,))
    r = cur.fetchone()
    if not r:
        raise ValueError(f"Contact not found: {contact_name}")
    cid = r[0]
    loans = get_open_loans(conn, cid)
    remaining = float(amount)
    if not loans:
        # no open loans -> treat as simple transaction deposit
        add_transaction(
            conn,
            "Wallet",
            float(amount),
            date_str,
            category="repayment",
            merchant=contact_name,
            note=note,
        )
        return {"unapplied": 0.0, "applied": float(amount)}
    applied_total = 0.0
    for loan in loans:
        if remaining <= 0:
            break
        applied = apply_repayment_to_loan(conn, loan, remaining, date_str, note)
        remaining -= applied
        applied_total += applied
    return {"unapplied": remaining, "applied": applied_total}


# Summaries & reports


def compute_contact_summary(conn, contact_name: str):
    cur = conn.cursor()
    cur.execute(
        "SELECT id,name,relation,tags,note FROM contacts WHERE name=?", (contact_name,)
    )
    c = cur.fetchone()
    if not c:
        raise ValueError("Contact not found")
    cid = c[0]
    lent_total = cur.execute(
        "SELECT IFNULL(SUM(amount),0) FROM loans WHERE contact_id=? AND role='you_lent'",
        (cid,),
    ).fetchone()[0]
    lent_repaid = cur.execute(
        "SELECT IFNULL(SUM(repaid_amount),0) FROM loans WHERE contact_id=? AND role='you_lent'",
        (cid,),
    ).fetchone()[0]
    lent_open = cur.execute(
        "SELECT IFNULL(SUM(amount - IFNULL(repaid_amount,0)),0) FROM loans WHERE contact_id=? AND role='you_lent' AND status='open'",
        (cid,),
    ).fetchone()[0]
    bor_total = cur.execute(
        "SELECT IFNULL(SUM(amount),0) FROM loans WHERE contact_id=? AND role='you_borrowed'",
        (cid,),
    ).fetchone()[0]
    bor_repaid = cur.execute(
        "SELECT IFNULL(SUM(repaid_amount),0) FROM loans WHERE contact_id=? AND role='you_borrowed'",
        (cid,),
    ).fetchone()[0]
    bor_open = cur.execute(
        "SELECT IFNULL(SUM(amount - IFNULL(repaid_amount,0)),0) FROM loans WHERE contact_id=? AND role='you_borrowed' AND status='open'",
        (cid,),
    ).fetchone()[0]
    net = (lent_open or 0.0) - (bor_open or 0.0)
    return {
        "contact": dict(c),
        "lent_total": lent_total or 0.0,
        "lent_repaid": lent_repaid or 0.0,
        "lent_open": lent_open or 0.0,
        "borrowed_total": bor_total or 0.0,
        "borrowed_repaid": bor_repaid or 0.0,
        "borrowed_open": bor_open or 0.0,
        "net": net,
    }


def contacts_report(conn):
    cur = conn.cursor()
    rows = cur.execute("SELECT id,name FROM contacts ORDER BY name").fetchall()
    result = []
    grand_they_owe = 0.0
    grand_you_owe = 0.0
    for r in rows:
        cid = r[0]
        name = r[1]
        lent_open = cur.execute(
            "SELECT IFNULL(SUM(amount - IFNULL(repaid_amount,0)),0) FROM loans WHERE contact_id=? AND role='you_lent' AND status='open'",
            (cid,),
        ).fetchone()[0]
        bor_open = cur.execute(
            "SELECT IFNULL(SUM(amount - IFNULL(repaid_amount,0)),0) FROM loans WHERE contact_id=? AND role='you_borrowed' AND status='open'",
            (cid,),
        ).fetchone()[0]
        grand_they_owe += lent_open or 0.0
        grand_you_owe += bor_open or 0.0
        result.append(
            {
                "name": name,
                "they_owe_you": lent_open or 0.0,
                "you_owe_them": bor_open or 0.0,
                "net": (lent_open or 0.0) - (bor_open or 0.0),
            }
        )
    return {
        "contacts": result,
        "grand_they_owe": grand_they_owe,
        "grand_you_owe": grand_you_owe,
        "net": grand_they_owe - grand_you_owe,
    }


def aging_buckets(conn):
    cur = conn.cursor()
    rows = cur.execute(
        "SELECT * FROM loans WHERE status='open' ORDER BY date"
    ).fetchall()
    buckets = {"0-30": 0.0, "31-90": 0.0, "91-180": 0.0, "180+": 0.0}
    from datetime import date as _d

    today = _d.today()
    for r in rows:
        dt = _d.fromisoformat(r["date"]) if r["date"] else _d.today()
        age = (today - dt).days
        open_amt = r["amount"] - (r["repaid_amount"] or 0.0)
        if age <= 30:
            buckets["0-30"] += open_amt
        elif age <= 90:
            buckets["31-90"] += open_amt
        elif age <= 180:
            buckets["91-180"] += open_amt
        else:
            buckets["180+"] += open_amt
    return buckets


# Ask agent (rule-based)


def ask_agent(conn, query: str):
    q = query.lower()
    if "how much i gave" in q or "how much i give" in q:
        d = _month_start()
        cur = conn.cursor()
        s = cur.execute(
            "SELECT IFNULL(SUM(amount),0) FROM loans WHERE role='you_lent' AND date>=?",
            (d,),
        ).fetchone()[0]
        explanation = f"SUM(loans.role='you_lent' AND date >= '{d}') = {s}"
        return {"answer": float(s), "explanation": explanation}
    if "how much i take" in q or "how much i borrow" in q:
        d = _month_start()
        cur = conn.cursor()
        s = cur.execute(
            "SELECT IFNULL(SUM(amount),0) FROM loans WHERE role='you_borrowed' AND date>=?",
            (d,),
        ).fetchone()[0]
        explanation = f"SUM(loans.role='you_borrowed' AND date >= '{d}') = {s}"
        return {"answer": float(s), "explanation": explanation}
    if "outstanding" in q or "borrow from others" in q:
        rep = contacts_report(conn)
        return {"answer": rep, "explanation": "contacts report"}
    return {
        "answer": None,
        "explanation": "I can answer: 'how much i gave', 'how much i borrowed', 'outstanding'",
    }


def _month_start():
    from datetime import date

    d = date.today()
    return d.replace(day=1).isoformat()
