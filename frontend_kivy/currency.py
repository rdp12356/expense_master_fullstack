# currency.py
import requests
from local_db import execute

SERVER_URL = "http://127.0.0.1:5000"  # change for remote
def populate_currencies():
    try:
        r = requests.get(f"{SERVER_URL}/admin/fetch")  # triggers server fetch (admin)
    except:
        pass
    # client fills basic list (you can call /currencies if you add that endpoint)
    execute("INSERT OR IGNORE INTO currencies (code,name) VALUES (?,?)", ("USD","US Dollar"), commit=True)
    execute("INSERT OR IGNORE INTO currencies (code,name) VALUES (?,?)", ("INR","Indian Rupee"), commit=True)
