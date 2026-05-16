from __future__ import annotations

from llm_router.backends import resolve_backend_model, backend_order
from llm_router.schemas import RouterConfig


def test_resolve_backend_model_with_override(example_config: RouterConfig):
    model = resolve_backend_model("model-with-overrides", "openai", example_config)
    assert model == "openai-specific-name"

    model = resolve_backend_model("model-with-overrides", "anthropic", example_config)
    assert model == "anthropic-specific-name"


def test_resolve_backend_model_without_override(example_config: RouterConfig):
    model = resolve_backend_model("gpt-4o", "openai", example_config)
    assert model == "gpt-4o"

    model = resolve_backend_model("claude-opus", "anthropic", example_config)
    assert model == "claude-3-opus-20240229"


def test_backend_order_explicit(example_config: RouterConfig):
    order = backend_order("generic-model", example_config)
    assert order == ["openai", "anthropic"]


def test_backend_order_auto(example_config: RouterConfig):
    # Create a config without explicit backends for an alias
    # First test with a model that has explicit backends
    order = backend_order("gpt-4o", example_config)
    assert order == ["openai"]

    # Model with auto backends (when no backends specified, should use all enabled sorted by priority)
    from llm_router.schemas import ModelRouteConfig
    example_config.models["auto-model"] = ModelRouteConfig(
        provider_model="auto-model-id",
        policy="standard"
    )
    order = backend_order("auto-model", example_config)
    assert order == ["openai", "anthropic"]  # sorted by priority ascending
