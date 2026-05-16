#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
CONFIG="${LLM_ROUTER_CONFIG:-configs/router.local.yaml}"
exec uvicorn llm_router.app:create_app --host 127.0.0.1 --port 18080 --reload || \
  exec python -m llm_router.cli serve --config "$CONFIG"
