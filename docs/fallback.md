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

### Standardmaessig kein Fallback bei:

- 400 Bad Request (Client-Fehler)
- 404 Model not found, sofern `fallback_on_model_not_found: false`
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

- **Retry** = dasselbe Backend nochmal versuchen
- **Fallback** = nächstes Backend in der Reihenfolge wählen

In Version 0.1 wird pro Backend praktisch ein Versuch gemacht; Verbindungsfehler fuehren bei aktivierter Policy direkt zum naechsten Backend.

```
Anfrage -> Backend vm -> Connection Error
                     |
                     +-> Backend pi
```

## Beispiel-Log

```json
{"timestamp":1778962130.123,"request_id":"01HY...","client":"chess-system",
 "request_model":"chess-large","provider_model":"gemma4:31b-cloud","backend":"vm",
 "status_code":429,"limit_detected":true,"fallback_used":false,"duration_ms":823}

{"timestamp":1778962131.456,"request_id":"01HY...","client":"chess-system",
 "request_model":"chess-large","provider_model":"gemma4:31b-cloud","backend":"pi",
 "status_code":200,"limit_detected":false,"fallback_used":true,"duration_ms":5720}
```

## Troubleshooting

| Problem | Ursache | Lösung |
|---|---|---|
| Kein Fallback trotz 429 | `fallback_on_limit: false` | Policy anpassen |
| Endlosschleife | Falscher `base_url` | `llm-router check-config` |
| Alle Backends rot | Netzwerkproblem | `llm-router test-backends` |
