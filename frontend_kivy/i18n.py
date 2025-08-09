# i18n.py
import os, json
from local_db import execute

TRAN_DIR = os.path.join(os.path.dirname(__file__), "translations")
os.makedirs(TRAN_DIR, exist_ok=True)

def load_local_translation(lang):
    path = os.path.join(TRAN_DIR, f"{lang}.json")
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    rows = execute("SELECT key,text FROM translations WHERE lang=?", (lang,))
    return {r['key']: r['text'] for r in rows} if rows else {}

def translate(key, lang, fallback=None):
    t = load_local_translation(lang)
    return t.get(key) or fallback or key
