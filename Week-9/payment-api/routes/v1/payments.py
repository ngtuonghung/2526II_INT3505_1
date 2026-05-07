from flask import Blueprint, jsonify, request

from services.payment_service import create_payment, get_payment


payments_v1 = Blueprint("payments_v1", __name__)


@payments_v1.post("/payments")
def create_payment_v1():
    data = request.get_json(silent=True) or {}

    payment = create_payment(
        amount=data.get("amount", "0"),
        description=data.get("description", ""),
    )

    return jsonify(to_v1_response(payment)), 201


@payments_v1.get("/payments/<payment_id>")
def get_payment_v1(payment_id):
    payment = get_payment(payment_id)
    if payment is None:
        return jsonify({"error": "Payment not found"}), 404

    response = jsonify(to_v1_response(payment))
    response.headers["Deprecation"] = "true"
    response.headers["Warning"] = '299 - "API v1 is deprecated and will be removed on 2026-12-31. Please migrate to /api/v2/payments"'
    return response


def to_v1_response(payment):
    return {
        "id": payment["id"],
        "amount": f"{payment['amount']:.2f}",
        "description": payment["description"],
        "status": payment["status"],
    }
