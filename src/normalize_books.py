# Read from data/books.csv --> normalize data --> write to normalized_book.csv
# book.csv COLS: ISBN10	ISBN13	Title	Author	Cover	Publisher	Pages

import csv
import os

def normalize_books(input_file, book_output, book_authors_output, authors_output):
    # Ensure the normalized_data directory exists
    os.makedirs(os.path.dirname(book_output), exist_ok=True)
    os.makedirs(os.path.dirname(book_authors_output), exist_ok=True)
    os.makedirs(os.path.dirname(authors_output), exist_ok=True)

    # Read the original books.csv file
    with open(input_file, mode='r', newline='', encoding='utf-8') as infile:
        # Specify delimiter as tab since the file is tab-separated
        reader = csv.DictReader(infile, delimiter='\t')
        
        print(reader.fieldnames)  # Print the column headers
        books = []
        book_authors = []
        authors = {}

        # book.csv COLS: ISBN10	ISBN13	Title	Author	Cover	Publisher	Pages
        # process by row, extract each field
        for row in reader:
            isbn10 = row['ISBN10']
            isbn13 = row['ISBN13']
            title = row['Title']
            author = row['Author']
            cover = row['Cover']
            publisher = row['Publisher']
            pages = row['Pages']

            # Normalize book data
            books.append({
                'ISBN10': isbn10,
                'ISBN13': isbn13,
                'Title': title,
                'Cover': cover,
                'Publisher': publisher,
                'Pages': pages
            })

            # Normalize authors data
            author = author.strip()
            if author not in authors:
                authors[author] = len(authors) + 1
            author_id = authors[author] # assign unique author_id to each author, populating book_authors
            book_authors.append({'ISBN10': isbn10, 'Author_id': author_id})

    # Write the normalized book.csv file
    with open(book_output, mode='w', newline='', encoding='utf-8') as outfile:
        fieldnames = ['ISBN10', 'ISBN13', 'Title', 'Cover', 'Publisher', 'Pages']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(books)

    # Write the normalized book_authors.csv file
    with open(book_authors_output, mode='w', newline='', encoding='utf-8') as outfile:
        fieldnames = ['ISBN10', 'Author_id']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(book_authors)

    # Write the normalized authors.csv file
    with open(authors_output, mode='w', newline='', encoding='utf-8') as outfile:
        fieldnames = ['Author_id', 'Name']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows({'Author_id': author_id, 'Name': name} for name, author_id in authors.items())

if __name__ == "__main__":
    # Define file paths
    input_file = '../data/books.csv'
    book_output = '../normalized_data/normalized_book.csv'
    book_authors_output = '../normalized_data/normalized_book_authors.csv'
    authors_output = '../normalized_data/normalized_authors.csv'

    # Normalize the books data
    normalize_books(input_file, book_output, book_authors_output, authors_output)