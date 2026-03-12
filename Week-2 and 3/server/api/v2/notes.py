import base64
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from flask import Blueprint, abort, jsonify, make_response, request

from services.user_auth import require_auth

notes_bp = Blueprint("notes_v2", __name__)

UPLOAD_DIR = Path(__file__).parent / "uploads"
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
EXT_MAP = {"image/jpeg": ".jpg", "image/png": ".png", "image/gif": ".gif", "image/webp": ".webp"}

notes = {}
next_id = 1


def _note_etag(note):
    return hashlib.md5(json.dumps(note, sort_keys=True).encode()).hexdigest()


def _make_note(title, content):
    global next_id
    note = {
        "id": next_id,
        "title": title,
        "content": content,
        "has_image": False,
        "time": datetime.now(timezone.utc).isoformat(),
    }
    notes[next_id] = note
    next_id += 1
    return note


def _image_path(note_id):
    for ext in EXT_MAP.values():
        p = UPLOAD_DIR / f"{note_id}{ext}"
        if p.exists():
            return p
    return None


def _image_data_url(note_id):
    img = _image_path(note_id)
    if img is None:
        return None
    ext_to_mime = {v: k for k, v in EXT_MAP.items()}
    mime = ext_to_mime.get(img.suffix, "image/jpeg")
    data = base64.b64encode(img.read_bytes()).decode()
    return f"data:{mime};base64,{data}"


def _with_image_data(note):
    if not note.get("has_image"):
        return note
    data_url = _image_data_url(note["id"])
    if data_url:
        return {**note, "image_data": data_url}
    return note


@notes_bp.route("", methods=["GET"])
@require_auth
def get_notes():
    raw = list(notes.values())
    etag = hashlib.md5(json.dumps(raw, sort_keys=True).encode()).hexdigest()
    if request.headers.get("If-None-Match") == etag:
        return "", 304
    data = [_with_image_data(n) for n in raw]
    resp = make_response(jsonify(data), 200)
    resp.headers["Cache-Control"] = "private, max-age=5"
    resp.headers["ETag"] = etag
    return resp


@notes_bp.route("/<int:note_id>", methods=["GET"])
@require_auth
def get_note(note_id):
    note = notes.get(note_id)
    if note is None:
        abort(404, description="Note not found")
    etag = _note_etag(note)
    if request.headers.get("If-None-Match") == etag:
        return "", 304
    resp = make_response(jsonify(_with_image_data(note)), 200)
    resp.headers["Cache-Control"] = "private, max-age=5"
    resp.headers["ETag"] = etag
    return resp


@notes_bp.route("", methods=["POST"])
@require_auth
def create_note():
    title = request.form.get("title", "").strip()
    content = request.form.get("content", "").strip()
    if not title:
        abort(400, description="'title' is required")
    note = _make_note(title, content)
    image = request.files.get("image")
    if image:
        if image.content_type not in ALLOWED_TYPES:
            notes.pop(note["id"])
            abort(400, description="Unsupported image type")
        ext = EXT_MAP[image.content_type]
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        image.save(UPLOAD_DIR / f"{note['id']}{ext}")
        note["has_image"] = True
    return jsonify(note), 201


@notes_bp.route("/<int:note_id>", methods=["PATCH"])
@require_auth
def patch_note(note_id):
    note = notes.get(note_id)
    if note is None:
        abort(404, description="Note not found")
    if request.content_type and "multipart" in request.content_type:
        data = request.form
        image = request.files.get("image")
    else:
        data = request.get_json(silent=True) or {}
        image = None
    if not data and image is None:
        abort(400, description="Request body must be multipart/form-data or JSON")
    if "title" in data:
        title = data["title"].strip()
        if not title:
            abort(400, description="'title' cannot be empty")
        note["title"] = title
    if "content" in data:
        note["content"] = data["content"].strip()
    if image:
        if image.content_type not in ALLOWED_TYPES:
            abort(400, description="Unsupported image type")
        old = _image_path(note_id)
        if old:
            old.unlink(missing_ok=True)
        ext = EXT_MAP[image.content_type]
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        image.save(UPLOAD_DIR / f"{note_id}{ext}")
        note["has_image"] = True
    note["time"] = datetime.now(timezone.utc).isoformat()
    return jsonify(note), 200


@notes_bp.route("/<int:note_id>", methods=["DELETE"])
@require_auth
def delete_note(note_id):
    note = notes.pop(note_id, None)
    if note is None:
        abort(404, description="Note not found")
    img = _image_path(note_id)
    if img:
        img.unlink(missing_ok=True)
    return jsonify({"message": "Note deleted"}), 200