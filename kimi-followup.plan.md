# Kimi-Folgeplan - CaiLama-LLM-Router

Dieser Plan ist ein versionierbarer Handoff fuer weitere Kimi-Arbeit. Er ist
keine Prompt-Datei und enthaelt keine Secrets.

## Vor Arbeitsbeginn lesen

1. `README.md`
2. `TODO.md`
3. `docs/architecture.md`
4. `docs/backends.md`
5. `docs/configuration.md`
6. `docs/fallback.md`
7. `docs/security.md`
8. `plan.md`

## Prioritaet

Der Router bleibt eine eigenstaendige Infrastruktur-Schicht. Er soll
OpenAI-kompatiblen Modellzugriff, Alias-Aufloesung, Backend-Routing,
Fallbacks und sichere Betriebsdiagnose liefern, ohne CaiLama-Produktlogik zu
enthalten.

## Naechste Aufgaben

- [ ] TODO-Bereich "Betriebs- und Fallback-Haertung" priorisieren.
- [ ] Rollen-Aliase mit CaiLama-Erwartungen abgleichen und Tests bzw.
  Dokumentation nachziehen.
- [ ] Verhalten bei Limit-, Timeout-, Connection- und 5xx-Faellen gezielt
  testen.
- [ ] Logging-Konfiguration pruefen, damit keine Prompt-/Response-Inhalte und
  keine Header mit Secrets geschrieben werden.
- [ ] Kimi-CLI- und CaiLama-Smoke-Pfade aktuell halten.

## Grenzen

- Keine echten Provider-Keys, Tokens oder `.env`-Dateien committen.
- Keine lokalen Host-spezifischen Configs versionieren.
- Keine Schachproduktlogik in den Router verschieben.
- Live-Zugriffe auf Backends nur auf ausdruecklichen Auftrag.

## Abschlusspruefung

```bash
pytest -q
ruff check .
mypy src
git status --short
git diff --check
```

Falls einzelne Tools lokal nicht installiert sind, im Abschluss klar nennen,
welcher Check nicht ausgefuehrt werden konnte.
