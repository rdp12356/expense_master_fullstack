# app.py
import os
from flask import Flask, request, jsonify, session, redirect, render_template, url_for
from dotenv import load_dotenv
from models import db, User, EmailToken, APIKey, ExchangeRate, UsageLog
from utils import make_magic_token, confirm_magic_token, generate_api_key_plain, hash_api_key
from email_service import send_verification_email
from fetcher import fetch_and_store
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from functools import wraps

load_dotenv()

def create_app():
    app = Flask(__name__, static_folder="static", template_folder="templates")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///./exchange.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.secret_key = os.getenv("SECRET_KEY", "dev-secret")
    db.init_app(app)
    return app

app = create_app()

# Scheduler for fetching rates
scheduler = BackgroundScheduler()
def scheduled_fetch():
    with app.app_context():
        print("Scheduled fetch:", datetime.utcnow().isoformat())
        fetch_and_store(os.getenv("FETCH_BASE", "USD"))
scheduler.add_job(scheduled_fetch, 'interval', seconds=int(os.getenv("FETCH_INTERVAL_SECONDS", 1800)))
scheduler.start()

# Helpers
def require_login(fn):
    @wraps(fn)
    def wrapper(*a, **kw):
        uid = session.get("user_id")
        if not uid:
            if request.is_json:
                return jsonify({"error":"login required"}), 401
            return redirect(url_for("login_page"))
        request.user = User.query.get(uid)
        return fn(*a, **kw)
    return wrapper

# Routes: pages
@app.route("/")
def index():
    if session.get("user_id"):
        return redirect("/dashboard")
    return redirect("/login")

@app.route("/login")
def login_page():
    return render_template("login.html")

@app.route("/dashboard")
@require_login
def dashboard_page():
    return render_template("dashboard.html", user=request.user)

# magic link request
@app.route("/request-magic-link", methods=["POST"])
def request_magic_link():
    data = request.json or {}
    email = (data.get("email") or "").strip().lower()
    name = (data.get("name") or "").strip()
    if not email:
        return jsonify({"error":"email required"}), 400
    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(email=email, name=name, verified=False)
        db.session.add(user); db.session.commit()
    token = make_magic_token(email)
    expire = datetime.utcnow() + timedelta(hours=24)
    et = EmailToken(user_id=user.id, token=token, expires_at=expire)
    db.session.add(et); db.session.commit()
    sent = send_verification_email(email, token)
    if sent:
        return jsonify({"ok":True, "message":"Magic link sent"})
    else:
        # dev fallback: return link
        host = os.getenv("HOST_URL", "http://localhost:5000")
        return jsonify({"ok":True, "magic_link": f"{host}/magic?token={token}"})

# magic link endpoint
@app.route("/magic")
def magic():
    token = request.args.get("token")
    if not token:
        return "token required", 400
    email = confirm_magic_token(token)
    if not email:
        return "invalid or expired token", 400
    user = User.query.filter_by(email=email).first()
    if not user:
        return "user not found", 404
    user.verified = True
    db.session.commit()
    # remove token records
    EmailToken.query.filter_by(user_id=user.id).delete()
    db.session.commit()
    # set session
    session.clear()
    session["user_id"] = user.id
    session.permanent = True
    return redirect("/dashboard")

# logout
@app.route("/logout", methods=["POST","GET"])
def logout():
    session.clear()
    if request.is_json:
        return jsonify({"ok":True})
    return redirect("/login")

# API: create API key (requires login)
@app.route("/apikeys/create", methods=["POST"])
@require_login
def apikey_create():
    name = (request.json or {}).get("name","default")
    raw = generate_api_key_plain()
    h = hash_api_key(raw)
    ak = APIKey(user_id=request.user.id, key_hash=h, name=name)
    db.session.add(ak); db.session.commit()
    return jsonify({"api_key": raw, "key_id": ak.id})

@app.route("/apikeys/list")
@require_login
def apikeys_list():
    rows = APIKey.query.filter_by(user_id=request.user.id).all()
    res = [{"id":r.id,"name":r.name,"revoked":r.revoked,"created_at":r.created_at.isoformat()} for r in rows]
    return jsonify(res)

@app.route("/apikeys/revoke", methods=["POST"])
@require_login
def apikey_revoke():
    data = request.json or {}
    key_id = data.get("key_id")
    if not key_id:
        return jsonify({"error":"key_id required"}), 400
    ak = APIKey.query.get(key_id)
    if not ak or ak.user_id != request.user.id:
        return jsonify({"error":"not found"}), 404
    ak.revoked = True
    db.session.commit()
    return jsonify({"ok":True})

# simple internal: require api_key header for conversion & rate
def require_apikey(fn):
    @wraps(fn)
    def w(*a, **kw):
        api_key = request.headers.get("X-API-Key") or request.args.get("api_key")
        if not api_key:
            return jsonify({"error":"api_key required"}), 401
        from utils import hash_api_key
        k = APIKey.query.filter_by(key_hash=hash_api_key(api_key), revoked=False).first()
        if not k:
            return jsonify({"error":"invalid key"}), 401
        request.apikey_obj = k
        # log usage
        ul = UsageLog(api_key_id=k.id, endpoint=request.path)
        db.session.add(ul); db.session.commit()
        return fn(*a, **kw)
    return w

@app.route("/convert")
@require_apikey
def convert():
    base = request.args.get("base")
    target = request.args.get("target")
    try:
        amount = float(request.args.get("amount", "1"))
    except:
        amount = 1.0
    if not base or not target:
        return jsonify({"error":"base and target required"}), 400
    ex = ExchangeRate.query.filter_by(base=base.upper(), target=target.upper()).first()
    if not ex:
        return jsonify({"error":"rate not available"}), 404
    return jsonify({"rate": ex.rate, "converted": amount * ex.rate})

@app.route("/latest")
@require_apikey
def latest():
    base = request.args.get("base", os.getenv("FETCH_BASE","USD"))
    rows = ExchangeRate.query.filter_by(base=base.upper()).all()
    if not rows:
        return jsonify({"error":"no rates"}), 404
    rates = {r.target: r.rate for r in rows}
    return jsonify({"base": base.upper(), "rates": rates, "fetched_at": rows[0].fetched_at.isoformat()})

# admin fetch
@app.route("/admin/fetch", methods=["POST"])
def admin_fetch():
    res = fetch_and_store(os.getenv("FETCH_BASE","USD"))
    return jsonify(res)

# usage per key (dashboard)
@app.route("/usage")
@require_login
def usage():
    since = datetime.utcnow() - timedelta(days=1)
    from sqlalchemy import func
    rows = db.session.query(func.count(UsageLog.id)).filter(UsageLog.timestamp>=since, UsageLog.api_key_id==APIKey.id, APIKey.user_id==request.user.id).scalar()
    return jsonify({"last_24h_calls": rows or 0})

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT",5000)), debug=True)
from flask import Flask
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Import routes after app is created
    from routes import register_routes
    register_routes(app)

    return app

app = create_app()
# Initialize the app