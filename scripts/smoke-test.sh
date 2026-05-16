#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

HOST="${LLM_ROUTER_HOST:-127.0.0.1}"
PORT="${LLM_ROUTER_PORT:-18080}"
BASE="http://${HOST}:${PORT}"
MODEL="${1:-default}"
PROMPT="${2:-Antworte nur 'OK'.}"

echo "» Smoke-Test gegen $BASE"
echo "» Modell: $MODEL"
echo "» Prompt: $PROMPT"
echo ""

# 1. Health
echo "» GET /health"
HEALTH=$(curl -fsS "$BASE/health")
echo "  ok: $(echo "$HEALTH" | jq -r '.ok')"
echo "  version: $(echo "$HEALTH" | jq -r '.version')"
echo "  models: $(echo "$HEALTH" | jq -r '.models | @tsv')"
echo ""

# 2. Models
echo "» GET /v1/models"
echo "  Models:"
curl -fsS "$BASE/v1/models" | jq -r '.data[].id' | sed 's/^/    - /'
echo ""

# 3. Chat – mit Header-Ausgabe über temp files
TMPOUT=$(mktemp)
TMPHDR=$(mktemp)

echo "» POST /v1/chat/completions"
curl -fsS -D "$TMPHDR" -X POST "$BASE/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -H "X-LLM-Client: smoke-test" \
  -d "{\"model\":\"$MODEL\",\"messages\":[{\"role\":\"user\",\"content\":\"$PROMPT\"}]}" \
  -o "$TMPOUT"

# Header extrahieren
echo "  Router-Header:"
grep -i 'x-llm-router' "$TMPHDR" | sed 's/^/    /' || echo "    (keine)"
echo ""

echo "  Antwort: $(jq -r '.choices[0].message.content // empty | tostring | .[0:100]' "$TMPOUT")"
echo ""

rm -f "$TMPOUT" "$TMPHDR"

echo "✓ Smoke-Test erfolgreich"
