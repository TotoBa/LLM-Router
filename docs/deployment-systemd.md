# Deployment mit systemd

## Installation lokal

1. Kopiere die Beispiel-Service-Datei:

```bash
sudo cp systemd/llm-router.service.example /etc/systemd/system/llm-router.service
sudo nano /etc/systemd/system/llm-router.service
```

2. Passe die Pfade an (ersetze `DEIN_USER` und ggf. den vollständigen Pfad).

3. Aktiviere den Service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now llm-router
```

## Status und Logs

```bash
systemctl status llm-router
journalctl -u llm-router -f
```

## Autostart

Der Service startet nach `network.target` und startet bei Absturz automatisch neu (`Restart=always`).
