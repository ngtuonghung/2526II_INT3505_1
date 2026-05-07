from decimal import Decimal, InvalidOperation


payments = {}
next_payment_number = 1


def create_payment(amount, description="", currency="USD", idempotency_key=None):
    global next_payment_number

    payment_id = f"pay_{next_payment_number}"
    next_payment_number += 1

    payment = {
        "id": payment_id,
        "amount": _to_decimal(amount),
        "currency": currency,
        "description": description,
        "status": "created",
        "idempotency_key": idempotency_key,
    }
    payments[payment_id] = payment
    return payment


def get_payment(payment_id):
    return payments.get(payment_id)


def _to_decimal(value):
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return Decimal("0")
