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

def borrowers():
    borrowers = Tk()
    frm = ttk.Frame(borrowers, padding=20)
    frm.grid()
    ttk.Label(frm, text="Borrowers").grid(column=0, row=0)
    ttk.Button(frm, text="Get Fines", command=fines.list_fines).grid(column=0, row=1)
    ttk.Button(frm, text="Pay Fines", command=payfines).grid(column=0, row=2)
    ttk.Button(frm, text="Quit", command=root.destroy).grid(column=0, row=3)
    root.mainloop()

def add_borrower():
    name = tkinter.simpledialog.askstring("Add Borrower", "Name:")
    if not name:
        return

    ssn = tkinter.simpledialog.askstring("Add Borrower", "SSN:")
    if not ssn:
        return

    address = tkinter.simpledialog.askstring("Add Borrower", "Address:")
    if not address:
        return

    phone = tkinter.simpledialog.askstring("Add Borrower", "Phone (optional):")
    if phone is not None:
        phone = phone.strip() or None

    try:
        card_id = borrower_management.add_borrower(
            name.strip(),
            ssn.strip(),
            address.strip(),
            phone
        )
        messagebox.showinfo("Success", f"Borrower added.\nCard ID: {card_id}")
    except ValueError as e:
        messagebox.showwarning("Invalid Input", str(e))
    except RuntimeError as e:
        messagebox.showerror("Error", str(e))
    except Exception as e:
        messagebox.showerror("Error", f"{e}")

def payfines():
    query = tkinter.simpledialog.askstring("Card ID", "")

    fines.pay_fines(query)

if __name__ == "__main__":
    root = Tk()
    frm = ttk.Frame(root, padding=20)
    frm.grid()
    ttk.Label(frm, text="Library System").grid(column=0, row=0)
    ttk.Button(frm, text="Search", command=search).grid(column=0, row=1)
    ttk.Button(frm, text="Borrowers", command=borrowers).grid(column=0, row=2)
    ttk.Button(frm, text="Quit", command=root.destroy).grid(column=0, row=3)
    root.mainloop()
