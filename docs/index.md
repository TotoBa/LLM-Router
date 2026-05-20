# CaiLama-LLM-Router Dokumentation

Willkommen! Diese Doku richtet sich an alle, die den Router einrichten, konfigurieren oder erweitern wollen.

## Für Einsteiger

| Dokument | Worum geht es? |
|---|---|
| [Architektur](architecture.md) | Wie funktioniert der Router? Wer spricht mit wem? |
| [Konfiguration](configuration.md) | Wie schreibe ich meine eigene Config? |
| [Schnellinstallation](../README.md#schnellinstallation) | Schnell zum Laufen bringen |

## Für spezifische Tools

| Dokument | Worum geht es? |
|---|---|
| [Kimi CLI](kimi-cli.md) | Kimi über den Router nutzen |
| [Schachsystem](chess-system.md) | Schachsystem an den Router anbinden |

## Für Betrieb

| Dokument | Worum geht es? |
|---|---|
| [Backends](backends.md) | Ollama, RasPi, Netzwerk, OpenRouter |
| [Fallback](fallback.md) | Was passiert bei Fehlern? |
| [Logging](logging.md) | Logs lesen, Fehler finden |
| [Deployment](deployment-systemd.md) | systemd-Service einrichten |
| [VM + Pi Rollout](rollout-vm-pi.md) | Beispielhafter Router-Rollout ohne Credentials |
| [Security](security.md) | Secrets, Netzwerk, Best Practices |

## Häufige Fragen

**Woher weiß das Schachsystem, welches Modell es nimmt?**

Das Schachsystem fragt nur logische Aliase (`chess-small`, `chess-large`). Der Router weiß, welches echte Modell dahinter steht.

**Was passiert, wenn Ollama auf dem Pi nicht erreichbar ist?**

Falls konfiguriert, versucht der Router automatisch das nächste Backend (z.B. lokal). Details stehen unter [Fallback](fallback.md).

**Wie verhindere ich, dass meine API-Keys ins Repo kommen?**

Alle `.local.yaml`-Dateien und `.env` sind in `.gitignore`. Stelle sicher, dass du nie `git add -f configs/router.local.yaml` machst.
