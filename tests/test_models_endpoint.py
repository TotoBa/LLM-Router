from __future__ import annotations

import pytest

from llm_router.config import load_config
from llm_router.schemas import RouterConfig


def test_models_returns_logical_aliases(client):
    response = client.get("/v1/models")
    assert response.status_code == 200
    data = response.json()
    model_ids = [m["id"] for m in data.get("data", [])]
    assert "gpt-4o" in model_ids
    assert "claude-opus" in model_ids


def test_no_secrets_in_models_response(client):
    response = client.get("/v1/models")
    assert response.status_code == 200
    text = response.text
    assert "OPENAI_API_KEY" not in text
    assert "ANTHROPIC_API_KEY" not in text
    assert "api_key" not in text.lower() or "api_key_env" not in text


def test_health_no_secrets(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert "OPENAI_API_KEY" not in str(data)
    assert "ANTHROPIC_API_KEY" not in str(data)
    assert "models" in data
    assert "backends" in data
