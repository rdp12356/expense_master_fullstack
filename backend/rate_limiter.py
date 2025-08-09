# rate_limiter.py
import time
import redis
import os
from functools import wraps
from flask import request, jsonify

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
redis_cli = redis.from_url(REDIS_URL, decode_responses=True)

def token_bucket_key(api_key_id):
    return f"tb:{api_key_id}"

def allow_request(api_key_id, capacity=120, refill_rate_per_sec=2):
    """
    capacity: max tokens (e.g., 120)
    refill_rate_per_sec: number of tokens added per second
    This uses a simple Lua-less approach relying on timestamps / atomicity may vary.
    """
    key = token_bucket_key(api_key_id)
    now = time.time()
    data = redis_cli.hgetall(key)
    if not data:
        tokens = capacity
        last = now
    else:
        tokens = float(data.get("tokens", capacity))
        last = float(data.get("last", now))
    # refill
    delta = now - last
    tokens = min(capacity, tokens + delta * refill_rate_per_sec)
    if tokens < 1:
        # not allowed
        redis_cli.hset(key, mapping={"tokens": tokens, "last": now})
        return False, int(tokens)
    tokens -= 1
    redis_cli.hset(key, mapping={"tokens": tokens, "last": now})
    return True, int(tokens)

def rate_limited(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        # find API key object attached to request
        ak = getattr(request, "apikey_obj", None)
        if not ak:
            return jsonify({"error":"api key required"}), 401
        ok, remain = allow_request(ak.id, capacity=int(os.getenv("RATE_LIMIT_CAP",120)), refill_rate_per_sec=float(os.getenv("RATE_REFILL",2.0)))
        if not ok:
            return jsonify({"error":"rate limit exceeded", "retry_after_seconds": 1}), 429
        return fn(*args, **kwargs)
    return wrapper
