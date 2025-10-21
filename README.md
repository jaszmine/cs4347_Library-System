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
- [Git Reference](#git-reference)

<br>

## Project Overview
The project aims to develop a Library Management System using SQL. The first milestone involves normalizing the provided `books.csv` and `borrowers.csv` files into separate tables that adhere to the schema defined below.

<br>

### Schema
<img width="579" height="579" alt="library-system_schema drawio" src="https://github.com/user-attachments/assets/e9968d64-d5d7-472f-ad1f-58b41e338471" />

<br>

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
│   └── generate_visualizations.py
├── tests/
│   ├── test_normalize_books.py
│   ├── test_normalize_borrowers.py
└── README.md
```

<br>

## Dependencies
- Python 3.x
- `csv` module (standard library)
- `pandas` (optional, for more advanced data manipulation)

<br>

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

<br>

## Normalization Process
Normalizing `books.csv`
The normalize_books.py script reads the books.csv file, normalizes the data into Third Normal Form (3NF), and writes the results to book.csv, book_authors.csv, and authors.csv.

Normalizing `borrowers.csv`
The normalize_borrowers.py script reads the borrowers.csv file and normalizes the data into the borrower.csv file.

<br>

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

<br>

## Git Reference

### Pushing to Your Branch
| Command | Meaning |
|---|---|
| `git branch` | //check what branch you're on |
| `git status` <br> `git status && git branch` | //check branch status OR <br> use helpful one-liner |
| `git checkout main` | //switch to main branch for updates |
| `git pull origin main` | //pull all latest updates from main |
| `git checkout your-branch-name` | //switch to your branch |
| `git merge main` | //merge latest changes from main into your branch |
|  | Edit files, run scripts, etc. |
| `git add .` | //stage changes |
| `git commit -m "Add commit message"` | //commit with message |
| `git push origin your-branch-name` | //push to your branch |

<br>

### If `git merge main` shows conflicts
```bash
# Resolve conflicts in your editor, then:
git add .
git commit -m "Merge main into my branch"
git push origin your-branch-name
```
<br>

### Pushing to Main via Pull Request
| Command | Meaning |
|---|---|
| Complete your work on your branch | Make sure all changes are committed and pushed |
| Go to GitHub | Navigate to repo |
| Click "Pull Requests" → "New Pull Request" | Start the PR process |
| Select: base: `main` ← compare: `your-branch-name` | Set up the merge |
| Add PR title & description | Explain what you changed |
| Request reviews from teammates | Get code review |
| Address review comments | Make requested changes |
| Merge the pull request | Squash & merge recommended |

<br>

### Git Commands During PR Process:
| Command | Meaning |
|---|---|
| `git checkout your-branch-name` | // switch to your branch |
| `git fetch origin` | //	Get latest remote changes |
| `git merge origin/main` | // Update your branch with latest main |
| `git push origin your-branch-name` | // push updates after addressing review comments |

<br>

### Complete PR Workflow Example:
```bash
# 1. Make sure your branch is up to date and ready
git checkout your-branch-name
git fetch origin
git merge origin/main
git push origin your-branch-name

# 2. Go to GitHub and create PR
# - Base: main
# - Compare: your-branch-name
# - Title: "feat: add book normalization script"
# - Description: "Implements 3NF normalization for books data..."

# 3. If teammates request changes:
git checkout your-branch-name
# ... make the requested changes ...
git add .
git commit -m "fix: address PR review comments"
git push your-branch-name
# The PR automatically updates

# 4. After approval, merge via GitHub UI
# Use "Squash and merge" to keep history clean
```

<br>

### Pushing to Main
> Only do this if you're CERTAIN it won't mess shit up <3

| Command | Meaning |
|---|---|
| `git status && git branch` | //check branch status & which branch you're on|
| `git checkout main` | //switch to main branch |
| `git pull origin main` | //pull all latest changes from main |
|  | Edit files, run scripts, etc. |
| `git add .` | //stage changes |
| `git commit -m "Add commit message"` | //commit changes with message |
| `git push origin main` | //push to remote main branch |
