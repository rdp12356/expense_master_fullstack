# db_init.py
from app import create_app
from models import db
import os

app = create_app()
with app.app_context():
    db.create_all()
    print("DB created at:", os.environ.get("DATABASE_URL", "sqlite:///./exchange.db"))
