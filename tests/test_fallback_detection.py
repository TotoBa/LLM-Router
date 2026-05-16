from __future__ import annotations

import pytest

from llm_router.fallback import looks_like_limit_error, should_fallback
from llm_router.schemas import LimitDetectionConfig, PolicyConfig


@pytest.fixture
def limit_config():
    return LimitDetectionConfig(
        status_codes=[402, 403, 429],
        body_markers=["rate limit", "quota exceeded", "insufficient_quota"]
    )


@pytest.fixture
def policy():
    return PolicyConfig(
        max_attempts_per_backend=1,
        retry_on_connection_error=True,
        retry_on_timeout=False,
        fallback_on_limit=True,
        fallback_on_5xx=False,
        fallback_on_4xx=False,
        fallback_on_model_not_found=False,
        timeout_seconds=300
    )


def test_looks_like_limit_error_status_code(limit_config):
    assert looks_like_limit_error(429, b"", limit_config) is True
    assert looks_like_limit_error(402, b"", limit_config) is True
    assert looks_like_limit_error(403, b"", limit_config) is True
    assert looks_like_limit_error(500, b"", limit_config) is False
    assert looks_like_limit_error(200, b"", limit_config) is False


def test_looks_like_limit_error_body_marker(limit_config):
    assert looks_like_limit_error(429, b"You have hit a rate limit", limit_config) is True
    assert looks_like_limit_error(200, b"Your quota exceeded for this month", limit_config) is True
    assert looks_like_limit_error(400, b"insufficient_quota: please upgrade", limit_config) is True
    assert looks_like_limit_error(200, b"success", limit_config) is False


def test_looks_like_limit_error_case_insensitive(limit_config):
    assert looks_like_limit_error(429, b"RATE LIMIT", limit_config) is True
    assert looks_like_limit_error(429, b"Quota Exceeded", limit_config) is True


def test_should_fallback_connection_error(policy):
    config = type("C", (), {"limit_detection": LimitDetectionConfig(status_codes=[429], body_markers=[])})
    assert should_fallback(0, None, True, policy, config) is True

    policy_no_retry = policy.model_copy(update={"retry_on_connection_error": False})
    assert should_fallback(0, None, True, policy_no_retry, config) is False


def test_should_fallback_limit(policy, limit_config):
    config = type("C", (), {"limit_detection": limit_config})
    assert should_fallback(429, b"rate limit", False, policy, config) is True

    policy_no_limit = policy.model_copy(update={"fallback_on_limit": False})
    assert should_fallback(429, b"rate limit", False, policy_no_limit, config) is False


def test_should_fallback_5xx(policy):
    config = type("C", (), {"limit_detection": LimitDetectionConfig(status_codes=[429], body_markers=[])})
    policy_5xx = policy.model_copy(update={"fallback_on_5xx": True})
    assert should_fallback(502, b"bad gateway", False, policy_5xx, config) is True
    assert should_fallback(500, b"internal error", False, policy_5xx, config) is True
    assert should_fallback(500, b"internal error", False, policy, config) is False


def test_should_fallback_4xx(policy):
    config = type("C", (), {"limit_detection": LimitDetectionConfig(status_codes=[429], body_markers=[])})
    policy_4xx = policy.model_copy(update={"fallback_on_4xx": True})
    assert should_fallback(400, b"bad request", False, policy_4xx, config) is True
    assert should_fallback(429, b"rate limit", False, policy_4xx, config) is True  # limit overrides 4xx

    assert should_fallback(400, b"bad request", False, policy, config) is False
