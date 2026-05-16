# Schachsystem-Anbindung

## Prinzip

Das Schachsystem spricht nicht direkt mit Ollama. Es spricht nur mit dem Router.

Das Schachsystem kennt:
- logische Rollen (`router`, `small`, `large`, `task`)
- Modell-Aliase (`chess-router`, `chess-small`, `chess-large`, `chess-task`)

Es weiß **nicht**, welches echte Modell dahinter steht und ob es lokal oder auf dem Pi läuft.

## Env-Konfiguration im Schachsystem

```env
LLM_BASE_URL=http://ROUTER_VM_IP:18080/v1
LLM_API_KEY=ollama

LLM_MODEL_ROUTER=chess-router
LLM_MODEL_SMALL=chess-small
LLM_MODEL_LARGE=chess-large
LLM_MODEL_TASK=chess-task
```

## Modellzuordnung

| Rolle | Modell-Alias | Provider-Modell | Zweck |
|---|---|---|---|
| router | `chess-router` | `deepseek-v4-flash:cloud` | Aufgabenklasse, Analyseweg |
| small | `chess-small` | `deepseek-v4-flash:cloud` | Klassifikation, Zugbewertung |
| large | `chess-large` | `gemma4:31b-cloud` | Lange Analyse, Kommentierung |
| task | `chess-task` | `deepseek-v4-pro:cloud` | PGN-Kommentare, Zusammenfassungen |

Diese Zuordnung lebt **nur im Router** – das Schachsystem fragt einfach `chess-small` und bekommt eine Antwort.

## Router-Konfiguration für Chess

```yaml
models:
  chess-router:
    provider_model: "deepseek-v4-flash:cloud"
    backends: ["vm", "pi"]
    policy: "standard"

  chess-small:
    provider_model: "deepseek-v4-flash:cloud"
    backends: ["vm", "pi"]
    policy: "standard"

  chess-large:
    provider_model: "gemma4:31b-cloud"
    backends: ["vm", "pi"]
    policy: "long_running"

  chess-task:
    provider_model: "deepseek-v4-pro:cloud"
    backends: ["vm", "pi"]
    policy: "standard"
```

## Test

```bash
# Direkter Test via curl
curl -s http://ROUTER_VM_IP:18080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "X-LLM-Client: chess-system" \
  -d '{
    "model": "chess-small",
    "messages": [{"role":"user","content":"Evaluate 1.e4"}]
  }'
```
