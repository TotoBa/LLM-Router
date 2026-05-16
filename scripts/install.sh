#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

echo "══════════════════════════════════════════"
echo "  LLM-Router Installation"
echo "══════════════════════════════════════════"
echo ""

# 1. Prüfe Python-Version
PYTHON="${PYTHON:-python3}"
if ! command -v "$PYTHON" >/dev/null 2>&1; then
    echo "✗ python3 nicht gefunden. Bitte installieren."
    exit 1
fi

PYVER=$($PYTHON -c 'import sys; print(sys.version_info[:2])')
echo "» Python-Version: $PYVER"

if ! $PYTHON -c 'import sys; assert sys.version_info >= (3,11)' 2>/dev/null; then
    echo "✗ Python ≥ 3.11 erforderlich."
    exit 1
fi

# 2. Virtualenv
echo ""
echo "» Erstelle Virtual Environment: .venv"
$PYTHON -m venv .venv
echo "  ✓ .venv erstellt"

# 3. Aktivieren + Installieren
echo ""
echo "» Installiere llm-router[dev]"
.venv/bin/pip install -e ".[dev]"
echo "  ✓ Installation abgeschlossen"

# 4. Beispielconfig kopieren
echo ""
echo "» Erstelle initiale Config"

if [ ! -f configs/router.local.yaml ]; then
    cp configs/router.example.yaml configs/router.local.yaml
    echo "  ✓ configs/router.local.yaml angelegt (bitte anpassen!)"
else
    echo "  → configs/router.local.yaml existiert bereits"
fi

if [ ! -f .env ]; then
    cp .env.example .env
    echo "  ✓ .env angelegt (bitte anpassen!)"
else
    echo "  → .env existiert bereits"
fi

# 5. Testen
echo ""
echo "» Konfiguration prüfen"
set -a
[ -f .env ] && . .env
set +a

if .venv/bin/llm-router check-config --config configs/router.local.yaml > /dev/null 2>&1; then
    echo "  ✓ Config ist syntaktisch gültig"
else
    echo "  ⚠ Config-Warnungen – bitte configs/router.local.yaml anpassen"
fi

echo ""
echo "──────────────────────────────────────────"
echo "  Installation abgeschlossen!"
echo ""
echo "  Nächste Schritte:"
echo "    1. nano configs/router.local.yaml"
echo "    2. nano .env"
echo "    3. .venv/bin/llm-router serve --config configs/router.local.yaml"
echo "    4. curl http://127.0.0.1:18080/health"
echo ""
echo "  Oder einfach: scripts/run-dev.sh"
echo "──────────────────────────────────────────"
