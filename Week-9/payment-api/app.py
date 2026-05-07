from flask import Flask, jsonify, send_from_directory

from routes.v1.payments import payments_v1
from routes.v2.payments import payments_v2


def create_app():
    app = Flask(__name__)

    app.register_blueprint(payments_v1, url_prefix="/api/v1")
    app.register_blueprint(payments_v2, url_prefix="/api/v2")

    @app.get("/")
    def index():
        return jsonify(
            {
                "message": "Payment API versioning demo",
                "versions": ["/api/v1/payments", "/api/v2/payments"],
                "openapi": "/openapi.yaml",
            }
        )

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"})

    @app.get("/openapi.yaml")
    def openapi_spec():
        return send_from_directory(app.root_path, "openapi.yaml")

    return app


if __name__ == "__main__":
    create_app().run(debug=True)
