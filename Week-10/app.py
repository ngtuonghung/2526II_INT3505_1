import os
import re
import time
from datetime import datetime, timezone, timedelta
from functools import wraps

import jwt
from flask import Flask, request, jsonify, g
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from loguru import logger
from werkzeug.security import generate_password_hash, check_password_hash

# Config
SECRET_KEY = os.environ.get("SECRET_KEY", "mylittlesecret")
TOKEN_TTL = 3600  # seconds
MAX_FAILED = 5
LOCKOUT_SECONDS = 900  # 15 min

# Logging (suspicious events only)
logger.remove()
logger.add(
    "app.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    level="WARNING",
    rotation="10 MB",
)

# In-memory stores
users = {}           # username -> {password_hash, display_name}
failed_attempts = {} # username -> [epoch_timestamps]

# App
app = Flask(__name__)
CORS(app)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=[],
    storage_uri="memory://",
)


@limiter.request_filter
def _exempt_health():
    return False


def _log(level, event, detail=""):
    ip = request.remote_addr or "unknown"
    getattr(logger, level)(f"{ip} | {event} | {detail}")


# WAF helpers
_SUSPICIOUS_RE = re.compile(r"<\s*script|javascript:|on\w+\s*=", re.IGNORECASE)


def _sanitize(value: str) -> str:
    return (
        value.replace("&", "&amp;")
             .replace("<", "&lt;")
             .replace(">", "&gt;")
             .replace('"', "&quot;")
             .replace("'", "&#x27;")
    )


def _check_xss(field: str, value: str):
    if _SUSPICIOUS_RE.search(value):
        _log("warning", "XSS_ATTEMPT", f"field={field} value={value!r}")


# Auth helpers
def _make_token(username: str) -> str:
    payload = {
        "sub": username,
        "exp": datetime.now(timezone.utc) + timedelta(seconds=TOKEN_TTL),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def require_jwt(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return jsonify({"error": "Missing token"}), 401
        token = auth[7:]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        g.username = payload["sub"]
        return f(*args, **kwargs)
    return wrapper


# Lockout helpers
def _is_locked(username: str) -> bool:
    now = time.time()
    attempts = [t for t in failed_attempts.get(username, []) if now - t < LOCKOUT_SECONDS]
    failed_attempts[username] = attempts
    return len(attempts) >= MAX_FAILED


def _record_failure(username: str):
    failed_attempts.setdefault(username, []).append(time.time())
    count = len(failed_attempts[username])
    _log("warning", "LOGIN_FAILED", f"username={username} attempts={count}")
    if count >= MAX_FAILED:
        _log("warning", "ACCOUNT_LOCKED", f"username={username}")


def _clear_failures(username: str):
    failed_attempts.pop(username, None)


@app.errorhandler(429)
def _ratelimit_handler(e):
    _log("warning", "RATE_LIMIT_EXCEEDED", str(e.description))
    return jsonify({"error": "Too many requests"}), 429


# Routes
@app.post("/auth/register")
@limiter.limit("3 per minute")
def register():
    data = request.get_json(silent=True) or {}
    username = data.get("username", "").strip()
    password = data.get("password", "")
    display_name = data.get("display_name", "").strip()

    if not username or not password or not display_name:
        return jsonify({"error": "username, password, display_name required"}), 400
    if len(username) < 3 or len(username) > 32:
        return jsonify({"error": "username must be 3 to 32 chars"}), 400
    if len(password) < 8:
        return jsonify({"error": "password must be at least 8 chars"}), 400

    _check_xss("username", username)
    _check_xss("display_name", display_name)

    if username in users:
        return jsonify({"error": "User already exists"}), 400

    users[username] = {
        "password_hash": generate_password_hash(password),
        "display_name": _sanitize(display_name),
    }
    return jsonify({"message": "User created"}), 201


@app.post("/auth/login")
@limiter.limit("5 per minute")
def login():
    data = request.get_json(silent=True) or {}
    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or not password:
        return jsonify({"error": "username and password required"}), 400

    if _is_locked(username):
        _log("warning", "LOGIN_BLOCKED", f"username={username} (account locked)")
        return jsonify({"error": "Account locked, try again later"}), 401

    user = users.get(username)
    if not user or not check_password_hash(user["password_hash"], password):
        _record_failure(username)
        return jsonify({"error": "Invalid credentials"}), 401

    _clear_failures(username)
    return jsonify({"token": _make_token(username)}), 200


@app.get("/me")
@require_jwt
def me():
    user = users.get(g.username)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({
        "username": g.username,
        "display_name": user["display_name"],
    }), 200


if __name__ == "__main__":
    app.run(debug=True)
