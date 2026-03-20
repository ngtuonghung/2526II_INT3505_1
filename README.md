# 2526II_INT3505_1
Kiến trúc hướng dịch vụ

Swagger UI Demo: https://app.swaggerhub.com/apis/uet-363/book-management-system/1337

Production server: https://week-4-nu-two.vercel.app/

Request:
```plain
curl -X 'GET' \
  'https://week-4-nu-two.vercel.app/books?page=1' \
  -H 'accept: application/json'
```

Response:
```plain
[{"author":{"birth":1970,"id":1,"name":"Author One","numOfBooks":2},"cover":{},"description":"Intro to Flask","id":1,"numOfPages":200,"title":"Flask Basics","year":2020},{"author":{"birth":1970,"id":1,"name":"Author One","numOfBooks":2},"cover":{},"description":"Advanced Python","id":2,"numOfPages":350,"title":"Python Deep Dive","year":2021},{"author":{"birth":1985,"id":2,"name":"Author Two","numOfBooks":1},"cover":{},"description":"API best practices","id":3,"numOfPages":180,"title":"REST API Design","year":2022}]
```