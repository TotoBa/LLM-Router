# LLM-Router

Generic local LLM routing gateway with OpenAI-compatible API, model aliases, backend fallback and JSONL logging.

## Features

- OpenAI-compatible `/v1/chat/completions`
- Logical model aliases mapped to real provider models
- Backend fallback on rate limits, quota errors or connection failures
- Configurable policies per model alias
- JSONL request logging without storing prompts by default
- Config-driven routing – no credentials in repository
- Usable by Kimi CLI, chess systems and other local tools

## Quickstart

```bash
git clone git@github.com:TotoBa/LLM-Router.git
cd LLM-Router
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp configs/router.example.yaml configs/router.local.yaml
# Edit configs/router.local.yaml to match your setup
llm-router serve --config configs/router.local.yaml
```

Test:

```bash
curl http://127.0.0.1:18080/health
curl http://127.0.0.1:18080/v1/models
```

## Configuration

Copy the example and adapt it locally:

```bash
cp configs/router.example.yaml configs/router.local.yaml
cp .env.example .env
```

Local configs, `.env` and logs are gitignored by default.

## Kimi CLI

Add to `~/.kimi/config.toml`:

```toml
default_model = "kimi-cli-default"

[providers.local-llm-router]
type = "openai_legacy"
base_url = "http://127.0.0.1:18080/v1"
api_key = "ollama"

[models.kimi-cli-default]
provider = "local-llm-router"
model = "kimi-cli-default"
max_context_size = 131072
capabilities = ["thinking"]
```

Then run:

```bash
kimi --model kimi-cli-default
```

## Chess System Example

```env
LLM_BASE_URL=http://127.0.0.1:18080/v1
LLM_API_KEY=ollama

LLM_MODEL_ROUTER=chess-router
LLM_MODEL_SMALL=chess-small
LLM_MODEL_LARGE=chess-large
LLM_MODEL_TASK=chess-task
```

## Security Notes

- Router binds to `127.0.0.1` by default
- No secrets are logged or returned in API responses
- Keep real API keys in `.env` or environment variables only

## License

MIT
