import csv, os, mysql.connector
from mysql.connector import errorcode

def createTables(books, authors, bookauthors):

    TABLES = {}
    TABLES['books'] = (
        "CREATE TABLE `books` ("
        "  `isbn` varchar(10) NOT NULL,"
        "  `title` varchar(200) NOT NULL,"
        "  `borrowed` boolean NOT NULL,"
        "  PRIMARY KEY (`isbn`)"
        ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4")

    TABLES['authors'] = (
        "CREATE TABLE `authors` ("
        "  `name` varchar(100) NOT NULL,"
        "  `author_id` int(10) NOT NULL,"
        "  PRIMARY KEY (`author_id`)"
        ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
    )

    TABLES['book_authors'] = (
        "CREATE TABLE `book_authors` ("
        "  `isbn` varchar(10) NOT NULL,"
        "  `author_id` int(10) NOT NULL,"
        "  FOREIGN KEY (`isbn`) "
        "       REFERENCES `books` (`isbn`) ON DELETE CASCADE,"
        "  FOREIGN KEY (`author_id`) "
        "       REFERENCES `authors` (`author_id`)"
        ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
    )
    TABLES['borrower'] = (
        "CREATE TABLE `borrowers` ("
        "  `ssn` int(9) NOT NULL,"
        "  `name` varchar(20) NOT NULL,"
        "  `card_id` int(10) NOT NULL,"
        "  `address` varchar(100) NOT NULL,"
        "  `phone` int(10),"
        "  PRIMARY KEY (`card_id`),"
        "UNIQUE KEY `ssn` (`ssn`)"
        ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
    )
    TABLES['book_loans'] = (
        "CREATE TABLE `book_loans` ("
        "  `loan_id` int(10) NOT NULL,"
        "  `isbn` varchar(10) NOT NULL,"
        "  `card_id` int(10) NOT NULL,"
        "  `date_out` date NOT NULL,"
        "  `due_date` date NOT NULL,"
        "  `date_in` date NOT NULL,"
        "  `loan_count` enum('1', '2', '3') NOT NULL,"
        "  PRIMARY KEY (loan_id),"
        "  UNIQUE KEY `loans_per_borrower` (`loan_count`, `card_id`),"
        "  FOREIGN KEY (`card_id`) "
        "       REFERENCES `borrower` (`card_id`)"
        ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
    )
    TABLES['fines'] = (
        "CREATE TABLE `fines` ("
        "  `loan_id` int(10) NOT NULL,"
        "  `fine_amt` decimal(4,2) NOT NULL,"
        "  `paid` boolean NOT NULL,"
        "  PRIMARY KEY (`loan_id`),"
        "  FOREIGN KEY (`loan_id`) "
        "       REFERENCES `book_loans` (`loan_id`)"
        ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
    )

    db = mysql.connector.connect(user='root',
        password='password')
    cursor = db.cursor()
    dbname = "Library"

    def create_database(cursor):
        try:
            cursor.execute(
                "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(dbname))
        except mysql.connector.Error as err:
            print("Failed creating database: {}".format(err))
            exit(1)

    created = False
    try:
        cursor.execute("USE {}".format(dbname))
    except mysql.connector.Error as err:
        print("Database {} does not exist.".format(dbname))
        if err.errno == errorcode.ER_BAD_DB_ERROR:
            create_database(cursor)
            created = True
            print("Database {} created successfully.".format(dbname))
            db.database = dbname
        else:
            print(err)
            exit(1)
    cursor.execute("SET @OLD_FOREIGN_KEY_CHECKS =@@FOREIGN_KEY_CHECKS")

    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")

    for table_name in TABLES:
        table_description = TABLES[table_name]
        try:
            print("Creating table {}: ".format(table_name), end='')
            cursor.execute(table_description)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                print("already exists.")
            else:
                print(err.msg)
        else:
            print("All tables created")

    if created:
        with open(books, mode='r', newline='', encoding='utf-8') as f:

            reader = csv.DictReader(f)

            add_book = ("INSERT INTO books "
                        "(`isbn`, `title`, `borrowed`)"
                        "VALUES (%s, %s, %s)")

            for row in reader:
                book_data = (row['Isbn'], row['Title'], False)
                cursor.execute(add_book, book_data)
            db.commit()

        with open(authors, mode='r', newline='', encoding='utf-8') as f:

            reader = csv.DictReader(f)

            add_author = ("INSERT INTO authors "
                        "(`name`, `author_id`)"
                        "VALUES (%s, %s)")

            for row in reader:
                author_data = (row['Name'], row['Author_id'])
                cursor.execute(add_author, author_data)
            db.commit()

        with open(bookauthors, mode='r', newline='', encoding='utf-8') as f:

            reader = csv.DictReader(f)

            add_bookauthor = ("INSERT INTO book_authors "
                        "(`isbn`, `author_id`)"
                        "VALUES (%s, %s)")

            for row in reader:
                bookauthor_data = (row['Isbn'], row['Author_id'])
                cursor.execute(add_bookauthor, bookauthor_data)
            db.commit()

    cursor.execute("SET FOREIGN_KEY_CHECKS = @OLD_FOREIGN_KEY_CHECKS")
    cursor.close()
    db.close()

if __name__ == "__main__":
    # Define file paths
    books = '../normalized_data/normalized_book.csv'
    authors = '../normalized_data/normalized_authors.csv'
    book_authors = '../normalized_data/normalized_book_authors.csv'

    # Create Database
    createTables(books, authors, book_authors)
