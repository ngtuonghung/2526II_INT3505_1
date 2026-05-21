# Week-11: Microservice API Design Patterns

Microservice Flask nhỏ để demo kết hợp CRUD, HATEOAS, Event-Driven và Web Hook. Dữ liệu lưu in-memory nên sẽ mất khi restart container.

## Chạy bằng Docker

```bash
docker build -t week11-api-design-demo Week-11
docker run --rm -p 5000:5000 week11-api-design-demo
```

API chạy tại `http://localhost:5000`.

## Chạy local không dùng Docker

```bash
cd Week-11
pip install -r requirements.txt
python app.py
```

## Endpoint chính

| Method | Path | Mô tả |
|--------|------|-------|
| GET | `/` | Root API có HATEOAS links |
| GET | `/health` | Kiểm tra service |
| GET | `/orders` | Danh sách order |
| POST | `/orders` | Tạo order |
| GET | `/orders/<id>` | Chi tiết order |
| PATCH | `/orders/<id>` | Cập nhật order |
| DELETE | `/orders/<id>` | Xóa order |
| GET | `/events` | Event log nội bộ |
| POST | `/webhooks` | Đăng ký webhook |
| GET | `/webhooks` | Danh sách webhook |
| DELETE | `/webhooks/<id>` | Xóa webhook |
| POST | `/mock-webhook` | Receiver demo trong cùng service |
| GET | `/mock-webhook/events` | Xem webhook đã nhận |

## Demo nhanh

Kiểm tra root API và HATEOAS links:

```bash
curl -s http://localhost:5000/ | python3 -m json.tool
```

Đăng ký webhook trỏ tới mock receiver:

```bash
curl -s -X POST http://localhost:5000/webhooks \
  -H "Content-Type: application/json" \
  -d '{"url":"http://localhost:5000/mock-webhook","secret":"demo-secret"}' \
  | python3 -m json.tool
```

Tạo order:

```bash
curl -s -X POST http://localhost:5000/orders \
  -H "Content-Type: application/json" \
  -d '{"customer_name":"Alice","item":"Keyboard","quantity":2}' \
  | python3 -m json.tool
```

Cập nhật order:

```bash
ORDER_ID="<id-tu-response-tao-order>"

curl -s -X PATCH http://localhost:5000/orders/$ORDER_ID \
  -H "Content-Type: application/json" \
  -d '{"status":"paid"}' \
  | python3 -m json.tool
```

Xóa order:

```bash
curl -s -X DELETE http://localhost:5000/orders/$ORDER_ID | python3 -m json.tool
```

Xem event nội bộ:

```bash
curl -s http://localhost:5000/events | python3 -m json.tool
```

Xem webhook receiver đã nhận gì:

```bash
curl -s http://localhost:5000/mock-webhook/events | python3 -m json.tool
```

Trong dữ liệu mock webhook sẽ có header `X-Webhook-Signature` nếu webhook được đăng ký kèm `secret`.

## Pattern được demo

- CRUD: quản lý vòng đời `orders`.
- HATEOAS: response có `_links` để client biết action tiếp theo.
- Event-Driven: mỗi thay đổi order tạo event `order.created`, `order.updated`, `order.deleted`.
- Web Hook: service tự POST event tới URL đã đăng ký, có HMAC signature và retry tối đa 2 lần.
