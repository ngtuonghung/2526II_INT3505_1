import hashlib
import json
from flask import Flask, request, jsonify, abort, make_response
from flask_cors import CORS
from datetime import datetime, timezone

app = Flask(__name__)
CORS(app)

notes = {}
next_id = 1


def note_etag(note):
    return hashlib.md5(json.dumps(note, sort_keys=True).encode()).hexdigest()


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


# GET /notes - list all notes
@app.route("/notes", methods=["GET"])
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
def delete_note(note_id):
    note = notes.pop(note_id, None)
    if note is None:
        abort(404, description="Note not found")
    return jsonify({"message": "Note deleted"}), 200


@app.errorhandler(400)
@app.errorhandler(404)
def handle_error(e):
    return jsonify({"error": str(e.description)}), e.code


if __name__ == "__main__":
    app.run(debug=True)
