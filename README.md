# Library System Programming Project

## CS-4347 Database Systems (Milestone 1)

This project involves the creation of a database host application that interfaces with a backend SQL database implementing a Library Management System. The first milestone focuses on normalizing the given data into Third Normal Form (3NF) and preparing the schema for further development.

## Table of Contents
- [Project Overview](#project-overview)
- [Directory Structure](#directory-structure)
- [Dependencies](#dependencies)
- [Setup Instructions](#setup-instructions)
- [Normalization Process](#normalization-process)
- [Contributing](#contributing)

## Project Overview
The project aims to develop a Library Management System using SQL. The first milestone involves normalizing the provided `books.csv` and `borrowers.csv` files into separate tables that adhere to the schema defined below.

### Schema
- **BOOK**
  - ISBN
  - Title
- **BOOK_AUTHORS**
  - ISBN
  - Author_id
- **AUTHORS**
  - Author_id
  - Name
- **BORROWER**
  - Card_id
  - Bname
  - Address
  - Phone
  - Ssn
- **BOOK_LOANS**
  - Loan_id
  - ISBN
  - Card_id
  - Date_out
  - Due_date
  - Date_in
- **FINES**
  - Fine_amt
  - Loan_id
  - Paid

## Directory Structure

```tree
cs4347_Library-System/
├── data/
│   ├── books.csv
│   ├── borrowers.csv
├── normalized_data/
│   ├── normalized_book.csv
│   ├── normalized_book_authors.csv
│   ├── normalized_authors.csv
│   ├── normalized_borrower.csv
├── src/
│   ├── normalize_books.py
│   ├── normalize_borrowers.py
├── tests/
│   ├── test_normalize_books.py
│   ├── test_normalize_borrowers.py
├── setup.sh
└── README.md
```


## Dependencies
- Python 3.x
- `csv` module (standard library)
- `pandas` (optional, for more advanced data manipulation)

## Setup Instructions
1. **Clone the Repository:**
```bash
git clone https://github.com/jaszmine/cs4347_Library-System.git
cd cs4347_Library-System
```

2. **Install Dependencies:**
```bash
pip3 install pandas
```

3. **Run the Normalization Scripts:**
Navigate to the src directory and run the normalization scripts:
```bash
python3 normalize_books.py
python3 normalize_borrowers.py
```

4. **Verify the Normalized Data:**
Check the normalized_data directory for the normalized CSV files.

## Normalization Process
Normalizing `books.csv`
The normalize_books.py script reads the books.csv file, normalizes the data into Third Normal Form (3NF), and writes the results to book.csv, book_authors.csv, and authors.csv.

Normalizing `borrowers.csv`
The normalize_borrowers.py script reads the borrowers.csv file and normalizes the data into the borrower.csv file.

## Contributing

1. Fork the Repository:
Fork the repository to your GitHub account.

2. Create a New Branch:
Create a new branch for your feature or fix:
```bash
git checkout -b your-branch-name
```

3. Commit Your Changes:
Commit your changes with descriptive commit messages:
```bash
git add .
git commit -m "Your commit message"
```

4. Push Your Changes:
Push your branch to your forked repository:
```bash
git push origin your-branch-name
```

5. Create a Pull Request:
Go to the original repository and create a pull request from your branch.
