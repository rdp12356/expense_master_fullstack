import hmac
import hashlib
from config import Config

def sign_api_key(raw_key):
    """Sign API key using HMAC with the master secret key."""
    return hmac.new(Config.SECRET_KEY.encode(), raw_key.encode(), hashlib.sha256).hexdigest()

def verify_api_key_signature(raw_key, signature):
    """Verify API key signature."""
    expected = sign_api_key(raw_key)
    return hmac.compare_digest(expected, signature)
