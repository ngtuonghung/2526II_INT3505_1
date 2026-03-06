from flask import Flask, request, jsonify, abort, make_response
from datetime import datetime, timezone

ONE_MONTH = 60 * 60 * 24 * 30  # 2592000 seconds

app = Flask(__name__)

notes = {}
next_id = 1


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
    resp = make_response(jsonify(list(notes.values())), 200)
    resp.headers["Cache-Control"] = f"private, max-age={ONE_MONTH}"
    return resp


# GET /notes/<id> - get a single note
@app.route("/notes/<int:note_id>", methods=["GET"])
def get_note(note_id):
    note = notes.get(note_id)
    if note is None:
        abort(404, description="Note not found")
    resp = make_response(jsonify(note), 200)
    resp.headers["Cache-Control"] = f"private, max-age={ONE_MONTH}"
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
