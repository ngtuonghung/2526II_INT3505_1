import hashlib
import json
import os
from functools import wraps
from flask import Flask, request, jsonify, abort, make_response
from flask_cors import CORS
from datetime import datetime, timezone, timedelta
import jwt  # PyJWT

app = Flask(__name__)
CORS(app)

# ── JWT config ────────────────────────────────────────────────────────────────
JWT_SECRET = os.environ.get("JWT_SECRET", "2526II_INT3505_1_SECRET")
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_HOURS = 1

USERS = {
    "admin": "240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9",
}

notes = {}
next_id = 1


def note_etag(note):
    return hashlib.md5(json.dumps(note, sort_keys=True).encode()).hexdigest()


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


# POST /auth/login - exchange credentials for a JWT
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
    # Use constant-time comparison path: always hash before comparing
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    if stored_hash is None or password_hash != stored_hash:
        abort(401, description="Invalid credentials")
    exp = datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRY_HOURS)
    token = jwt.encode(
        {"sub": username, "exp": exp},
        JWT_SECRET,
        algorithm=JWT_ALGORITHM,
    )
    return jsonify({"token": token}), 200


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
