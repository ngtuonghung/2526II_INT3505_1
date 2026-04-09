from flask import Flask, jsonify
from flask_cors import CORS

from services.user_auth import auth_bp

app = Flask(__name__)

CORS_ORIGINS = [
    "http://127.0.0.1:5500",
    "http://localhost:5500",
    "http://100.98.1.54:5500",
]
CORS(app, supports_credentials=True, origins=CORS_ORIGINS)

app.register_blueprint(auth_bp, url_prefix="/auth")


@app.errorhandler(400)
@app.errorhandler(401)
@app.errorhandler(403)
@app.errorhandler(404)
def handle_error(e):
    return jsonify({"error": str(e.description)}), e.code


if __name__ == "__main__":
    app.run(debug=True)
