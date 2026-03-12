import hashlib
import os
import secrets
from functools import wraps
from flask import Blueprint, request, jsonify, abort, make_response
from datetime import datetime, timezone, timedelta
import jwt

JWT_SECRET = os.environ.get("JWT_SECRET", "2526II_INT3505_1_SECRET")  # MUST override via env in production
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRY_MINUTES = 15
REFRESH_TOKEN_EXPIRY_DAYS = 7
COOKIE_SECURE = os.environ.get("COOKIE_SECURE", "false").lower() == "true"

# Passwords stored as SHA-256 hex digests
USERS = {
    "admin": "8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918",
}

refresh_tokens = {}  # In-memory only — cleared on every server restart

auth_bp = Blueprint("auth", __name__)


def issue_access_token(username):
    exp = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRY_MINUTES)
    return jwt.encode({"sub": username, "exp": exp}, JWT_SECRET, algorithm=JWT_ALGORITHM)


def issue_refresh_token(username):
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRY_DAYS)
    refresh_tokens[token] = {"username": username, "expires_at": expires_at}
    return token


def set_refresh_cookie(resp, token):
    resp.set_cookie(
        "refresh_token",
        token,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite="Strict",
        max_age=REFRESH_TOKEN_EXPIRY_DAYS * 86400,
        path="/auth",  # limits cookie scope to /auth routes only
    )


def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            abort(401, description="Missing or malformed Authorization header")
        token = auth_header[len("Bearer "):]
        try:
            jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        except jwt.ExpiredSignatureError:
            abort(401, description="Token has expired")
        except jwt.InvalidTokenError:
            abort(401, description="Invalid token")
        return f(*args, **kwargs)

    return decorated


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True)
    if not data:
        abort(400, description="Request body must be JSON")
    username = data.get("username", "").strip()
    password = data.get("password", "")
    if not username or not password:
        abort(400, description="'username' and 'password' are required")
    stored_hash = USERS.get(username)
    password_hash = password  # pre-hashed SHA-256 from client
    # Vulnerable to timing attack — use hmac.compare_digest() in production
    if stored_hash is None or password_hash != stored_hash:
        abort(401, description="Invalid credentials")
    resp = make_response(jsonify({"access_token": issue_access_token(username)}), 200)
    set_refresh_cookie(resp, issue_refresh_token(username))
    return resp


@auth_bp.route("/refresh", methods=["POST"])
def refresh():
    token = request.cookies.get("refresh_token")
    if not token:
        abort(401, description="No refresh token")
    entry = refresh_tokens.get(token)
    if not entry:
        abort(401, description="Invalid refresh token")
    if datetime.now(timezone.utc) > entry["expires_at"]:
        refresh_tokens.pop(token, None)
        abort(401, description="Refresh token expired")
    # Refresh token is not rotated — reuse until expiry
    # Refresh token is not rotated — reused until expiry
    return jsonify({"access_token": issue_access_token(entry["username"])}), 200


@auth_bp.route("/logout", methods=["POST"])
def logout():
    token = request.cookies.get("refresh_token")
    if token:
        refresh_tokens.pop(token, None)
    resp = make_response(jsonify({"message": "Logged out"}), 200)
    resp.set_cookie(
        "refresh_token",
        "",
        max_age=0,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite="Strict",
        path="/auth",
    )
    return resp
