# Fallback

## Wann passiert Fallback?

Der Router versucht Backends in der konfigurierten Reihenfolge. Wenn ein Backend versagt, wird das nächste versucht.

### Fallback wird ausgelöst bei:

| Situation | HTTP-Code | Policy-Einstellung |
|---|---|---|
| Rate Limit | 429 | `fallback_on_limit` |
| Quota überschritten | 402 | `fallback_on_limit` |
| Limit-Erkennung in Body | 403 + Marker | `fallback_on_limit` |
| Verbindungsfehler | — | `retry_on_connection_error` |
| Timeout | — | `retry_on_timeout` |
| Server-Fehler | 5xx | `fallback_on_5xx` |

### KEIN Fallback bei:

- 400 Bad Request (Client-Fehler)
- 404 Model not found (außer via speziellem Flag – nicht in v0.1)
- Unbekanntes Modell ohne Default (je nach `unknown_model_strategy`)

## Limit-Erkennung

Erkennung kombiniert Status-Codes und Body-Inhalt:

```yaml
limit_detection:
  status_codes: [402, 403, 429]
  body_markers:
    - "rate limit"
    - "quota"
    - "insufficient quota"
    - "too many requests"
```

## Retry vs. Fallback

- **Retry** = dasselbe Backend nochmal versuchen (z.B. bei Connection-Error)
- **Fallback** = nächstes Backend in der Reihenfolge wählen

```
Anfrage → Backend local (1. Versuch) → Connection Error
                        |
              ja, retry_count < max | nein
                        |
              Wiederholung --------→ Fallback zu nächstem Backend
```

## Beispiel-Log

```json
{"ts":"2026-05-16T20:15:30+02:00","request_id":"01HY...","client":"chess-system",
 "request_model":"chess-large","provider_model":"gemma4:26b","backend":"local",
 "status_code":429,"limit_detected":true,"fallback_used":false,"duration_ms":823}

{"ts":"2026-05-16T20:15:31+02:00","request_id":"01HY...","client":"chess-system",
 "request_model":"chess-large","provider_model":"gemma4:26b","backend":"pi",
 "status_code":200,"limit_detected":false,"fallback_used":true,"duration_ms":5720}
```

## Troubleshooting

| Problem | Ursache | Lösung |
|---|---|---|
| Kein Fallback trotz 429 | `fallback_on_limit: false` | Policy anpassen |
| Endlosschleife | Falscher `base_url` | `llm-router check-config` |
| Alle Backends rot | Netzwerkproblem | `llm-router test-backends` |
