#!/usr/bin/env bash
set -euo pipefail
URL="${LLM_ROUTER_URL:-http://127.0.0.1:18080}"
echo "=== Health ==="
curl -sf "$URL/health" | python3 -m json.tool
echo "=== Models ==="
curl -sf "$URL/v1/models" | python3 -m json.tool
echo "=== Chat ==="
curl -sf "$URL/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -H "X-LLM-Client: smoke-test" \
  -d '{"model":"default","messages":[{"role":"user","content":"Say OK."}]}' | python3 -m json.tool
