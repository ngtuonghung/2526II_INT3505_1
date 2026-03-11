import hashlib
import json
import os
import secrets
from functools import wraps
from flask import Flask, request, jsonify, abort, make_response
from flask_cors import CORS
from datetime import datetime, timezone, timedelta
import jwt  # PyJWT

app = Flask(__name__)
# credentials=True is required for the refresh-token HttpOnly cookie.
# Origins must match the exact page origin (wildcards are disallowed with credentials).
DEFAULT_CORS_ORIGINS = [
    "http://127.0.0.1:5500",
    "http://127.0.0.1:3000",
]
CORS_ORIGINS = [
    o.strip() for o in os.environ.get("CORS_ORIGINS", "").split(",") if o.strip()
] or DEFAULT_CORS_ORIGINS
CORS(app, supports_credentials=True, origins=CORS_ORIGINS)

# ── Token config ──────────────────────────────────────────────────────────────
JWT_SECRET = os.environ.get("JWT_SECRET", "2526II_INT3505_1_SECRET")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRY_MINUTES = 15
REFRESH_TOKEN_EXPIRY_DAYS = 7
# Set COOKIE_SECURE=true in production (requires HTTPS)
COOKIE_SECURE = os.environ.get("COOKIE_SECURE", "false").lower() == "true"

USERS = {
    "admin": "8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918",
}

notes = {}
next_id = 1

refresh_tokens = {}


def note_etag(note):
    return hashlib.md5(json.dumps(note, sort_keys=True).encode()).hexdigest()


# ── Token helpers ─────────────────────────────────────────────────────────────
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
        path="/auth",  # cookie only sent to /auth/* routes
    )


def require_auth(f):
    """Decorator: validates Bearer JWT from Authorization header; aborts 401 otherwise."""
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


def make_note(title, content):
    global next_id
    note = {
        "id": next_id,
        "title": title,
        "content": content,
        "time": datetime.now(timezone.utc).isoformat(),
    }
    notes[next_id] = note
    next_id += 1
    return note


# POST /auth/login - verify credentials, return access token + set refresh cookie
@app.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json(silent=True)
    if not data:
        abort(400, description="Request body must be JSON")
    username = data.get("username", "").strip()
    password = data.get("password", "")
    if not username or not password:
        abort(400, description="'username' and 'password' are required")
    stored_hash = USERS.get(username)
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    if stored_hash is None or password_hash != stored_hash:
        abort(401, description="Invalid credentials")
    resp = make_response(jsonify({"access_token": issue_access_token(username)}), 200)
    set_refresh_cookie(resp, issue_refresh_token(username))
    return resp


# POST /auth/refresh - exchange a valid refresh-token cookie for a new access token
@app.route("/auth/refresh", methods=["POST"])
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
    return jsonify({"access_token": issue_access_token(entry["username"])}), 200


# POST /auth/logout - invalidate the refresh token and clear the cookie
@app.route("/auth/logout", methods=["POST"])
def logout():
    token = request.cookies.get("refresh_token")
    if token:
        refresh_tokens.pop(token, None)
    resp = make_response(jsonify({"message": "Logged out"}), 200)
    resp.set_cookie("refresh_token", "", max_age=0, httponly=True,
                    secure=COOKIE_SECURE, samesite="Strict", path="/auth")
    return resp


# GET /notes - list all notes
@app.route("/notes", methods=["GET"])
@require_auth
def get_notes():
    data = list(notes.values())
    etag = hashlib.md5(json.dumps(data, sort_keys=True).encode()).hexdigest()
    if request.headers.get("If-None-Match") == etag:
        return "", 304
    resp = make_response(jsonify(data), 200)
    resp.headers["Cache-Control"] = "private, max-age=5"
    resp.headers["ETag"] = etag
    return resp


# GET /notes/<id> - get a single note
@app.route("/notes/<int:note_id>", methods=["GET"])
@require_auth
def get_note(note_id):
    note = notes.get(note_id)
    if note is None:
        abort(404, description="Note not found")
    etag = note_etag(note)
    if request.headers.get("If-None-Match") == etag:
        return "", 304
    resp = make_response(jsonify(note), 200)
    resp.headers["Cache-Control"] = "private, max-age=5"
    resp.headers["ETag"] = etag
    return resp


# POST /notes - create a new note
@app.route("/notes", methods=["POST"])
@require_auth
def create_note():
    data = request.get_json(silent=True)
    if not data:
        abort(400, description="Request body must be JSON")
    title = data.get("title", "").strip()
    content = data.get("content", "").strip()
    if not title:
        abort(400, description="'title' is required")
    note = make_note(title, content)
    return jsonify(note), 201


# PATCH /notes/<id> - partially update a note
@app.route("/notes/<int:note_id>", methods=["PATCH"])
@require_auth
def patch_note(note_id):
    note = notes.get(note_id)
    if note is None:
        abort(404, description="Note not found")
    data = request.get_json(silent=True)
    if not data:
        abort(400, description="Request body must be JSON")
    if "title" in data:
        title = data["title"].strip()
        if not title:
            abort(400, description="'title' cannot be empty")
        note["title"] = title
    if "content" in data:
        note["content"] = data["content"].strip()
    note["time"] = datetime.now(timezone.utc).isoformat()
    return jsonify(note), 200


# DELETE /notes/<id> - delete a note
@app.route("/notes/<int:note_id>", methods=["DELETE"])
@require_auth
def delete_note(note_id):
    note = notes.pop(note_id, None)
    if note is None:
        abort(404, description="Note not found")
    return jsonify({"message": "Note deleted"}), 200


@app.errorhandler(400)
@app.errorhandler(401)
@app.errorhandler(404)
def handle_error(e):
    return jsonify({"error": str(e.description)}), e.code


if __name__ == "__main__":
    app.run(debug=True)
