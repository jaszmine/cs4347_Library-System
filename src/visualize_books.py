# visualize_books.py
import os
import csv
from collections import Counter
import matplotlib.pyplot as plt

# Auto-detect base directory
BASE_DIR = os.path.dirname(__file__)

def read_csv(filename):
    """Reads a TSV (tab-separated) file into a list of dictionaries."""
    path = os.path.join(BASE_DIR, filename)
    with open(path, newline='', encoding='utf-8-sig') as f:
        return list(csv.DictReader(f, delimiter='\t'))


# Read data from books.csv
books = read_csv(r"..\data\books.csv")


if not books:
    print("No book data found.")
    exit()


# 1. Top Authors by Book Count
author_count = Counter()
for b in books:
    author = (b.get("Author") or "").strip()
    if author:
        author_count[author] += 1

top_authors = author_count.most_common(10)
if top_authors:
    author_names, book_counts = zip(*top_authors)

    plt.figure(figsize=(10, 6))
    plt.barh(author_names[::-1], book_counts[::-1], color='skyblue')
    plt.title("Top 10 Authors by Number of Books")
    plt.xlabel("Book Count")
    plt.ylabel("Author")
    plt.tight_layout()
    plt.show()
else:
    print("No author data found in books.csv")

# 2. Publisher Distribution
publisher_count = Counter()
for b in books:
    publisher = (b.get("Publisher") or "").strip()
    if publisher:
        publisher_count[publisher] += 1

if publisher_count:
    top_publishers = publisher_count.most_common(10)
    publisher_names, pub_counts = zip(*top_publishers)

    plt.figure(figsize=(10, 6))
    plt.barh(publisher_names[::-1], pub_counts[::-1], color='lightgreen')
    plt.title("Top 10 Publishers by Number of Books")
    plt.xlabel("Book Count")
    plt.ylabel("Publisher")
    plt.tight_layout()
    plt.show()
else:
    print("No publisher data found in books.csv")

# 3. Page Count Distribution
pages = []
for b in books:
    try:
        p = int(float(b.get("Pages", 0)))
        if 0 < p < 5000:
            pages.append(p)
    except (ValueError, TypeError):
        pass

if pages:
    plt.figure(figsize=(10, 6))
    plt.hist(pages, bins=30, color='salmon', edgecolor='black')
    plt.title("Distribution of Book Page Counts")
    plt.xlabel("Number of Pages")
    plt.ylabel("Frequency")
    plt.tight_layout()
    plt.show()
else:
    print("No valid page data found in books.csv")

print("All visualizations generated successfully.")
