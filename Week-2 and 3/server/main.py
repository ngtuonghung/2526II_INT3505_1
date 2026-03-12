from flask import Flask, jsonify
from flask_cors import CORS

from api.v1.notes import notes_bp as notes_bp_v1
from api.v2.notes import notes_bp as notes_bp_v2
from services.user_auth import auth_bp

app = Flask(__name__)

CORS_ORIGINS = [
    "http://127.0.0.1:5500",
    "http://127.0.0.1:3000",
]
CORS(app, supports_credentials=True, origins=CORS_ORIGINS)

app.register_blueprint(auth_bp)
app.register_blueprint(notes_bp_v1, url_prefix="/api/v1/notes")
app.register_blueprint(notes_bp_v2, url_prefix="/api/v2/notes")


@app.errorhandler(400)
@app.errorhandler(401)
@app.errorhandler(404)
def handle_error(e):
    return jsonify({"error": str(e.description)}), e.code


if __name__ == "__main__":
    app.run(debug=True)
