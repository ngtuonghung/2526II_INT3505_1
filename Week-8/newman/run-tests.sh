#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COLLECTION_FILE="$ROOT_DIR/postman/product-api.postman_collection.json"
DEFAULT_ENV_FILE="$ROOT_DIR/postman/local.postman_environment.json"
ENV_FILE="${1:-$DEFAULT_ENV_FILE}"
echo $ENV_FILE
REPORT_DIR="$ROOT_DIR/newman/reports"
REPORT_FILE="$REPORT_DIR/newman-report.json"

if ! command -v newman >/dev/null 2>&1; then
  echo "Error: newman is not installed."
  echo "Install with: npm install -g newman"
  exit 1
fi

if [[ ! -f "$COLLECTION_FILE" ]]; then
  echo "Error: collection file not found at $COLLECTION_FILE"
  exit 1
fi

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Error: environment file not found at $ENV_FILE"
  exit 1
fi

mkdir -p "$REPORT_DIR"

echo "Running Newman with:"
echo "- Collection: $COLLECTION_FILE"
echo "- Environment: $ENV_FILE"

time newman run "$COLLECTION_FILE" \
  -e "$ENV_FILE" \
  --reporters cli,json \
  --reporter-json-export "$REPORT_FILE"

echo "Report generated at: $REPORT_FILE"
