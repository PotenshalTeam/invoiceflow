#!/usr/bin/env python3
"""Offline draft-first InvoiceFlow demo; no mail is sent."""
import argparse, datetime as dt, json, sqlite3, re
from decimal import Decimal, InvalidOperation
from pathlib import Path
from html import escape
from email.message import EmailMessage

SCHEMA = """CREATE TABLE IF NOT EXISTS invoices(
id TEXT PRIMARY KEY, customer TEXT NOT NULL,email TEXT NOT NULL,
service TEXT NOT NULL,service_date TEXT NOT NULL,issue_date TEXT NOT NULL,
due_date TEXT NOT NULL,amount INTEGER NOT NULL,currency TEXT NOT NULL,
status TEXT NOT NULL DEFAULT 'DRAFT', paid_date TEXT,payment_method TEXT)"""

def run():
    p=argparse.ArgumentParser(description="Local InvoiceFlow starter")
    p.add_argument("--db",default="invoiceflow.db")
    p.add_argument("--out",default="output")
    sub=p.add_subparsers(dest="command",required=True)
    c=sub.add_parser("create")
    for k in ("id","customer","email","service","service-date","issue-date","amount"):
        c.add_argument("--"+k,required=True)
    c.add_argument("--currency",default="USD")
    c.add_argument("--terms-days",type=int,default=7)
    c=sub.add_parser("confirm-payment")
    for k in ("id","date","method"):c.add_argument("--"+k,required=True)
    c=sub.add_parser("show");c.add_argument("--id",required=True)
    sub.add_parser("list")
    a=p.parse_args()
    con=sqlite3.connect(a.db);con.row_factory=sqlite3.Row
    con.execute(SCHEMA);con.commit()
    out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,79}", a.id if hasattr(a,"id") else "LIST") or (hasattr(a,"id") and ".." in a.id): raise ValueError("Unsafe invoice ID")
    if a.command=="create":
        if "\\n" in a.email or "\\r" in a.email or "@" not in a.email: raise ValueError("Invalid email")
        if not re.fullmatch(r"[A-Z]{3}",a.currency.upper()): raise ValueError("Invalid currency")
        cents=Decimal(a.amount)*100
        if not cents.is_finite() or cents != cents.to_integral_value() or cents<=0:raise ValueError("Invalid amount")
        issue=dt.date.fromisoformat(a.issue_date)
        dt.date.fromisoformat(a.service_date)
        if not 0 <= a.terms_days <= 365:raise ValueError("Invalid payment terms")
        due=issue+dt.timedelta(days=a.terms_days)
        con.execute("INSERT INTO invoices VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
          (a.id,a.customer,a.email,a.service,a.service_date,str(issue),str(due),int(cents),a.currency,"DRAFT",None,None))
        con.commit()
    if a.command=="confirm-payment":
        dt.date.fromisoformat(a.date)
        row=con.execute("SELECT status FROM invoices WHERE id=?",(a.id,)).fetchone()
        if not row:raise ValueError("Invoice not found")
        if row["status"]=="PAID":raise ValueError("Payment already recorded")
        if not a.method.strip():raise ValueError("Payment method required")
        con.execute("UPDATE invoices SET status='PAID',paid_date=?,payment_method=? WHERE id=?",(a.date,a.method,a.id));con.commit()
    if a.command in ("show","create","confirm-payment"):
        row=con.execute("SELECT * FROM invoices WHERE id=?",(a.id,)).fetchone()
        if row is None:raise ValueError("Invoice not found")
        row=dict(row)
        amount=f'{row["currency"]} {Decimal(row["amount"])/100:.2f}'
        title="PAID INVOICE" if row["status"]=="PAID" else "INVOICE"
        details=(f'<h2>PAID IN FULL</h2><p>Paid {escape(row["paid_date"])} via {escape(row["payment_method"])}<br>Balance: {row["currency"]} 0.00</p>'
                 if row["status"]=="PAID" else "")
        html=f'''<!doctype html><meta charset="utf-8"><title>{escape(row["id"])}</title>
<style>body{{font:16px Arial;max-width:720px;margin:48px auto;color:#253046}}header{{border-bottom:3px solid #253046}}article{{padding:24px 0}}footer{{margin-top:48px;color:#777}}</style>
<header><h1>{title}</h1></header><article><p><b>Invoice:</b> {escape(row["id"])}</p>
<p><b>Bill to:</b> {escape(row["customer"])}</p>
<p><b>Service:</b> {escape(row["service"])} ({escape(row["service_date"])})</p>
<p><b>Issued:</b> {row["issue_date"]} · <b>Due:</b> {row["due_date"]}</p>
<h2>Total: {amount}</h2>{details}</article><footer>InvoiceFlow local example; check legal requirements before issuing.</footer>'''
        suffix="-PAID" if row["status"]=="PAID" else ""
        invoice=out/(a.id+suffix+".html");invoice.write_text(html,encoding="utf8")
        if a.command=="create":
            msg=EmailMessage()
            msg["To"]=row["email"];msg["Subject"]=f'Invoice {row["id"]}'
            msg.set_content(f'Hello {row["customer"]},\n\nPlease find invoice {row["id"]} for {row["service"]}.\nTotal: {amount}\nDue: {row["due_date"]}\n\nAttach {invoice.name} before sending.')
            (out/(a.id+"-UNSENT.eml")).write_bytes(msg.as_bytes())
        print(json.dumps({"status":row["status"],"invoice":str(invoice),"sent":False}))
    else:
        print(json.dumps([dict(r) for r in con.execute("SELECT * FROM invoices")],indent=2))
if __name__=="__main__":run()
