# local_db.py
import sqlite3, threading, os
from datetime import datetime

DB_FILE = os.path.join(os.path.dirname(__file__), "local.db")
_LOCK = threading.Lock()

def conn():
    c = sqlite3.connect(DB_FILE, check_same_thread=False)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA foreign_keys=ON;")
    return c

def init_local_db():
    with _LOCK:
        c = conn(); cur = c.cursor()
        cur.executescript("""
        CREATE TABLE IF NOT EXISTS categories (id INTEGER PRIMARY KEY, name TEXT UNIQUE, icon TEXT);
        CREATE TABLE IF NOT EXISTS expenses (id INTEGER PRIMARY KEY, amount REAL, currency TEXT, amount_base REAL, description TEXT, category_id INTEGER, created_at DATETIME DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS settings (k TEXT PRIMARY KEY, v TEXT);
        CREATE TABLE IF NOT EXISTS currencies (code TEXT PRIMARY KEY, name TEXT);
        CREATE TABLE IF NOT EXISTS translations (lang TEXT, key TEXT, text TEXT, PRIMARY KEY(lang,key));
        """)
        c.commit(); c.close()

def execute(q, params=(), commit=False):
    with _LOCK:
        c = conn(); cur = c.cursor()
        cur.execute(q, params)
        if commit:
            c.commit(); last = cur.lastrowid; c.close(); return last
        rows = cur.fetchall(); c.close(); return rows
