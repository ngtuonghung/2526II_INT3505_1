# Week 9 - API Versioning & Lifecycle Management

Demo một Payment API nhỏ bằng Flask để minh họa:

- API versioning bằng URL: `/api/v1` và `/api/v2`
- Deprecation thông qua response headers
- OpenAPI spec cho cả 2 version

## Project Structure

```text
payment-api/
├── app.py
├── routes/
│   ├── v1/payments.py
│   └── v2/payments.py
├── services/
│   └── payment_service.py
└── openapi.yaml
```

## Setup

Chạy từ thư mục root của repo:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

## Run

```bash
cd Week-9/payment-api
../../.venv/bin/python app.py
```

Server:

```text
http://localhost:5000
```

OpenAPI spec:

```text
http://localhost:5000/openapi.yaml
```

## API Demo

### V1 - Deprecated

Tạo payment:

```bash
curl -i -X POST http://localhost:5000/api/v1/payments \
  -H "Content-Type: application/json" \
  -d '{"amount":"100.00","description":"Book order"}'
```

Lấy payment:

```bash
curl -i http://localhost:5000/api/v1/payments/pay_1
```

V1 trả response format cũ, trong đó `amount` là string:

```json
{
  "id": "pay_1",
  "amount": "100.00",
  "description": "Book order",
  "status": "created"
}
```

V1 có deprecation headers:

```text
Deprecation: true
Warning: 299 - "API v1 is deprecated and will be removed on 2026-12-31. Please migrate to /api/v2/payments"
```

### V2 - Current

Tạo payment:

```bash
curl -i -X POST http://localhost:5000/api/v2/payments \
  -H "Content-Type: application/json" \
  -d '{"amount":100.0,"currency":"USD","description":"Book order","idempotency_key":"abc-123"}'
```

Lấy payment:

```bash
curl -i http://localhost:5000/api/v2/payments/pay_2
```

V2 trả response format mới, trong đó `amount` là number và có thêm `currency`, `idempotency_key`:

```json
{
  "id": "pay_2",
  "amount": 100.0,
  "currency": "USD",
  "description": "Book order",
  "status": "created",
  "idempotency_key": "abc-123"
}
```

V2 không có deprecation headers.
