#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
CONFIG="${1:-configs/router.local.yaml}"
exec llm-router check-config --config "$CONFIG"
