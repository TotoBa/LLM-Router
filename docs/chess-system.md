# Schachsystem-Anbindung

## Prinzip

Das Schachsystem spricht nicht direkt mit Ollama. Es spricht nur mit dem Router.

Das Schachsystem kennt:
- logische Rollen (`router`, `small`, `large`, `task`, `coach`, `analyst`, `critic`, `vision`, `scribe`, `researcher`)
- Modell-Aliase (`chess-router`, `chess-small`, `chess-large`, `chess-task`, `chess-coach`, `chess-analyst`, `chess-critic`, `chess-vision`, `chess-scribe`, `chess-researcher`)

Es weiß **nicht**, welches echte Modell dahinter steht und ob es lokal oder auf dem Pi läuft.
Rollenverhalten wie Didaktik, Spoilerarmut, Quellenattribution oder vorsichtiger Umgang mit Diagrammen bleibt Aufgabe des aufrufenden Schachsystems bzw. seiner Prompts. Der Router mappt nur Aliase auf Provider-Modelle und Backends.
Alle Schachrollen sollten vom Client so gepromptet werden, dass Nutzerantworten auf Deutsch erfolgen.

## Env-Konfiguration im Schachsystem

```env
LLM_BASE_URL=http://ROUTER_VM_IP:18080/v1
LLM_API_KEY=ollama

LLM_MODEL_ROUTER=chess-router
LLM_MODEL_SMALL=chess-small
LLM_MODEL_LARGE=chess-large
LLM_MODEL_TASK=chess-task
LLM_MODEL_COACH=chess-coach
LLM_MODEL_ANALYST=chess-analyst
LLM_MODEL_CRITIC=chess-critic
LLM_MODEL_VISION=chess-vision
LLM_MODEL_SCRIBE=chess-scribe
LLM_MODEL_RESEARCHER=chess-researcher
```

## Modellzuordnung

| Rolle | Modell-Alias | Provider-Modell | Zweck |
|---|---|---|---|
| router | `chess-router` | `deepseek-v4-flash:cloud` | Aufgabenklasse, Analyseweg |
| small | `chess-small` | `gemma4:31b-cloud` | Klassifikation, Zugbewertung |
| large | `chess-large` | `kimi-k2.6:cloud` | Lange Analyse, Kommentierung |
| task | `chess-task` | `kimi-k2.6:cloud` | PGN-Kommentare, Zusammenfassungen |
| translator | `chess-translator` | `ministral-3:3b-cloud` | Deutsche Ausgabe-/Uebersetzungsschicht fuer intern englische Rollen-Probes |
| coach | `chess-coach` | `gemma4:31b-cloud` | Didaktischer Trainingscoach, deutsch, spoilerarm, Nutzerstaerke beachten |
| analyst | `chess-analyst` | `qwen3.5:397b-cloud` | Tiefe Analyse aus Engine-, Maia-, Board-Truth-, PGN- und Trainingskontext |
| critic | `chess-critic` | `kimi-k2.6:cloud` | Widersprueche, unbelegte Aussagen und riskante Tool-/Analyseausgaben pruefen |
| vision | `chess-vision` | `gemma4:31b-cloud` | OCR-, Bild- und Diagrammkontext; vorsichtig, keine geratenen FENs |
| scribe | `chess-scribe` | `deepseek-v4-flash:cloud` | Strukturierte deutsche Berichte, PGN-Kommentare, Lernkarten und Konsolentexte |
| researcher | `chess-researcher` | `kimi-k2.6:cloud` | Vorhandene Quellen-, Such- und Knowledge-Kontexte mit Attribution verdichten |

Diese Zuordnung lebt **nur im Router** – das Schachsystem fragt einfach `chess-small` und bekommt eine Antwort.

## Empfohlene Policies

| Alias | Empfohlene Policy | Begründung |
|---|---|---|
| `chess-router` | `standard` | Schnelle Klassifikation, max. 300s |
| `chess-small` | `long_running` | Zugbewertung und Klassifikation mit gemma4:31b-cloud, max. 900s |
| `chess-large` | `long_running` | Lange Analyse, max. 900s |
| `chess-task` | `long_running` | PGN-Kommentare und Zusammenfassungen mit kimi-k2.6, max. 900s |
| `chess-coach` | `long_running` | Didaktische Ausführung, max. 900s |
| `chess-analyst` | `long_running` | Umfangreiche Analyse, max. 900s |
| `chess-critic` | `long_running` | Prüfung auf Konsistenz mit kimi-k2.6, max. 900s |
| `chess-vision` | `long_running` | OCR-/Diagramm-Analyse, max. 900s |
| `chess-scribe` | `standard` | Berichtserstellung, max. 300s |
| `chess-researcher` | `long_running` | Recherche-Verdichtung mit kimi-k2.6, max. 900s |

**Kimi-CLI** verwendet `kimi-cli-default` mit `policy: interactive`
(max. 300s, `fallback_on_5xx: true`), da es als interaktiver Client
schnell antworten und bei Fehlern schnell wechseln muss.

## Router-Konfiguration für Chess

```yaml
models:
  chess-router:
    provider_model: "deepseek-v4-flash:cloud"
    capabilities: ["text", "fast"]
    backends: ["vm", "pi"]
    policy: "standard"

  chess-small:
    provider_model: "gemma4:31b-cloud"
    capabilities: ["text", "fast"]
    backends: ["vm", "pi"]
    policy: "long_running"

  chess-large:
    provider_model: "kimi-k2.6:cloud"
    capabilities: ["text", "large_context", "analysis"]
    backends: ["vm", "pi"]
    policy: "long_running"

  chess-task:
    provider_model: "kimi-k2.6:cloud"
    backends: ["vm", "pi"]
    policy: "long_running"

  chess-coach:
    provider_model: "gemma4:31b-cloud"
    backends: ["vm", "pi"]
    policy: "long_running"

  chess-analyst:
    provider_model: "qwen3.5:397b-cloud"
    backends: ["vm", "pi"]
    policy: "long_running"

  chess-critic:
    provider_model: "kimi-k2.6:cloud"
    backends: ["vm", "pi"]
    policy: "long_running"

  chess-vision:
    provider_model: "gemma4:31b-cloud"
    capabilities: ["text", "vision", "analysis"]
    backends: ["vm", "pi"]
    policy: "long_running"

  chess-scribe:
    provider_model: "deepseek-v4-flash:cloud"
    backends: ["vm", "pi"]
    policy: "standard"

  chess-researcher:
    provider_model: "kimi-k2.6:cloud"
    backends: ["vm", "pi"]
    policy: "long_running"
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
