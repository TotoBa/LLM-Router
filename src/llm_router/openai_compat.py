from __future__ import annotations

import json
import time
import uuid
from typing import Any

import httpx
from fastapi import APIRouter, Header, Request
from fastapi.responses import JSONResponse, StreamingResponse

from llm_router.backends import backend_order, resolve_backend_model
from llm_router.errors import RouterError, error_response
from llm_router.fallback import should_fallback
from llm_router.schemas import BackendConfig, RouterConfig

router = APIRouter()

# App state is injected by the app module at startup
_CONFIG: RouterConfig | None = None
_HTTP_CLIENT: httpx.AsyncClient | None = None
_LOGGER: Any = None


def _get_logger() -> Any:
    return _LOGGER


def _get_config() -> RouterConfig:
    if _CONFIG is None:
        raise RouterError(500, "configuration_error", "Config not loaded")
    return _CONFIG


def set_config(config: RouterConfig) -> None:
    global _CONFIG
    _CONFIG = config


def set_http_client(client: httpx.AsyncClient) -> None:
    global _HTTP_CLIENT
    _HTTP_CLIENT = client


def set_logger(logger: Any) -> None:
    global _LOGGER
    _LOGGER = logger


def _build_headers(backend: BackendConfig, api_key: str | None) -> dict[str, str]:
    headers: dict[str, str] = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    return headers


def _unknown_model_error(model: str) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content=error_response(f"Unknown model '{model}'", "model_not_found"),
    )


@router.get("/health", response_model=None)
async def health() -> dict[str, Any]:
    config = _get_config()
    return {
        "ok": True,
        "version": "0.1.0",
        "config_loaded": True,
        "models": list(config.models.keys()),
        "backends": {name: {"type": b.type, "priority": b.priority} for name, b in config.backends.items()},
    }


@router.get("/v1/models", response_model=None)
async def list_models() -> dict[str, Any]:
    config = _get_config()
    data: list[dict[str, Any]] = []
    for alias, route in config.models.items():
        data.append(
            {
                "id": alias,
                "object": "model",
                "created": int(time.time()),
                "owned_by": "llm-router",
            }
        )
    return {"object": "list", "data": data}


@router.post("/v1/chat/completions", response_model=None)
async def chat_completions(
    request: Request,
    x_llm_client: str = Header(default="unknown"),
) -> StreamingResponse | JSONResponse:
    config = _get_config()
    body_bytes = await request.body()
    try:
        payload = json.loads(body_bytes)
    except json.JSONDecodeError:
        return JSONResponse(status_code=400, content=error_response("Invalid JSON", "invalid_request"))

    model_alias = payload.get("model")
    if not model_alias or not isinstance(model_alias, str):
        return JSONResponse(status_code=400, content=error_response("Missing or invalid 'model' field", "invalid_request"))

    if model_alias not in config.models:
        if config.runtime.unknown_model_strategy == "error":
            return _unknown_model_error(model_alias)
        # passthrough: use default backends
        backends = [name for name, b in sorted(config.backends.items(), key=lambda x: x[1].priority) if b.enabled]
    else:
        backends = backend_order(model_alias, config)

    if not backends:
        return JSONResponse(status_code=503, content=error_response("No backends available", "no_backends"))

    request_id = str(uuid.uuid4())
    stream = payload.get("stream", False)
    client = x_llm_client
    fallback_used = False
    last_response: httpx.Response | None = None

    for attempt, backend_name in enumerate(backends):
        backend = config.backends[backend_name]
        provider_model = resolve_backend_model(model_alias, backend_name, config)
        proxied_payload = {**payload, "model": provider_model}

        try:
            if _HTTP_CLIENT is None:
                raise RuntimeError("HTTP client not initialized")

            if stream:
                proxy_resp = await _HTTP_CLIENT.stream(
                    "POST",
                    f"{backend.base_url.rstrip('/')}/chat/completions",
                    json=proxied_payload,
                    headers=_build_headers(backend, None),  # resolved per-call in real impl
                )
            else:
                proxy_resp = await _HTTP_CLIENT.post(
                    f"{backend.base_url.rstrip('/')}/chat/completions",
                    json=proxied_payload,
                    headers=_build_headers(backend, None),
                )
        except (httpx.ConnectError, httpx.ConnectTimeout):
            last_response = None
            route = config.models.get(model_alias)
            policy_name = route.policy if route else "default"
            policy = config.policies.get(policy_name) or next(iter(config.policies.values()))
            is_last = attempt == len(backends) - 1
            if not is_last and should_fallback(0, None, True, policy, config):
                fallback_used = True
                continue
            return JSONResponse(status_code=503, content=error_response("Connection error to all backends", "connection_error"))

        last_response = proxy_resp

        if proxy_resp.status_code < 300:
            # success
            status_code = proxy_resp.status_code
            response_headers = {
                "x-llm-router-backend": backend_name,
                "x-llm-router-request-model": model_alias,
                "x-llm-router-provider-model": provider_model,
                "x-llm-router-fallback-used": "true" if fallback_used else "false",
            }

            if stream:
                async def _stream_response(resp: httpx.Response) -> Any:
                    async for chunk in resp.aiter_raw():
                        yield chunk

                return StreamingResponse(
                    _stream_response(proxy_resp),
                    status_code=status_code,
                    headers=response_headers,
                    media_type="text/event-stream",
                )

            out_body = proxy_resp.content
            return JSONResponse(
                status_code=status_code,
                content=json.loads(out_body),
                headers=response_headers,
            )

        # error path – decide whether to fallback
        route = config.models.get(model_alias)
        policy_name = route.policy if route else "default"
        policy = config.policies.get(policy_name) or next(iter(config.policies.values()))
        is_last = attempt == len(backends) - 1

        resp_body = await proxy_resp.aread()
        if not is_last and should_fallback(proxy_resp.status_code, resp_body, False, policy, config):
            fallback_used = True
            continue

        # final attempt failed or not fallbackable
        if proxy_resp.status_code == 404 and config.runtime.unknown_model_strategy != "error":
            return JSONResponse(status_code=404, content=error_response("Model not found on backend", "model_not_found"))

    return JSONResponse(
        status_code=503,
        content=error_response("All backends failed", "all_backends_failed"),
    )
