import hashlib
import json
from datetime import datetime, timezone

from flask import Blueprint, abort, jsonify, make_response, request

from services.user_auth import require_auth

notes_bp = Blueprint("notes_v1", __name__)

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
        "time": datetime.now(timezone.utc).isoformat(),
    }
    notes[next_id] = note
    next_id += 1
    return note


@notes_bp.route("", methods=["GET"])
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


@notes_bp.route("/<int:note_id>", methods=["GET"])
@require_auth
def get_note(note_id):
    note = notes.get(note_id)
    if note is None:
        abort(404, description="Note not found")
    etag = _note_etag(note)
    if request.headers.get("If-None-Match") == etag:
        return "", 304
    resp = make_response(jsonify(note), 200)
    resp.headers["Cache-Control"] = "private, max-age=5"
    resp.headers["ETag"] = etag
    return resp


@notes_bp.route("", methods=["POST"])
@require_auth
def create_note():
    data = request.get_json(silent=True)
    if not data:
        abort(400, description="Request body must be JSON")
    title = data.get("title", "").strip()
    content = data.get("content", "").strip()
    if not title:
        abort(400, description="'title' is required")
    note = _make_note(title, content)
    return jsonify(note), 201


@notes_bp.route("/<int:note_id>", methods=["PATCH"])
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


@notes_bp.route("/<int:note_id>", methods=["DELETE"])
@require_auth
def delete_note(note_id):
    note = notes.pop(note_id, None)
    if note is None:
        abort(404, description="Note not found")
    return jsonify({"message": "Note deleted"}), 200
