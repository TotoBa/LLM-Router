from __future__ import annotations

from llm_router.cli import _check_env_vars, _format_usage
from llm_router.schemas import RouterConfig


def _make_config(**kwargs) -> RouterConfig:
    raw = {
        "server": {"host": "127.0.0.1", "port": 18080},
        "runtime": {},
        "backends": {},
        "models": {},
        "policies": {},
        "limit_detection": {},
        "logging": {},
    }
    raw.update(kwargs)
    return RouterConfig(**raw)


def test_check_env_vars_all_present(monkeypatch):
    monkeypatch.setenv("OPENAI_KEY", "secret")
    monkeypatch.setenv("ANTHROPIC_KEY", "secret")
    cfg = _make_config(backends={
        "openai": {
            "type": "openai_compatible",
            "base_url": "https://api.openai.com/v1",
            "api_key_env": "OPENAI_KEY",
            "priority": 10,
        },
        "anthropic": {
            "type": "openai_compatible",
            "base_url": "https://api.anthropic.com/v1",
            "api_key_env": "ANTHROPIC_KEY",
            "priority": 20,
        },
    })
    assert _check_env_vars(cfg) == []


def test_check_env_vars_missing(monkeypatch):
    monkeypatch.delenv("MISSING_KEY", raising=False)
    cfg = _make_config(backends={
        "openai": {
            "type": "openai_compatible",
            "base_url": "https://api.openai.com/v1",
            "api_key_env": "MISSING_KEY",
            "priority": 10,
        },
    })
    issues = _check_env_vars(cfg)
    assert len(issues) == 1
    assert "MISSING_KEY" in issues[0]


def test_check_env_vars_no_key_required():
    cfg = _make_config(backends={
        "ollama": {
            "type": "openai_compatible",
            "base_url": "http://127.0.0.1:11434/v1",
            "priority": 10,
        },
    })
    assert _check_env_vars(cfg) == []


def test_check_env_vars_server_require_api_key(monkeypatch):
    monkeypatch.delenv("ROUTER_KEY", raising=False)
    cfg = _make_config(
        server={"host": "127.0.0.1", "port": 18080, "require_api_key": True, "api_key_env": "ROUTER_KEY"},
    )
    issues = _check_env_vars(cfg)
    assert len(issues) == 1
    assert "ROUTER_KEY" in issues[0]


def test_format_usage_shows_requests_and_usage():
    data = {
        "timestamp": 12345.0,
        "requests": {
            "total": 10,
            "success": 8,
            "errors": 2,
            "fallbacks": 1,
            "average_latency_ms": 120.5,
        },
        "usage": {
            "prompt_tokens": 1000,
            "completion_tokens": 500,
            "total_tokens": 1500,
        },
        "aliases": {"chess-small": 8, "chess-large": 2},
        "backends": {"local": 5, "pi": 5},
    }
    text = _format_usage(data)
    assert "Requests  total:" in text
    assert "8" in text
    assert "errors:" in text
    assert "fallbacks:" in text
    assert "avg latency:" in text
    assert "prompt:" in text
    assert "1000" in text
    assert "Alias distribution" in text
    assert "Backend distribution" in text


def test_format_usage_no_distributions():
    data = {
        "timestamp": 1.0,
        "requests": {"total": 0, "success": 0, "errors": 0, "fallbacks": 0, "average_latency_ms": 0},
        "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
        "aliases": {},
        "backends": {},
        "cooldowns": {},
        "backend_failures": {},
        "limit_detections": {},
    }
    text = _format_usage(data)
    assert "Requests  total:" in text
    assert "cooldown" not in text.lower()
    assert "failure" not in text.lower()
    assert "limit" not in text.lower()


def test_format_usage_shows_cooldowns_failures_limits():
    data = {
        "timestamp": 1.0,
        "requests": {"total": 5, "success": 3, "errors": 2, "fallbacks": 1, "average_latency_ms": 200.0},
        "usage": {"prompt_tokens": 42, "completion_tokens": 0, "total_tokens": 42},
        "aliases": {},
        "backends": {},
        "cooldowns": {"local": 1},
        "backend_failures": {"pi": 2},
        "limit_detections": {"openai": 1},
    }
    text = _format_usage(data)
    assert "Cooldowns" in text
    assert "local: 1" in text
    assert "Backend failures" in text
    assert "pi: 2" in text
    assert "Limit detections" in text
    assert "openai: 1" in text


def test_format_usage_does_not_contain_content():
    data = {
        "timestamp": 1.0,
        "requests": {"total": 0, "success": 0, "errors": 0, "fallbacks": 0, "average_latency_ms": 0},
        "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
        "aliases": {},
        "backends": {},
    }
    text = _format_usage(data)
    assert "secret" not in text.lower()
    assert "api_key" not in text.lower()
    assert "content" not in text
