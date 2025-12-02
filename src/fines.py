import mysql.connector
from datetime import date


def update_fines():
    db = mysql.connector.connect(
        user='root',
        password='password',
        host='127.0.0.1',
        database='Library'
    )
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT loan_id, due_date, date_in
        FROM book_loans
        WHERE (date_in > due_date)
           OR (date_in IS NULL AND due_date < CURDATE())
    """)
    loans = cursor.fetchall()

    for loan in loans:
        loan_id = loan['loan_id']
        due = loan['due_date']
        date_in = loan['date_in']

        if date_in is None:
            end_date = date.today()
        else:
            end_date = date_in

        late_days = (end_date - due).days
        fine_amt = round(max(0, late_days) * 0.25, 2)

        cursor.execute("SELECT fine_amt, paid FROM fines WHERE loan_id = %s", (loan_id,))
        existing = cursor.fetchone()

        if existing:
            if existing['paid'] == 1:
                continue
            if float(existing['fine_amt']) != fine_amt:
                cursor.execute("UPDATE fines SET fine_amt = %s WHERE loan_id = %s",
                               (fine_amt, loan_id))
        else:
            cursor.execute("INSERT INTO fines (loan_id, fine_amt, paid) VALUES (%s, %s, 0)",
                           (loan_id, fine_amt))

    db.commit()
    cursor.close()
    db.close()


def list_fines(show_paid=False):
    db = mysql.connector.connect(
        user='root',
        password='password',
        host='127.0.0.1',
        database='Library'
    )
    cursor = db.cursor(dictionary=True)

    query = """
        SELECT br.card_id, br.name AS borrower_name,
            SUM(f.fine_amt) AS total_fines
        FROM borrowers br
        JOIN book_loans bl ON br.card_id = bl.card_id
        JOIN fines f ON bl.loan_id = f.loan_id
        WHERE (%s = TRUE OR f.paid = 0)
        GROUP BY br.card_id
        HAVING total_fines > 0
        ORDER BY br.card_id
    """

    cursor.execute(query, (show_paid,))
    rows = cursor.fetchall()

    print("CARD_ID     BORROWER NAME                        TOTAL FINES")
    print("--------------------------------------------------------------")

    for row in rows:
        print("{: <10} {: <35} ${: >7}".format(
            row['card_id'], row['borrower_name'], row['total_fines']
        ))

    cursor.close()
    db.close()


def pay_fines(card_id):
    db = mysql.connector.connect(
        user='root',
        password='password',
        host='127.0.0.1',
        database='Library'
    )
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT loan_id
        FROM book_loans
        WHERE card_id = %s AND date_in IS NULL
    """, (card_id,))
    still_out = cursor.fetchall()

    if still_out:
        print("Cannot pay fines — borrower still has books checked out.")
        cursor.close()
        db.close()
        return

    cursor.execute("""
        UPDATE fines f
        JOIN book_loans bl ON f.loan_id = bl.loan_id
        SET f.paid = 1
        WHERE bl.card_id = %s AND f.paid = 0
    """, (card_id,))

    db.commit()

    print("All fines successfully paid for card_id:", card_id)

    cursor.close()
    db.close()


if __name__ == "__main__":
    print("1. Update fines")
    print("2. Show unpaid fines")
    print("3. Show all fines (including paid)")
    print("4. Pay fines for borrower")
    choice = input("Enter option: ")

    if choice == "1":
        update_fines()
        print("Fines updated.")

    elif choice == "2":
        list_fines(show_paid=False)

    elif choice == "3":
        list_fines(show_paid=True)

    elif choice == "4":
        card_id = input("Enter card_id: ")
        pay_fines(card_id)

    else:
        print("Invalid choice.")
