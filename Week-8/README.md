# Week-8 API test guide

## Setup
Requirements:
- MongoDB running locally at `mongodb://localhost:27017`
- API server running at `http://localhost:8080`
- Node.js and Newman

Install Newman:
```bash
npm install -g newman
```

Run the API server:
```bash
cd server
pip install -r requirements.txt
python3 -m openapi_server
```

## Run
From the `Week-8` directory:
```bash
chmod +x newman/run-tests.sh
./newman/run-tests.sh
```

Use a different environment file:
```bash
./newman/run-tests.sh postman/local.postman_environment.json
```

## Scope
Collection: `postman/product-api.postman_collection.json`
Environment local: `postman/local.postman_environment.json`

Test suite covers:
- GET /products: 200
- POST /products: 201 and 400
- GET /products/{id}: 200, 400, 404
- PUT /products/{id}: 200, 400
- DELETE /products/{id}: 204, 404, 400