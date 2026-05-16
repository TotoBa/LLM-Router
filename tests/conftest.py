from __future__ import annotations

import pytest
from pathlib import Path
import httpx
from fastapi.testclient import TestClient

from llm_router.config import load_config
from llm_router.app import create_app
from llm_router.schemas import BackendConfig, ModelRouteConfig, PolicyConfig


pytest_plugins = ("pytest_asyncio",)


@pytest.fixture(scope="session")
def example_config_path(tmp_path_factory) -> Path:
    config_content = """
server:
  host: "127.0.0.1"
  port: 18080

runtime:
  request_timeout_seconds: 600
  connect_timeout_seconds: 10

backends:
  openai:
    type: openai_compatible
    base_url: https://api.openai.com/v1
    api_key_env: OPENAI_API_KEY
    priority: 10
  anthropic:
    type: openai_compatible
    base_url: https://api.anthropic.com/v1
    api_key_env: ANTHROPIC_API_KEY
    priority: 20
  hugging:
    type: openai_compatible
    base_url: https://huggingface.co/v1
    api_key_env: HF_API_KEY
    priority: 30
    enabled: false

models:
  gpt-4o:
    provider_model: gpt-4o
    backends:
      - openai
    policy: standard
  claude-opus:
    provider_model: claude-3-opus-20240229
    backends:
      - anthropic
    policy: standard
  generic-model:
    provider_model: some-model-id
    backends:
      - openai
      - anthropic
    policy: standard
  model-with-overrides:
    provider_model: base-model
    backend_models:
      openai: openai-specific-name
      anthropic: anthropic-specific-name
    backends:
      - openai
      - anthropic
    policy: standard

policies:
  standard:
    max_attempts_per_backend: 1
    retry_on_connection_error: true
    retry_on_timeout: false
    fallback_on_limit: true
    fallback_on_5xx: false
    fallback_on_4xx: false
    fallback_on_model_not_found: false
    timeout_seconds: 300

limit_detection:
  status_codes:
    - 402
    - 403
    - 429
  body_markers:
    - "rate limit"
    - "quota exceeded"
    - "insufficient_quota"

logging:
  level: INFO
  jsonl_path: null
  log_request_body: false
  log_response_body: false
  log_prompt_chars: false
  log_headers: false
"""
    path = tmp_path_factory.mktemp("config") / "test_router.yaml"
    path.write_text(config_content)
    return path


@pytest.fixture(scope="session")
def example_config(example_config_path: Path):
    return load_config(example_config_path)


@pytest.fixture
def app(example_config_path: Path):
    return create_app(config=load_config(example_config_path))


@pytest.fixture
def client(app) -> TestClient:
    return TestClient(app)


@pytest.fixture
def async_client(app) -> httpx.AsyncClient:
    return httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test")
