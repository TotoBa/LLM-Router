# Logging

## JSONL-Format

Wenn `logging.jsonl_path` gesetzt ist, erzeugt jeder Backend-Versuch einen JSONL-Eintrag. Bei Fallback entstehen also mindestens zwei Eintraege: der fehlgeschlagene Versuch und der erfolgreiche Fallback.

```json
{
  "timestamp": 1778962130.123,
  "request_id": "01HY...",
  "client": "chess-system",
  "path": "/v1/chat/completions",
  "request_model": "chess-large",
  "provider_model": "kimi-k2.6:cloud",
  "backend": "vm",
  "status_code": 429,
  "limit_detected": true,
  "fallback_used": false,
  "duration_ms": 823,
  "prompt_chars": null,
  "response_chars": null
}
```

## Datenschutz

**Standardmäßig werden keine sensitiven Daten geloggt:**

```yaml
logging:
  log_request_body: false
  log_response_body: false
  log_prompt_chars: false
  log_headers: false
```

Für lokalen Debugging kann man diese aktivieren, aber nie in Produktion.

## Client-Erkennung

Der Router liest den HTTP-Header `X-LLM-Client`:

```bash
curl -H "X-LLM-Client: chess-system" http://127.0.0.1:18080/v1/chat/completions ...
```

Ohne Header wird `unknown` geloggt.

## Logs prüfen

```bash
# Letzte 20 Einträge
tail -20 logs/llm-router.jsonl | jq .

# Alle Fehler
jq 'select(.status_code >= 400)' logs/llm-router.jsonl

# Fallback-Statistik
jq 'select(.fallback_used == true)' logs/llm-router.jsonl | wc -l
```

## Metriken

`/metrics` liefert aggregierte, inhaltsfreie Betriebsdaten. `cooldowns` zaehlt
nur tatsaechlich gestartete Backend-Cooldowns, nicht jeden einzelnen
fallbackfaehigen Fehler. Einzelne Backend-Fehler bleiben separat unter
`backend_failures` sichtbar.
