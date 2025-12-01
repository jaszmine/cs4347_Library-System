import csv
from datetime import datetime, timedelta

BOOKS = "../normalized_data/normalized_book.csv"
BORROWERS = "../normalized_data/normalized_borrower.csv"
BOOK_LOANS = "../normalized_data/normalized_book_loans.csv"
FINES = "../normalized_data/normalized_fines.csv"

def read_csv(path):
    with open(path, "r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def write_csv(path, fieldnames, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def find_loans(isbn=None, card_no=None, borrower_name=None):
    borrowers = read_csv(BORROWERS)
    loans = read_csv(BOOK_LOANS)

    results = []

    for loan in loans:
        if loan["Checkin_date"]:  
            continue  

        borrower = next((b for b in borrowers if b["Card_no"] == loan["Card_no"]), None)
        if borrower is None:
            continue

        if isbn and loan["Isbn"] != isbn:
            continue
        if card_no and loan["Card_no"] != card_no:
            continue
        if borrower_name and borrower_name.lower() not in borrower["Name"].lower():
            continue

        results.append(loan)

    return results


def checkout(isbn, card_no):

    books = read_csv(BOOKS)
    borrowers = read_csv(BORROWERS)
    loans = read_csv(BOOK_LOANS)
    fines = read_csv(FINES)

    
    book = next((b for b in books if b["Isbn"] == isbn), None)
    if not book:
        return "Error: Book not found."

    
    borrower = next((b for b in borrowers if b["Card_no"] == card_no), None)
    if not borrower:
        return "Error: Borrower not found."

   
    fine = next((f for f in fines if f["Card_no"] == card_no), None)
    if fine and float(fine["Fine"]) > 0:
        return "Error: Borrower has unpaid fines."

    
    active_loans = [l for l in loans if l["Card_no"] == card_no and not l["Checkin_date"]]
    if len(active_loans) >= 3:
        return "Error: Borrower already has 3 active loans."

  
    if any(l for l in loans if l["Isbn"] == isbn and not l["Checkin_date"]):
        return "Error: Book is currently checked out."

   
    today = datetime.now().date()
    due = today + timedelta(days=14)

    new_entry = {
        "Isbn": isbn,
        "Card_no": card_no,
        "Checkout_date": today.isoformat(),
        "Due_date": due.isoformat(),
        "Checkin_date": ""
    }

    loans.append(new_entry)

    
    write_csv(BOOK_LOANS, loans[0].keys(), loans)

    return f"Success: Book checked out. Due on {due}"


def checkin(isbn, card_no):
    loans = read_csv(BOOK_LOANS)

    updated = False
    for loan in loans:
        if loan["Isbn"] == isbn and loan["Card_no"] == card_no and not loan["Checkin_date"]:
            loan["Checkin_date"] = datetime.now().date().isoformat()
            updated = True
            break

    if not updated:
        return "Error: No active loan found."

    write_csv(BOOK_LOANS, loans[0].keys(), loans)
    return "Success: Book checked in."

if __name__ == "__main__":
    print("1 = Checkout")
    print("2 = Checkin")
    print("3 = Search Loans")

    ch = input("Choice: ")

    if ch == "1":
        isbn = input("ISBN: ")
        card = input("Borrower ID: ")
        print(checkout(isbn, card))

    elif ch == "2":
        isbn = input("ISBN: ")
        card = input("Borrower ID: ")
        print(checkin(isbn, card))

    elif ch == "3":
        name = input("Borrower name substring: ")
        results = find_loans(borrower_name=name)
        for r in results:
            print(r)
