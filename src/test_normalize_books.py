import csv, os

def test_normalize_books(books, authors, bookauthors):

    existingIsbns = []
    existingAuthorIDs = []

    with open(books, mode='r', newline='', encoding='utf-8') as f:

        reader = csv.DictReader(f)
        curRow = 1

        for row in reader:
            isbn = row['Isbn']
            if len(isbn) > 10:
                print(f"Row {curRow} in books has an invalid ISBN length!")

            existingIsbns.append(isbn)
            curRow += 1

    with open(authors, mode='r', newline='', encoding='utf-8') as f:

        reader = csv.DictReader(f)
        curRow = 1

        for row in reader:
            a_id = row['Author_id']
            if int(a_id) != curRow:
                print(f"Row {curRow} in authors has an invalid Author ID!")

            existingAuthorIDs.append(a_id)
            curRow += 1

    with open(bookauthors, mode='r', newline='', encoding='utf-8') as f:

        reader = csv.DictReader(f)
        curRow = 1

        for row in reader:
            a_id = row['Author_id']
            isbn = row['Isbn']

            if a_id not in existingAuthorIDs:
                print(f"Row {curRow} in book_authors has an unknown author id!")

            if isbn not in existingIsbns:
                print(f"Row {curRow} in book_authors has an unknown ISBN value!")

            curRow += 1

if __name__ == "__main__":
    # Define file paths
    books = '../normalized_data/normalized_book.csv'
    authors = '../normalized_data/normalized_authors.csv'
    book_authors = '../normalized_data/normalized_book_authors.csv'

    # Normalize the books data
    test_normalize_books(books, authors, book_authors)
    print("All files validated")