#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

CONFIG="${1:-configs/router.local.yaml}"

echo "» Prüfe $CONFIG"

if [ ! -f "$CONFIG" ]; then
    echo "✗ Config nicht gefunden: $CONFIG"
    echo "  Tipp: cp configs/router.example.yaml $CONFIG"
    exit 1
fi

# .env laden, falls vorhanden
if [ -f .env ]; then
    set -a
    . .env
    set +a
fi

llm-router check-config --config "$CONFIG"
