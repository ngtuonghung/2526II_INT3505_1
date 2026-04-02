import hashlib
import os
import secrets
from functools import wraps
from flask import Blueprint, request, jsonify, abort, make_response
from datetime import datetime, timezone, timedelta
import jwt

JWT_SECRET = os.environ.get("JWT_SECRET", "2526II_INT3505_1_SECRET")
JWT_ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRY_MINUTES = 0.5
REFRESH_TOKEN_EXPIRY_DAYS = 7

ACCESS_COOKIE_NAME = "access_token"
REFRESH_COOKIE_NAME = "refresh_token"

# Scopes per role
ROLE_SCOPES = {
    "admin": ["read", "write", "delete", "manage_users", "view_reports"],
    "customer": ["read", "write"],
}

ROLE_DISPLAY = {
    "admin": "Quản trị viên",
    "customer": "Khách hàng",
}

SCOPE_DISPLAY = {
    "read": "xem dữ liệu",
    "write": "thêm/sửa dữ liệu",
    "delete": "xóa dữ liệu",
    "manage_users": "quản lý người dùng",
    "view_reports": "xem báo cáo",
}

# Passwords stored as SHA-256 hex digests
# Format: { username: { "password": <sha256>, "role": <role> } }
USERS = {
    "admin0": {
        "password": "8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918",  # SHA-256("admin")
        "role": "admin",
    },
    "customer0": {
        "password": "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8",  # SHA-256("password")
        "role": "customer",
    },
}

refresh_tokens = {}  # In-memory only — cleared on every server restart

auth_bp = Blueprint("auth", __name__)


def issue_access_token(username):
    exp = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRY_MINUTES)
    role = USERS[username]["role"]
    scope = ROLE_SCOPES[role]
    payload = {"sub": username, "exp": exp, "role": role, "scope": scope}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def issue_refresh_token(username):
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRY_DAYS)
    refresh_tokens[token] = {"username": username, "expires_at": expires_at}
    return token


def set_refresh_cookie(resp, token):
    # Server → client: token delivered via "Set-Cookie" response header
    # Client → server: browser auto-sends it in "Cookie" request header on /auth/* requests
    resp.set_cookie(
        REFRESH_COOKIE_NAME,
        token,
        httponly=True,
        secure=True,
        samesite="Strict",
        max_age=REFRESH_TOKEN_EXPIRY_DAYS * 86400,
        path="/auth",  # limits cookie scope to /auth routes only
    )


def set_access_cookie(resp, token):
    # Server → client: token delivered via "Set-Cookie" response header
    # Client → server: browser auto-sends it in "Cookie" request header on every request
    resp.set_cookie(
        ACCESS_COOKIE_NAME,
        token,
        httponly=True,
        secure=True,
        samesite="Strict",
        max_age=int(ACCESS_TOKEN_EXPIRY_MINUTES * 60),
        path="/",  # allows access on protected API routes
    )


def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # Access token read from "Cookie" request header
        token = request.cookies.get(ACCESS_COOKIE_NAME)
        if not token:
            abort(401, description="Missing access token cookie")
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        except jwt.ExpiredSignatureError:
            abort(401, description="Token has expired")
        except jwt.InvalidTokenError:
            abort(401, description="Invalid token")
        # Inject token claims into kwargs so route handlers can use them
        kwargs["token_payload"] = payload
        return f(*args, **kwargs)

    return decorated


def require_scope(required_scope):
    """Decorator to restrict a route to users who have a specific scope."""
    def decorator(f):
        @wraps(f)
        @require_auth
        def decorated(*args, **kwargs):
            payload = kwargs.get("token_payload", {})
            if required_scope not in payload.get("scope", []):
                abort(403, description=f"Requires scope: {required_scope}")
            return f(*args, **kwargs)
        return decorated
    return decorator


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True)
    if not data:
        abort(400, description="Request body must be JSON")
    username = data.get("username", "").strip()
    password = data.get("password", "")
    if not username or not password:
        abort(400, description="'username' and 'password' are required")
    user_entry = USERS.get(username)
    password_hash = password  # pre-hashed SHA-256 from client
    if user_entry is None or password_hash != user_entry["password"]:
        abort(401, description="Invalid credentials")
    role = user_entry["role"]
    scope = ROLE_SCOPES[role]
    scope_text = ", ".join(SCOPE_DISPLAY[s] for s in scope)
    message = f"Bạn là {ROLE_DISPLAY[role]}, bạn có quyền: {scope_text}."
    resp = make_response(
        jsonify({"message": message, "role": role, "scope": scope}), 200
    )
    set_access_cookie(resp, issue_access_token(username))
    set_refresh_cookie(resp, issue_refresh_token(username))
    return resp


@auth_bp.route("/refresh", methods=["POST"])
def refresh():
    # Refresh token read from "Cookie" request header
    token = request.cookies.get(REFRESH_COOKIE_NAME)
    if not token:
        abort(401, description="No refresh token")
    entry = refresh_tokens.get(token)
    if not entry:
        abort(401, description="Invalid refresh token")
    if datetime.now(timezone.utc) > entry["expires_at"]:
        refresh_tokens.pop(token, None)
        abort(401, description="Refresh token expired")
    # Refresh token is not rotated — reused until expiry
    resp = make_response(jsonify({"message": "Access token refreshed"}), 200)
    set_access_cookie(resp, issue_access_token(entry["username"]))
    return resp


@auth_bp.route("/logout", methods=["POST"])
def logout():
    # Refresh token read from "Cookie" request header; cleared by overwriting cookies with empty value + max_age=0
    token = request.cookies.get(REFRESH_COOKIE_NAME)
    if token:
        refresh_tokens.pop(token, None)
    resp = make_response(jsonify({"message": "Logged out"}), 200)
    resp.set_cookie(
        REFRESH_COOKIE_NAME,
        "",
        max_age=0,
        httponly=True,
        secure=True,
        samesite="Strict",
        path="/auth",
    )
    resp.set_cookie(
        ACCESS_COOKIE_NAME,
        "",
        max_age=0,
        httponly=True,
        secure=True,
        samesite="Strict",
        path="/",
    )
    return resp


# Demo: any logged-in user — returns info from JWT
@auth_bp.route("/me")
@require_auth
def me(token_payload):
    return jsonify({
        "username": token_payload["sub"],
        "role": token_payload["role"],
        "scope": token_payload["scope"],
    })


# Demo: admin only (requires "manage_users" scope)
@auth_bp.route("/admin/users")
@require_scope("manage_users")
def admin_users(**_):
    return jsonify({"users": list(USERS.keys())})
