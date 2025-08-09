import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from config import Config

load_dotenv()

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.office365.com")
SMTP_PORT   = int(os.getenv("SMTP_PORT", 587))
SMTP_EMAIL  = os.getenv("SMTP_EMAIL")
SMTP_PASS   = os.getenv("SMTP_PASSWORD")
EMAIL_FROM  = os.getenv("EMAIL_FROM", SMTP_EMAIL)

# Single serializer for tokens
serializer = URLSafeTimedSerializer(Config.SECRET_KEY)

def generate_verification_token(email):
    return serializer.dumps(email, salt="email-verify")

def confirm_verification_token(token, expiration=3600):
    try:
        email = serializer.loads(token, salt="email-verify", max_age=expiration)
    except (SignatureExpired, BadSignature):
        return None
    return email

def send_verification_email(recipient_email, verification_link):
    if not (SMTP_EMAIL and SMTP_PASS):
        print("SMTP not configured. Skipping email send.")
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Verify your ExpenseMaster email"
    msg["From"] = EMAIL_FROM
    msg["To"] = recipient_email

    text = f"Please verify your email: {verification_link}"
    html = f"""
    <html>
      <body>
        <p>Click the link below to verify:</p>
        <a href="{verification_link}">Verify Email</a>
      </body>
    </html>
    """

    msg.attach(MIMEText(text, "plain"))
    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_EMAIL, SMTP_PASS)
            server.sendmail(SMTP_EMAIL, recipient_email, msg.as_string())
        return True
    except Exception as e:
        print("Email send failed:", e)
        return False
