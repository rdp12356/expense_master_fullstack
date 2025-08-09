# utils.py
import os, hashlib, secrets
from itsdangerous import URLSafeTimedSerializer
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
TOKEN_SALT = "magic-link-salt"

def make_magic_token(email):
    s = URLSafeTimedSerializer(SECRET_KEY)
    return s.dumps(email, salt=TOKEN_SALT)

def confirm_magic_token(token, max_age=3600*24):
    s = URLSafeTimedSerializer(SECRET_KEY)
    try:
        email = s.loads(token, salt=TOKEN_SALT, max_age=max_age)
        return email
    except Exception:
        return None

def generate_api_key_plain():
    return secrets.token_urlsafe(36)

def hash_api_key(key_plain):
    return hashlib.sha256(key_plain.encode("utf-8")).hexdigest()
