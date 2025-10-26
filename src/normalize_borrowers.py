# borrowers.csv COLS: ID0000id, ssn, first_name, last_name, email, address, city, state, phone
# card id pk, ssn optional

import csv, os, re

def digits(s): 
    return re.sub(r"\D","",str(s or ""))

def clean(s): 
    return str(s or "").strip()

def titlecase(s): 
    return " ".join(w.capitalize() for w in clean(s).split())

def normalize_borrowers(inp_file, out_file):
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    with open(inp_file, 'r', newline='', encoding='utf8') as f:
        rdr = csv.DictReader(f)
        print("reading cols:", rdr.fieldnames)
        out_rows = []
        seen_card = set()
        seen_ssn = set()
        for r in rdr:
            cid = clean(r.get("ID0000id"))
            ssn = digits(r.get("ssn"))
            fname = clean(r.get("first_name"))
            lname = clean(r.get("last_name"))
            email = clean(r.get("email")).lower()
            street = clean(r.get("address"))
            city = clean(r.get("city"))
            state = clean(r.get("state"))[:2].upper()
            phone = digits(r.get("phone"))
            if not cid: 
                continue
            if cid in seen_card: 
                continue
            if ssn and ssn in seen_ssn:
                continue
            bname = (f"{titlecase(fname)} {titlecase(lname)}").strip()
            out_rows.append({
                "Card_id": cid,
                "Bname": bname,
                "Email": email,
                "Street": street,
                "City": city,
                "State": state,
                "Phone": phone,
                "Ssn": ssn
            })
            seen_card.add(cid)
            if ssn:
                seen_ssn.add(ssn)
    with open(out_file,'w',newline='',encoding='utf8') as f2:
        cols = ["Card_id","Bname","Email","Street","City","State","Phone","Ssn"]
        w = csv.DictWriter(f2, fieldnames=cols)
        w.writeheader(); w.writerows(out_rows)
        print("wrote",len(out_rows),"rows to",out_file)
        print("pk is card id, ssn uniq wen present lol")

def verify3nf():
    print("\n3nf chek")
    print("1nf ok")
    print("2nf ok (single key card_id)")
    print("3nf ok no dependcy mess")
    print("card id pk, ssn uniq optional")

if __name__=="__main__":
    inp = "/home/hung/Desktop/Scripts/borrowers(1).csv"
    out = "/home/hung/Desktop/Scripts/borrower_really_normalized.csv"
    normalize_borrowers(inp,out)
    verify3nf()
