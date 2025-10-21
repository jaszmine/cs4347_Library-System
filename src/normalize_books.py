# Read from data/books.csv --> normalize data --> write to normalized_book.csv

import csv
import os

def normalize_books(input_file, book_output, book_authors_output, authors_output):
    # Ensure the normalized_data directory exists
    os.makedirs(os.path.dirname(book_output), exist_ok=True)
    os.makedirs(os.path.dirname(book_authors_output), exist_ok=True)
    os.makedirs(os.path.dirname(authors_output), exist_ok=True)

    # Read the original books.csv file
    with open(input_file, mode='r', newline='', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        books = []
        book_authors = []
        authors = {}

        for row in reader:
            isbn = row['ISBN']
            title = row['Title']
            authors_str = row['Authors']  # Assuming authors are comma-separated
            authors_list = authors_str.split(',')

            books.append({'ISBN': isbn, 'Title': title})

            for author in authors_list:
                author = author.strip()
                if author not in authors:
                    authors[author] = len(authors) + 1
                author_id = authors[author]
                book_authors.append({'ISBN': isbn, 'Author_id': author_id})

    # Write the normalized book.csv file
    with open(book_output, mode='w', newline='', encoding='utf-8') as outfile:
        fieldnames = ['ISBN', 'Title']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(books)

    # Write the normalized book_authors.csv file
    with open(book_authors_output, mode='w', newline='', encoding='utf-8') as outfile:
        fieldnames = ['ISBN', 'Author_id']
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
    book_output = '../normalized_data/book.csv'
    book_authors_output = '../normalized_data/book_authors.csv'
    authors_output = '../normalized_data/authors.csv'

    # Normalize the books data
    normalize_books(input_file, book_output, book_authors_output, authors_output)