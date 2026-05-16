# Security

## Keine Secrets im Repository

- `.env` ist in `.gitignore`
- `configs/*.local.yaml` ist in `.gitignore`
- API-Keys werden nur über Env-Variablen referenziert (`api_key_env`)

## Keine Secrets in Logs

Niemals geloggt werden:
- `Authorization`-Header
- `api_key` in Request/Response-Bodies
- `Cookie` / `Set-Cookie`

Header-Logging ist standardmäßig deaktiviert. Wenn aktiviert, werden sensible Header redacted.

## Lokale Bindung

Standardmäßig bindet der Router an `127.0.0.1`:

```yaml
server:
  host: "127.0.0.1"
  port: 18080
```

Erst mit Bedacht auf `0.0.0.0` umstellen.

## Optionale Router-API-Key

Später kann der Router selbst einen API-Key fordern:

```yaml
server:
  require_api_key: true
  api_key_env: "LLM_ROUTER_API_KEY"
```

Für lokalen Betrieb ist das zunächst nicht nötig.

## Pi-Ollama im Netzwerk

- Kein Port-Forwarding ins Internet
- Optional: Firewall-Regel für Zugriff nur vom Hauptrechner
