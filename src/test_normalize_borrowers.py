import csv
import os

def test_normalize_borrowers(borrowers):
  existingSSns = []
  existingPhoneNum = []
  existingEmailAddr = []

  with open(borrowers, mode='r', newline='', encoding='utf-8') as f:

    reader = csv.DictReader(f)
    curRow = 1

    for row in reader:
      ssn = row['ssn']
      phoneNum = row['phone']
      emailAddr = row['email']
       if len(isbn) > 11:
         print(f"Row {curRow} in borrowers has an invalid SSN length!")
       if len(phoneNum) > 15:
         print(f"Row {curRow} in borrowers has an invalid phone number length!")
       if '@' not in emailAddr:
         print(f"Row {curRow} in borrowers has an invalid email address format!")
         
       existingSSns.append(ssn)
       existingPhoneNum.append(phoneNum)
       existingEmailAddr.append(emailAddr)
       curRow += 1

   if __name__ == "__main__":
    # Define file paths
    borrowers = '../data/borrowers.csv'


    # Normalize the books data
    test_normalize_borrowers(borrowers)
    print("All files validated")
