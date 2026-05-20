from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path

import httpx
import typer
import uvicorn

from llm_router.config import load_config
from llm_router.schemas import RouterConfig

cli = typer.Typer()

DEFAULT_CONFIG_PATH = Path(os.environ.get("LLM_ROUTER_CONFIG", "configs/router.local.yaml"))


def _load(path: Path) -> RouterConfig:
    if not path.is_absolute():
        path = Path.cwd() / path
    return load_config(path)


@cli.command()
def serve(
    config: Path = typer.Option(default=DEFAULT_CONFIG_PATH, help="Path to config YAML"),
    host: str = typer.Option(default="127.0.0.1", help="Bind host"),
    port: int = typer.Option(default=18080, help="Bind port"),
) -> None:
    """Start the LLM Router server."""
    os.environ["LLM_ROUTER_CONFIG"] = str(config.resolve())
    uvicorn.run("llm_router.app:app", host=host, port=port, log_level="info")


def _check_env_vars(cfg: RouterConfig) -> list[str]:
    """Check that referenced API key env vars are present in the environment."""
    missing: list[str] = []
    for name, backend in cfg.backends.items():
        if backend.api_key_env and backend.api_key_env not in os.environ:
            missing.append(
                f"Backend '{name}' references env var '{backend.api_key_env}' which is not set"
            )
    if cfg.server.require_api_key and cfg.server.api_key_env:
        if cfg.server.api_key_env not in os.environ:
            missing.append(
                f"Server requires API key env var '{cfg.server.api_key_env}' which is not set"
            )
    return missing


@cli.command()
def check_config(
    config: Path = typer.Option(default=DEFAULT_CONFIG_PATH, help="Path to config YAML"),
) -> None:
    """Validate configuration file and referenced environment variables."""
    try:
        cfg = _load(config)
        typer.echo("Configuration OK")
        typer.echo(f"Models: {list(cfg.models.keys())}")
        typer.echo(f"Backends: {list(cfg.backends.keys())}")
        typer.echo(f"Policies: {list(cfg.policies.keys())}")
        env_issues = _check_env_vars(cfg)
        if env_issues:
            for issue in env_issues:
                typer.echo(f"  ⚠ {issue}", err=True)
    except Exception as exc:
        typer.echo(f"Configuration error: {exc}", err=True)
        raise typer.Exit(1)


@cli.command()
def list_models(
    config: Path = typer.Option(default=DEFAULT_CONFIG_PATH, help="Path to config YAML"),
) -> None:
    """List configured model routes."""
    cfg = _load(config)
    for alias, route in cfg.models.items():
        typer.echo(f"{alias} -> provider_model={route.provider_model} policy={route.policy}")


@cli.command()
def test_backends(
    config: Path = typer.Option(default=DEFAULT_CONFIG_PATH, help="Path to config YAML"),
) -> None:
    """Test connectivity to all configured backends."""
    cfg = _load(config)

    async def _check() -> None:
        async with httpx.AsyncClient() as client:
            for name, backend in cfg.backends.items():
                try:
                    resp = await client.get(
                        f"{backend.base_url.rstrip('/')}/models",
                        timeout=10,
                    )
                    typer.echo(f"{name}: {resp.status_code} {resp.status_code < 300}")
                except Exception as exc:
                    typer.echo(f"{name}: ERROR {exc}")

    asyncio.run(_check())


@cli.command()
def smoke_test(
    config: Path = typer.Option(default=DEFAULT_CONFIG_PATH, help="Path to config YAML"),
    model: str = typer.Option(..., help="Model alias to test"),
    prompt: str = typer.Option(default="Say hello in one word.", help="Prompt to send"),
) -> None:
    """Send a single chat completion to test end-to-end routing."""
    cfg = _load(config)
    base_url = f"http://{cfg.server.host}:{cfg.server.port}"
    headers: dict[str, str] = {}
    if cfg.server.require_api_key and cfg.server.api_key_env:
        key = os.environ.get(cfg.server.api_key_env)
        if key:
            headers["Authorization"] = f"Bearer {key}"

    async def _run() -> None:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{base_url}/v1/chat/completions",
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 10,
                },
                headers=headers,
                timeout=60,
            )
            typer.echo(f"Status: {resp.status_code}")
            typer.echo(json.dumps(resp.json(), indent=2))

    asyncio.run(_run())


def main() -> None:
    cli()


if __name__ == "__main__":
    main()
