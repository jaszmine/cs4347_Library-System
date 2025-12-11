import tkinter
import tkinter.simpledialog
from tkinter import *
from tkinter import ttk
import book_search
import fines
import borrower_management

def search():
    query = tkinter.simpledialog.askstring(" ", "Search")

    book_search.book_search(query)

def borrowers():
    borrowers = Tk()
    frm = ttk.Frame(borrowers, padding=20)
    frm.grid()
    ttk.Label(frm, text="Borrowers").grid(column=0, row=0)
    ttk.Button(frm, text="Add Borrower", command=addborrower).grid(column=0, row=1)
    ttk.Button(frm, text="Quit", command=root.destroy).grid(column=0, row=2)
    root.mainloop()

def addborrower():

    name = tkinter.simpledialog.askstring(" ", "Name")
    ssn = tkinter.simpledialog.askstring(" ", "SSN")
    address = tkinter.simpledialog.askstring(" ", "Address")
    phone = tkinter.simpledialog.askstring(" ", "Phone")

    borrower_management.add_borrower(name, ssn, address, phone)

    ttk.Label(frm, text="Borrower Successfully Created").grid(column=0, row=0)
    ttk.Button(frm, text="Quit", command=root.destroy).grid(column=0, row=1)

def fine():
    fine = Tk()
    frm = ttk.Frame(fine, padding=40)
    frm.grid()
    ttk.Label(frm, text="Fines").grid(column=0, row=0)
    ttk.Button(frm, text="Get Fines", command=getfines).grid(column=0, row=1)
    ttk.Button(frm, text="Pay Fines", command=payfines).grid(column=0, row=2)
    ttk.Button(frm, text="Quit", command=root.destroy).grid(column=0, row=3)
    root.mainloop()

def getfines():
    fines.list_fines(True)

def payfines():
    query = tkinter.simpledialog.askstring(" ", "Card ID")
    fines.pay_fines(query)
    result = Tk()
    frm = ttk.Frame(result, padding=40)
    frm.grid()
    ttk.Label(frm, text="All Fines Successfully Paid").grid(column=0, row=0)
    ttk.Button(frm, text="Quit", command=root.destroy).grid(column=0, row=1)
    root.mainloop()

if __name__ == "__main__":
    root = Tk()
    frm = ttk.Frame(root, padding=40)
    frm.grid()
    ttk.Label(frm, text="Library System").grid(column=0, row=0)
    ttk.Button(frm, text="Search", command=search).grid(column=0, row=1)
    ttk.Button(frm, text="Borrowers", command=borrowers).grid(column=0, row=2)
    ttk.Button(frm, text="Fines", command=fine).grid(column=0, row=3)
    ttk.Button(frm, text="Quit", command=root.destroy).grid(column=0, row=4)
    root.mainloop()
