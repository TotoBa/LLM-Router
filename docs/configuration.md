# Konfiguration

## Überblick

Der Router wird über eine oder mehrere YAML-Dateien konfiguriert. Die Konfiguration ist in Bereiche aufgeteilt:

```yaml
server:      # Host/Port
runtime:     # Timeouts, Reload
backends:    # Liste der LLM-Backends
models:      # Logische Modell-Aliase
policies:    # Verhaltensregeln
limit_detection:   # Fallback bei Rate-Limits
logging:     # Log-Level und Dateipfade
```

## Schnellstart

```bash
# Kopieren und anpassen
cp configs/router.example.yaml configs/router.local.yaml
nano configs/router.local.yaml
```

`configs/router.local.yaml` ist in `.gitignore` – eure echte Config landet nie im Repository.

## Server

```yaml
server:
  host: "127.0.0.1"   # Oder "0.0.0.0" für alle Interfaces
  port: 18080
```

## Backends

```yaml
backends:
  local:
    type: "openai_compatible"
    base_url: "http://127.0.0.1:11434/v1"
    priority: 10        # Niedriegere Zahl = höhere Priorität
    enabled: true

  pi:
    type: "openai_compatible"
    base_url: "http://192.168.178.50:11434/v1"
    priority: 20
    enabled: true
```

- `base_url` zeigt auf die OpenAI-kompatible API, bei Ollama also mit `/v1`
- `api_key_env` ist optional; falls gesetzt, enthält es den Namen der Env-Variablen, nicht den Key selbst
- `priority` sortiert: niedrigere Zahl = höhere Priorität
- `enabled: false` deaktiviert das Backend komplett

## Modelle (Aliases)

```yaml
models:
  chess-small:
    provider_model: "deepseek-v4-flash:cloud"
    backends: ["local", "pi"]
    policy: "standard"

  chess-large:
    provider_model: "gemma4:31b-cloud"
    backends: ["local", "pi"]
    policy: "long_running"
```

- **Logisches Modell** (`chess-small`) ist das, was der Client anfragt
- **Provider-Modell** (`deepseek-v4-flash:cloud`) ist das, was das Backend versteht
- **Backends**: Reihenfolge ist Fallback-Reihenfolge. Fehlt sie, werden alle `enabled` Backends nach `priority` sortiert.
- Provider-Modelle muessen auf jedem Backend verfuegbar sein, das in `backends` genannt ist

## Policies

Definiert, bei welchen Fehlern Fallback passiert und wie Retry/Timeout gehandhabt werden:

```yaml
policies:
  standard:
    max_attempts_per_backend: 1
    retry_on_connection_error: true
    retry_on_timeout: false
    fallback_on_limit: true
    fallback_on_5xx: true
    fallback_on_4xx: false
    timeout_seconds: 300
```

| Feld | Beschreibung |
|---|---|
| `max_attempts_per_backend` | Wie oft dasselbe Backend versucht wird |
| `retry_on_connection_error` | Nochmal versuchen bei Verbindungsfehler |
| `fallback_on_limit` | Fallback bei 429 / Quota / Limit |
| `fallback_on_5xx` | Fallback bei Serverfehlern |
| `fallback_on_4xx` | Fallback bei Client-Fehlern (rarely true) |
| `timeout_seconds` | Harter Timeout pro Backend-Request |

## Limit Detection

```yaml
limit_detection:
  status_codes: [402, 403, 429]
  body_markers:
    - "rate limit"
    - "quota"
    - "insufficient quota"
```

## Logging

```yaml
logging:
  level: "INFO"
  jsonl_path: "logs/llm-router.jsonl"
  log_request_body: false
  log_response_body: false
  log_prompt_chars: false
  log_headers: false
```

Hinweis: Standardmäßig werden keine Prompts oder Antworten geloggt. Für Debugging lokal freischaltbar.

## Env-Variablen

```bash
OLLAMA_LOCAL_API_KEY=ollama         # für lokale Ollama
OLLAMA_PI_API_KEY=ollama            # für Pi-Ollama
LLM_ROUTER_CONFIG=configs/router.local.yaml
```

Erstelle `.env` im Projekt-Root – es wird nicht eingecheckt.

Ollama ignoriert den Wert eines Bearer-Tokens normalerweise. Fuer reine Ollama-Backends kann `api_key_env` daher weggelassen werden; manche OpenAI-Clients erwarten trotzdem einen API-Key-Wert in ihrer eigenen Konfiguration.
