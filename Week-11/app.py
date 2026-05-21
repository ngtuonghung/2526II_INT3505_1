import hashlib
import hmac
import json
import time
import uuid
from datetime import datetime, timezone

import requests
from flask import Flask, jsonify, request


app = Flask(__name__)

# Store in-memory để demo tối giản, dữ liệu mất khi restart app/container.
orders = {}
events = []
webhooks = {}
mock_webhook_events = []

MAX_EVENTS = 100
WEBHOOK_RETRIES = 2
WEBHOOK_TIMEOUT = 2


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def link(href, method):
    return {"href": href, "method": method}


# Các hàm *_links tạo HATEOAS links để client biết action tiếp theo.
def order_links(order_id):
    return {
        "self": link(f"/orders/{order_id}", "GET"),
        "collection": link("/orders", "GET"),
        "update": link(f"/orders/{order_id}", "PATCH"),
        "delete": link(f"/orders/{order_id}", "DELETE"),
    }


def serialize_order(order):
    return {**order, "_links": order_links(order["id"])}


def event_links(event_id):
    return {
        "self": link(f"/events/{event_id}", "GET"),
        "collection": link("/events", "GET"),
    }


def serialize_event(event):
    return {**event, "_links": event_links(event["id"])}


def webhook_links(webhook_id):
    return {
        "self": link(f"/webhooks/{webhook_id}", "GET"),
        "collection": link("/webhooks", "GET"),
        "delete": link(f"/webhooks/{webhook_id}", "DELETE"),
    }


def serialize_webhook(webhook):
    # Không trả secret ra response, chỉ báo webhook có secret hay không.
    public_webhook = {
        "id": webhook["id"],
        "url": webhook["url"],
        "has_secret": bool(webhook.get("secret")),
        "created_at": webhook["created_at"],
    }
    return {**public_webhook, "_links": webhook_links(webhook["id"])}


def sign_payload(payload, secret):
    # Ký payload bằng HMAC SHA-256 để receiver kiểm tra nguồn webhook.
    body = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    digest = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    return f"sha256={digest}"


def deliver_webhook(webhook, event):
    # Gửi event tới từng webhook đã đăng ký, kèm metadata qua headers.
    payload = serialize_event(event)
    headers = {
        "Content-Type": "application/json",
        "X-Event-Type": event["type"],
        "X-Event-Id": event["id"],
    }

    if webhook.get("secret"):
        headers["X-Webhook-Signature"] = sign_payload(payload, webhook["secret"])

    last_error = None
    for attempt in range(1, WEBHOOK_RETRIES + 1):
        try:
            # Retry ngắn giúp demo webhook delivery thực tế hơn nhưng vẫn minimal.
            response = requests.post(
                webhook["url"],
                json=payload,
                headers=headers,
                timeout=WEBHOOK_TIMEOUT,
            )
            if 200 <= response.status_code < 300:
                return {
                    "webhook_id": webhook["id"],
                    "url": webhook["url"],
                    "status": "delivered",
                    "attempts": attempt,
                    "status_code": response.status_code,
                }
            last_error = f"HTTP {response.status_code}"
        except requests.RequestException as exc:
            last_error = str(exc)

        if attempt < WEBHOOK_RETRIES:
            time.sleep(0.2)

    return {
        "webhook_id": webhook["id"],
        "url": webhook["url"],
        "status": "failed",
        "attempts": WEBHOOK_RETRIES,
        "error": last_error,
    }


def publish_event(event_type, data):
    # Event-Driven: mọi thay đổi order tạo event và fan-out tới webhooks.
    event = {
        "id": str(uuid.uuid4()),
        "type": event_type,
        "data": data,
        "created_at": now_iso(),
        "deliveries": [],
    }

    for webhook in list(webhooks.values()):
        event["deliveries"].append(deliver_webhook(webhook, event))

    events.append(event)
    del events[:-MAX_EVENTS]
    return event


def validate_order_payload(data, partial=False):
    # Dùng chung cho POST và PATCH; partial=True cho phép cập nhật một phần.
    if not isinstance(data, dict):
        return "JSON body is required"

    allowed_fields = {"customer_name", "item", "quantity", "status"}
    unknown_fields = set(data) - allowed_fields
    if unknown_fields:
        return f"Unknown fields: {', '.join(sorted(unknown_fields))}"

    required_fields = {"customer_name", "item", "quantity"}
    if not partial:
        missing = [field for field in required_fields if field not in data]
        if missing:
            return f"Missing fields: {', '.join(missing)}"

    if "customer_name" in data and not str(data["customer_name"]).strip():
        return "customer_name must not be empty"
    if "item" in data and not str(data["item"]).strip():
        return "item must not be empty"
    if "quantity" in data:
        try:
            quantity = int(data["quantity"])
        except (TypeError, ValueError):
            return "quantity must be an integer"
        if quantity <= 0:
            return "quantity must be greater than 0"
    if "status" in data:
        valid_statuses = {"pending", "paid", "shipped", "cancelled"}
        if data["status"] not in valid_statuses:
            return f"status must be one of: {', '.join(sorted(valid_statuses))}"

    return None


@app.get("/")
def index():
    # Root endpoint công bố các resource chính bằng HATEOAS links.
    return jsonify(
        {
            "message": "Week-11 API Design Patterns Demo",
            "patterns": ["CRUD", "HATEOAS", "Event-Driven", "Web Hook"],
            "_links": {
                "orders": link("/orders", "GET"),
                "webhooks": link("/webhooks", "GET"),
                "events": link("/events", "GET"),
                "health": link("/health", "GET"),
            },
        }
    )


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.get("/orders")
def list_orders():
    # CRUD - Read collection.
    return jsonify(
        {
            "count": len(orders),
            "items": [serialize_order(order) for order in orders.values()],
            "_links": {
                "self": link("/orders", "GET"),
                "create": link("/orders", "POST"),
            },
        }
    )


@app.post("/orders")
def create_order():
    # CRUD - Create, sau đó phát event order.created.
    data = request.get_json(silent=True)
    error = validate_order_payload(data)
    if error:
        return jsonify({"error": error}), 400

    order_id = str(uuid.uuid4())
    order = {
        "id": order_id,
        "customer_name": str(data["customer_name"]).strip(),
        "item": str(data["item"]).strip(),
        "quantity": int(data["quantity"]),
        "status": data.get("status", "pending"),
        "created_at": now_iso(),
        "updated_at": now_iso(),
    }
    orders[order_id] = order

    event = publish_event("order.created", serialize_order(order))
    response = jsonify({"order": serialize_order(order), "event": serialize_event(event)})
    response.status_code = 201
    response.headers["Location"] = f"/orders/{order_id}"
    return response


@app.get("/orders/<order_id>")
def get_order(order_id):
    order = orders.get(order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404
    return jsonify(serialize_order(order))


@app.patch("/orders/<order_id>")
def update_order(order_id):
    # CRUD - Update một phần, sau đó phát event order.updated.
    order = orders.get(order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404

    data = request.get_json(silent=True)
    error = validate_order_payload(data, partial=True)
    if error:
        return jsonify({"error": error}), 400
    if not data:
        return jsonify({"error": "At least one field is required"}), 400

    if "customer_name" in data:
        order["customer_name"] = str(data["customer_name"]).strip()
    if "item" in data:
        order["item"] = str(data["item"]).strip()
    if "quantity" in data:
        order["quantity"] = int(data["quantity"])
    if "status" in data:
        order["status"] = data["status"]
    order["updated_at"] = now_iso()

    event = publish_event("order.updated", serialize_order(order))
    return jsonify({"order": serialize_order(order), "event": serialize_event(event)})


@app.delete("/orders/<order_id>")
def delete_order(order_id):
    # CRUD - Delete, vẫn trả order đã xóa để demo event payload.
    order = orders.pop(order_id, None)
    if not order:
        return jsonify({"error": "Order not found"}), 404

    event = publish_event("order.deleted", serialize_order(order))
    return jsonify({"deleted": True, "order": serialize_order(order), "event": serialize_event(event)})


@app.get("/events")
def list_events():
    # Event log nội bộ giúp quan sát pattern Event-Driven khi demo.
    return jsonify(
        {
            "count": len(events),
            "items": [serialize_event(event) for event in events],
            "_links": {"self": link("/events", "GET")},
        }
    )


@app.get("/events/<event_id>")
def get_event(event_id):
    event = next((item for item in events if item["id"] == event_id), None)
    if not event:
        return jsonify({"error": "Event not found"}), 404
    return jsonify(serialize_event(event))


@app.get("/webhooks")
def list_webhooks():
    return jsonify(
        {
            "count": len(webhooks),
            "items": [serialize_webhook(webhook) for webhook in webhooks.values()],
            "_links": {
                "self": link("/webhooks", "GET"),
                "create": link("/webhooks", "POST"),
            },
        }
    )


@app.post("/webhooks")
def create_webhook():
    # Web Hook subscription: client đăng ký URL nhận event.
    data = request.get_json(silent=True) or {}
    url = str(data.get("url", "")).strip()
    secret = str(data.get("secret", "")).strip()

    if not url:
        return jsonify({"error": "url is required"}), 400
    if not (url.startswith("http://") or url.startswith("https://")):
        return jsonify({"error": "url must start with http:// or https://"}), 400

    webhook_id = str(uuid.uuid4())
    webhook = {
        "id": webhook_id,
        "url": url,
        "secret": secret,
        "created_at": now_iso(),
    }
    webhooks[webhook_id] = webhook

    response = jsonify(serialize_webhook(webhook))
    response.status_code = 201
    response.headers["Location"] = f"/webhooks/{webhook_id}"
    return response


@app.get("/webhooks/<webhook_id>")
def get_webhook(webhook_id):
    webhook = webhooks.get(webhook_id)
    if not webhook:
        return jsonify({"error": "Webhook not found"}), 404
    return jsonify(serialize_webhook(webhook))


@app.delete("/webhooks/<webhook_id>")
def delete_webhook(webhook_id):
    webhook = webhooks.pop(webhook_id, None)
    if not webhook:
        return jsonify({"error": "Webhook not found"}), 404
    return jsonify({"deleted": True, "webhook": serialize_webhook(webhook)})


@app.post("/mock-webhook")
def mock_webhook():
    # Receiver giả lập để demo webhook trong cùng một container.
    received = {
        "id": str(uuid.uuid4()),
        "received_at": now_iso(),
        "headers": {
            "X-Event-Type": request.headers.get("X-Event-Type"),
            "X-Event-Id": request.headers.get("X-Event-Id"),
            "X-Webhook-Signature": request.headers.get("X-Webhook-Signature"),
        },
        "payload": request.get_json(silent=True),
    }
    mock_webhook_events.append(received)
    del mock_webhook_events[:-MAX_EVENTS]
    return jsonify({"received": True, "event_id": received["headers"]["X-Event-Id"]}), 202


@app.get("/mock-webhook/events")
def list_mock_webhook_events():
    return jsonify(
        {
            "count": len(mock_webhook_events),
            "items": mock_webhook_events,
            "_links": {
                "self": link("/mock-webhook/events", "GET"),
                "receiver": link("/mock-webhook", "POST"),
            },
        }
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True, threaded=True)
