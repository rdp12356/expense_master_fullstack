import os
from dotenv import load_dotenv

# Load env variables from .env
load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-fallback-key")
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    HOST_URL = os.getenv("HOST_URL", "http://localhost:5000")
