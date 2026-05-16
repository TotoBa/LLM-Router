from __future__ import annotations

import json
import logging
import time
from typing import Any

from llm_router.schemas import RouterConfig


class _JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        if isinstance(record.msg, dict):
            return json.dumps(record.msg, default=str)
        return json.dumps({"message": record.getMessage()}, default=str)


def init_logger(config: RouterConfig) -> logging.Logger:
    logger = logging.getLogger("llm_router")
    logger.setLevel(getattr(logging, config.logging.level.upper(), logging.INFO))
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(_JSONFormatter())
        logger.addHandler(handler)
    if config.logging.jsonl_path:
        fh = logging.FileHandler(config.logging.jsonl_path)
        fh.setFormatter(_JSONFormatter())
        logger.addHandler(fh)
    return logger


def log_request(
    logger: logging.Logger,
    *,
    request_id: str,
    client: str,
    path: str,
    request_model: str,
    provider_model: str,
    backend: str,
    status_code: int | None,
    limit_detected: bool,
    fallback_used: bool,
    duration_ms: float,
    prompt_chars: int | None = None,
    response_chars: int | None = None,
) -> None:
    entry: dict[str, Any] = {
        "timestamp": time.time(),
        "request_id": request_id,
        "client": client,
        "path": path,
        "request_model": request_model,
        "provider_model": provider_model,
        "backend": backend,
        "status_code": status_code,
        "limit_detected": limit_detected,
        "fallback_used": fallback_used,
        "duration_ms": duration_ms,
    }
    if prompt_chars is not None:
        entry["prompt_chars"] = prompt_chars
    if response_chars is not None:
        entry["response_chars"] = response_chars
    logger.info(entry)
