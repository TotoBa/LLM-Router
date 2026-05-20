from __future__ import annotations

from llm_router.cli import _check_env_vars
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
