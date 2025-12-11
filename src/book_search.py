import mysql.connector
import tkinter
from tkinter import ttk
from tkinter import *

def book_search(search):

    db = mysql.connector.connect(user='root',
        password='password')
    cursor = db.cursor()

    cursor.execute('USE Library;')

    cursor.execute('SELECT books.isbn AS isbn, books.title AS title, GROUP_CONCAT(authors.name SEPARATOR \', \'), books.borrowed AS borrowed '
                   'FROM books '
                   'INNER JOIN book_authors ON books.isbn = book_authors.isbn '
                   'INNER JOIN authors ON authors.author_id = book_authors.author_id '
                   'WHERE books.isbn LIKE \'%' + search + '%\' '
                   '    OR books.title LIKE \'%' + search + '%\' '
                   '    OR authors.name LIKE \'%' + search + '%\' '
                   'GROUP BY isbn;')



    print("NO  ISBN       TITLE                                                                                                                                                                                                    AUTHORS                                            BORROWED")
    count = 1
    #for (isbn, title, name, borrowed) in cursor:
    #    print("{: <3} {: <10} {: <200} {: <50} {: <1}".format(count, isbn, title, name, borrowed))
    #    count += 1

    root = tkinter.Tk()
    root.geometry('1500x1000')
    listbox = Listbox(root, width=300)

    listbox.pack(side = LEFT, fill = BOTH)

    scrollbar = Scrollbar(root)

    scrollbar.pack(side = RIGHT, fill = BOTH)

# Insert elements into the listbox
    count = 1
    listbox.insert(END, "NO  ISBN       TITLE                                                                                                                                                                                                    AUTHORS                                            BORROWED")
    for (isbn, title, name, borrowed) in cursor:
        listbox.insert(END, "{: <3} {: <10} {: <200} {: <50} {: <1}".format(count, isbn, title, name, borrowed))
        count += 1

# Attaching Listbox to Scrollbar
# Since we need to have a vertical
# scroll we use yscrollcommand
    listbox.config(yscrollcommand = scrollbar.set)

# setting scrollbar command parameter
# to listbox.yview method its yview because
# we need to have a vertical view
    scrollbar.config(command = listbox.yview)

    cursor.close()


if __name__ == "__main__":

    # Search data
    search = input()
    book_search(search)