Install tools:
```bash
npm install -g @typespec/compiler @openapitools/openapi-generator-cli
```

Compile TypeSpec to OpenAPI:
```bash
tsp compile main.tsp --emit @typespec/openapi3
```

Optionally regenerate the Flask server from openapi.yaml:
```bash
cd tsp-output/schema
openapi-generator-cli generate -i openapi.yaml -g python-flask -o ./server --additional-properties=serverPort=8888,packageName=openapi_server
```

Run the server:
```bash
cd tsp-output/schema/server
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 -m openapi_server
```

Check:
- Swagger UI: http://localhost:8888/ui/
- OpenAPI JSON: http://localhost:8888/openapi.json