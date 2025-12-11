import tkinter
import tkinter.simpledialog
from tkinter import *
from tkinter import ttk
import book_search
import fines
import borrower_management

def search():
    query = tkinter.simpledialog.askstring("Search", "")

    book_search.book_search(query)



if __name__ == "__main__":
    root = Tk()
    frm = ttk.Frame(root, padding=20)
    frm.grid()
    ttk.Label(frm, text="Library System").grid(column=0, row=0)
    ttk.Button(frm, text="Search", command=search).grid(column=0, row=1)
    ttk.Button(frm, text="Borrowers", command=root.destroy).grid(column=0, row=2)
    ttk.Button(frm, text="Quit", command=root.destroy).grid(column=0, row=3)
    root.mainloop()
