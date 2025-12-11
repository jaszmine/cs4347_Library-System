from tkinter import *
from tkinter import ttk
import book_search
import fines
import borrower_management

if __name__ == "__main__":
    root = Tk()
    frm = ttk.Frame(root, padding=10)
    frm.grid()
    ttk.Label(frm, text="Library System").grid(column=0, row=0)
    ttk.Button(frm, text="Search", command=root.destroy).grid(column=2, row=0)
    ttk.Button(frm, text="Borrowers", command=root.destroy).grid(column=3, row=0)
    ttk.Button(frm, text="Quit", command=root.destroy).grid(column=4, row=0)
    root.mainloop()