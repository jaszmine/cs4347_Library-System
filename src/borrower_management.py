#!/usr/bin/env python3
import mysql.connector
from mysql.connector import errorcode


def db():
    return mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="password",
        database="Library"
    )


def parse_ssn(raw):
    digits = "".join(ch for ch in raw if ch.isdigit())
    if len(digits) != 9:
        raise ValueError("SSN must be 9 digits.")
    return int(digits)


def get_next_card_id(cur):
    cur.execute("SELECT MAX(card_id) FROM borrowers")
    row = cur.fetchone()
    return 1 if row[0] is None else int(row[0]) + 1


def add_borrower(name, ssn, address, phone=None):
    if not name or not ssn or not address:
        raise ValueError("Name, SSN, and address are required.")

    ssn_val = parse_ssn(ssn)

    if phone:
        digits = "".join(ch for ch in phone if ch.isdigit())
        phone = digits[:10] if digits else None

    conn = db()
    try:
        cur = conn.cursor()

        card_id = get_next_card_id(cur)

        cur.execute(
            "INSERT INTO borrowers (ssn, name, card_id, address, phone) "
            "VALUES (%s, %s, %s, %s, %s)",
            (ssn_val, name, card_id, address, phone)
        )
        conn.commit()
        return card_id

    except mysql.connector.IntegrityError as e:
        if e.errno == errorcode.ER_DUP_ENTRY:
            raise RuntimeError("That SSN already has a card.") from e
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    print("Add borrower")
    n = input("Name: ").strip()
    s = input("SSN (any format): ").strip()
    a = input("Address: ").strip()
    p = input("Phone (optional): ").strip() or None

    try:
        cid = add_borrower(n, s, a, p)
        print(f"Created borrower with card_id {cid}")
    except Exception as e:
        print("Error:", e)
