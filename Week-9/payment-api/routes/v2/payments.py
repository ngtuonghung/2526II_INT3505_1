from flask import Blueprint, jsonify, request

from services.payment_service import create_payment, get_payment


payments_v2 = Blueprint("payments_v2", __name__)


@payments_v2.post("/payments")
def create_payment_v2():
    data = request.get_json(silent=True) or {}

    payment = create_payment(
        amount=data.get("amount", 0),
        currency=data.get("currency", "USD"),
        description=data.get("description", ""),
        idempotency_key=data.get("idempotency_key"),
    )

    return jsonify(to_v2_response(payment)), 201


@payments_v2.get("/payments/<payment_id>")
def get_payment_v2(payment_id):
    payment = get_payment(payment_id)
    if payment is None:
        return jsonify({"error": "Payment not found"}), 404

    return jsonify(to_v2_response(payment))


def to_v2_response(payment):
    return {
        "id": payment["id"],
        "amount": float(payment["amount"]),
        "currency": payment["currency"],
        "description": payment["description"],
        "status": payment["status"],
        "idempotency_key": payment["idempotency_key"],
    }
