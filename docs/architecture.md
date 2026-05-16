# Architektur

## Übersicht

Der LLM-Router ist ein **generisches, lokales LLM-Gateway** mit einer OpenAI-kompatiblen API. Er leitet Anfragen von lokalen Tools an konfigurierte Backends weiter und entscheidet anhand von Policies über Fallback.

## Zentrale Architektur-Regel

> **Kimi-cli und das Schachsystem sprechen nie direkt mit Ollama.**
> **Sie sprechen nur mit dem LLM-Router.**

```
┌─────────────┐     ┌─────────────┐
│  kimi-cli   │     │ Schachsystem│
└──────┬──────┘     └──────┬──────┘
       │                   │
       └─────────┬─────────┘
                 │
       ┌─────────▼─────────┐
       │   LLM-Router        │
       │   ROUTER_VM_IP:18080 │
       └─────────┬───────────┘
                 │
       ┌─────────┴─────────┐
       ▼                   ▼
┌──────────────┐   ┌──────────────┐
│Backend 1     │   │Backend 2     │
│(z.B. Ollama) │   │(z.B. Ollama  │
│127.0.0.1     │   │im LAN)       │
└──────────────┘   └──────────────┘
```

## Komponenten

| Komponente | Zweck |
|---|---|
| **Config** | YAML-Datei definiert Backends, Modelle, Policies |
| **Router** | FastAPI-App mit OpenAI-kompatiblen Endpunkten |
| **Backend** | OpenAI-kompatibler Server (Ollama, OpenRouter, ...) |
| **Policy** | Verhaltensregeln: Retry, Timeout, Fallback-Bedingungen |
| **Logger** | JSONL-Logs fuer Anfragen, wenn `logging.jsonl_path` gesetzt ist |

## Flow einer Anfrage

```
1. POST /v1/chat/completions
   ├─ model "chess-small" empfangen
   ├─ Client "chess-system" erkannt
2. Routing
   ├─ "chess-small" → provider_model: "deepseek-v4-flash:cloud"
   ├─ Backends: [vm, pi]
3. Backend-Call #1 (vm)
   ├─ Request an lokales VM-Ollama mit model "deepseek-v4-flash:cloud"
   ├─ 429 zurück → Limit erkannt
4. Fallback → Backend-Call #2 (pi)
   ├─ Request an Pi-Ollama mit model "deepseek-v4-flash:cloud"
   ├─ 200 OK
5. Antwort + Header
   ├─ Original-Response zurück
   ├─ x-llm-router-backend: pi
   ├─ x-llm-router-fallback-used: true
```

## Designprinzipien

- **Generisch:** Keine Hardcoding von Modell- oder Backendnamen
- **Konfigurierbar:** Alles über YAML-Dateien steuerbar
- **Keine Secrets im Code:** API-Keys nur über Environment-Variablen
- **Transparent:** Router-Header zeigen, was passiert ist
