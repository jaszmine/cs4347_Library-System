import csv, mysql.connector

def book_search(search):

    db = mysql.connector.connect(user='root',
        password='password')
    cursor = db.cursor()

    cursor.execute('USE Library;')

    cursor.execute('SELECT *'
                   'FROM books '
                   'INNER JOIN book_authors ON books.isbn = book_authors.isbn '
                   'INNER JOIN authors ON authors.author_id = book_authors.author_id'
                   'WHERE books.isbn LIKE \'%' + search + '%\''
                   '    OR books.title LIKE \'%' + search + '%\''
                   '    OR authors.name LIKE \'%' + search + '%\';')



    print("NO   ISBN       TITLE                                             AUTHORS                                        BORROWED")
    count = 1
    for (books.isbn, books.title, authors.name, books.borrowed) in cursor:
        print("%d {} {} {} {}".format(count, books.isbn, books.title, authors.name, books.borrowed), count)



if __name__ == "__main__":

    # Search data
    search = input()
    book_search(search)