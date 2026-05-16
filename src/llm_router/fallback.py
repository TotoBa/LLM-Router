from __future__ import annotations

from typing import TYPE_CHECKING

from llm_router.schemas import LimitDetectionConfig, PolicyConfig

if TYPE_CHECKING:
    from llm_router.schemas import RouterConfig


def looks_like_limit_error(status_code: int, body: bytes, config: RouterConfig | LimitDetectionConfig) -> bool:
    if hasattr(config, "limit_detection"):
        status_codes = config.limit_detection.status_codes  # type: ignore[union-attr]
        body_markers = config.limit_detection.body_markers  # type: ignore[union-attr]
    else:
        status_codes = config.status_codes
        body_markers = config.body_markers
    if status_code in status_codes:
        return True
    text = body.decode("utf-8", errors="ignore").lower()
    return any(marker.lower() in text for marker in body_markers)


def should_fallback(
    status_code: int,
    body: bytes | None,
    is_connection_error: bool,
    policy: PolicyConfig,
    config: RouterConfig | LimitDetectionConfig,
) -> bool:
    if is_connection_error and policy.retry_on_connection_error:
        return True
    if body is not None and looks_like_limit_error(status_code, body, config) and policy.fallback_on_limit:
        return True
    if 500 <= status_code < 600 and policy.fallback_on_5xx:
        return True
    if 400 <= status_code < 500:
        if status_code == 404 and policy.fallback_on_model_not_found:
            return True
        if body is not None and looks_like_limit_error(status_code, body, config):
            # already handled above
            return False
        if policy.fallback_on_4xx:
            return True
    return False
