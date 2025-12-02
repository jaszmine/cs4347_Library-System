def checkout_sql(isbn, card_no):
    return f"""
-- 1) Ensure borrower exists
SELECT * 
FROM BORROWER 
WHERE Card_no = '{card_no}';

-- 2) Ensure book exists
SELECT * 
FROM BOOKS 
WHERE Isbn = '{isbn}';

-- 3) Check unpaid fines
SELECT * 
FROM FINES 
WHERE Card_no = '{card_no}' AND Fine > 0;

-- 4) Check borrower loan count
SELECT COUNT(*) AS ActiveLoans
FROM BOOK_LOANS
WHERE Card_no = '{card_no}' AND Checkin_date IS NULL;

-- 5) Check book availability
SELECT * 
FROM BOOK_LOANS
WHERE Isbn = '{isbn}' AND Checkin_date IS NULL;

-- 6) If all checks pass, insert loan
INSERT INTO BOOK_LOANS (Isbn, Card_no, Checkout_date, Due_date, Checkin_date)
VALUES ('{isbn}', '{card_no}', CURRENT_DATE, DATE_ADD(CURRENT_DATE, INTERVAL 14 DAY), NULL);
"""


def checkin_sql(isbn, card_no):
    return f"""
-- Find active loan
SELECT * 
FROM BOOK_LOANS
WHERE Isbn = '{isbn}' AND Card_no = '{card_no}' AND Checkin_date IS NULL;

-- Mark as returned
UPDATE BOOK_LOANS
SET Checkin_date = CURRENT_DATE
WHERE Isbn = '{isbn}' AND Card_no = '{card_no}' AND Checkin_date IS NULL;
"""


def search_loans_sql(isbn=None, card_no=None, borrower_name=None):
    conditions = []

    if isbn:
        conditions.append(f"BOOK_LOANS.Isbn = '{isbn}'")
    if card_no:
        conditions.append(f"BOOK_LOANS.Card_no = '{card_no}'")
    if borrower_name:
        conditions.append(f"BORROWER.Name LIKE '%{borrower_name}%'")

    where_clause = " AND ".join(conditions)
    if not where_clause:
        where_clause = "1=1"

    return f"""
SELECT BOOK_LOANS.Isbn, BOOK_LOANS.Card_no, BOOK_LOANS.Checkout_date, BOOK_LOANS.Due_date
FROM BOOK_LOANS
JOIN BORROWER ON BOOK_LOANS.Card_no = BORROWER.Card_no
WHERE {where_clause};
"""


if __name__ == "__main__":
    print("1 = Checkout (SQL)")
    print("2 = Checkin (SQL)")
    print("3 = Search Loans (SQL)")

    ch = input("Choice: ")

    if ch == "1":
        isbn = input("ISBN: ")
        card = input("Borrower ID: ")
        print(checkout_sql(isbn, card))

    elif ch == "2":
        isbn = input("ISBN: ")
        card = input("Borrower ID: ")
        print(checkin_sql(isbn, card))

    elif ch == "3":
        name = input("Borrower name substring: ")
        print(search_loans_sql(borrower_name=name))

