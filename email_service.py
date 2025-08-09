from itsdangerous import URLSafeTimedSerializer
from config import Config

serializer = URLSafeTimedSerializer(Config.SECRET_KEY)

def generate_verification_token(email):
    return serializer.dumps(email, salt="email-verify")

def confirm_verification_token(token, expiration=3600):
    from itsdangerous import SignatureExpired, BadSignature
    try:
        email = serializer.loads(token, salt="email-verify", max_age=expiration)
    except (SignatureExpired, BadSignature):
        return None
    return email
