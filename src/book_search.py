import csv, os, mysql.connector

def book_search(search, books, authors, book_authors):
    matches = []

    with open(books, mode='r', newline='', encoding='utf-8') as f:

        reader = csv.DictReader(f)

        for row in reader:
            title = row['Title']
            isbn = row['Isbn']
            if search.casefold() in title.casefold():
                matches.append([isbn, title, '', '', ''])
            if search.casefold() in isbn.casefold():
                matches.append([isbn, title, '', '', ''])

    with open(authors, mode='r', newline='', encoding='utf-8') as f:

        reader = csv.DictReader(f)

        for row in reader:
            a_id = row['Author_id']
            name = row['Name']
            if search.casefold() in name.casefold():
                matches.append(['', '', a_id, name, ''])
            if search.casefold() in a_id.casefold():
                matches.append(['', '', a_id, name, ''])

    with open(book_authors, mode='r', newline='', encoding='utf-8') as f:

        reader = csv.DictReader(f)

        for row in reader:
            a_id = row['Author_id']
            isbn = row['Isbn']
            for book in matches:
                if book[2] == a_id:
                    book[0] = isbn
                if book[0] == isbn:
                    book[2] = a_id

    with open(books, mode='r', newline='', encoding='utf-8') as f:

        reader = csv.DictReader(f)

        for row in reader:
            isbn = row['Isbn']
            title = row['Title']
            for book in matches:
                if book[0] == isbn:
                    book[1] = title

    with open(authors, mode='r', newline='', encoding='utf-8') as f:

        reader = csv.DictReader(f)

        for row in reader:
            a_id = row['Author_id']
            name = row['Name']
            for book in matches:
                if book[2] == a_id:
                    book[3] = name

    curCheck = 0
    curBook = 0
    combinedIsbns = []
    results = []
    for row in matches:
        if row[0] in combinedIsbns:
            continue
        for book in matches:
            if book[0] in combinedIsbns:
                curBook += 1
            elif curBook <= curCheck:
                curBook += 1
            elif isbn == book[0]:
                row[2] = row[2] + ', ' + book[2]
                row[3] = row[3] + ', ' + book[3]
                combinedIsbns.append(book[0])
            else:
                curBook += 1
        results.append(row)
        curCheck += 1

    print('ISBN       TITLE                                                                                                                                                                 AUTHOR IDS          AUTHORS                       STATUS')
    for row in results:
        if not row:
            next(row)
        print("{: >10} {: >150} {: >20} {: >30} {: >6}".format(*row))


if __name__ == "__main__":
    # Define file paths
    books = '../normalized_data/normalized_book.csv'
    authors = '../normalized_data/normalized_authors.csv'
    book_authors = '../normalized_data/normalized_book_authors.csv'

    # Search data
    search = input()
    book_search(search, books, authors, book_authors)