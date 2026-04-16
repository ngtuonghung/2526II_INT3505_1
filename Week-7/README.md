## Prerequisites

- Node.js with `@openapitools/openapi-generator-cli` installed globally (`npm install -g @openapitools/openapi-generator-cli`)
- Python 3.x virtualenv
- MongoDB running at `localhost:27017`

## Generate code from spec

```bash
openapi-generator-cli generate \
  -i spec.yaml \
  -g python-flask \
  -o server \
  --additional-properties=packageName=openapi_server,serverPort=8080
```

The generator overwrites the controller with stubs. Restore the MongoDB implementation:

```bash
cp products_controller.py server/openapi_server/controllers/products_controller.py
```

## Install dependencies

```bash
source ../venv/bin/activate
pip install -r server/requirements.txt
```

## Run the server

```bash
source ../venv/bin/activate
cd server
python -m openapi_server
```

The server listens at `http://localhost:8080`

Swagger UI: `http://localhost:8080/ui/`

## Endpoints

| Method | Path           | Description       |
|--------|----------------|-------------------|
| GET    | /products      | List all products |
| POST   | /products      | Create a product  |
| GET    | /products/{id} | Get product by id |
| PUT    | /products/{id} | Update a product  |
| DELETE | /products/{id} | Delete a product  |

## Example data

Start the shell:

```bash
mongosh
```

Then inside mongosh:

```js
use product_db

show collections

db.products.insertMany([
  { name: "T-shirt",  description: "100% cotton t-shirt",       price: 19.99, stock: 100, createdAt: new Date() },
  { name: "Jeans",    description: "Slim-fit denim jeans",       price: 49.99, stock: 60,  createdAt: new Date() },
  { name: "Sneakers", description: "Lightweight running shoes",  price: 89.99, stock: 35,  createdAt: new Date() }
])

db.products.find()
```

## Notes

- Product `id` is a 24-character hex string (MongoDB ObjectId).
- `createdAt` is assigned by the server on creation and must not be sent in the request body.
- MongoDB connection: `mongodb://localhost:27017/`, database `product_db`, collection `products`.