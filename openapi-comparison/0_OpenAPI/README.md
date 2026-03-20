## Tạo mã Python Client

Tải Docker image OpenAPI Generator:
```bash
docker pull openapitools/openapi-generator-cli
```

Tạo Python client từ OpenAPI spec:
```bash
docker run --rm \
  -v "${PWD}:/local" \
  openapitools/openapi-generator-cli generate \
  -i /local/api.yaml \
  -g python \
  -o /local/app
```

Lệnh này sẽ tạo Python client library trong thư mục `app/`.

## Cài đặt

Sửa quyền truy cập thư mục (do Docker tạo với quyền root):
```bash
sudo chown -R $USER:$USER app/
```

Tạo virtual environment:
```bash
cd app
python3 -m venv venv
source venv/bin/activate
```

Cài đặt client đã tạo:
```bash
pip install -e .
```

## Sử dụng API

Ví dụ đơn giản - lấy sách theo ID:
```python
import openapi_client

configuration = openapi_client.Configuration(host="http://127.0.0.1:5000/v1")

with openapi_client.ApiClient(configuration) as api_client:
    api_instance = openapi_client.BooksApi(api_client)
    book = api_instance.get_book(book_id=1)
    print(book)
```
