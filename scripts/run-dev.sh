#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

CONFIG="${1:-configs/router.local.yaml}"

if [ ! -f "$CONFIG" ]; then
    echo "» Config nicht gefunden: $CONFIG"
    echo "» Bitte erst kopieren: cp configs/router.example.yaml configs/router.local.yaml"
    exit 1
fi

# .env laden
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs -d '\n') || true
fi

echo "» Starte LLM-Router mit $CONFIG"
echo "» Logs gehen nach logs/llm-router.jsonl"
echo "» Ctrl+C zum Beenden"
echo ""

exec llm-router serve --config "$CONFIG"
