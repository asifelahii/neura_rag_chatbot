import os
import uuid

import pytest
from fastapi import HTTPException

from app.core.config import settings
from app.security.rate_limiter import (
    InMemoryRateLimiter,
    RedisRateLimiter,
)


@pytest.mark.anyio
async def test_memory_rate_limiter_blocks_after_limit(
    monkeypatch,
):
    limiter = InMemoryRateLimiter()

    monkeypatch.setattr(
        settings,
        "rate_limit_requests",
        2,
    )

    monkeypatch.setattr(
        settings,
        "rate_limit_window_seconds",
        60,
    )

    await limiter.check("test-client")
    await limiter.check("test-client")

    with pytest.raises(
        HTTPException
    ) as exc_info:
        await limiter.check(
            "test-client"
        )

    assert exc_info.value.status_code == 429

    assert (
        "Retry-After"
        in exc_info.value.headers
    )


@pytest.mark.integration
@pytest.mark.skipif(
    os.getenv(
        "RUN_REDIS_INTEGRATION_TESTS"
    ) != "1",
    reason=(
        "Redis integration tests are "
        "disabled."
    ),
)
@pytest.mark.anyio
async def test_redis_rate_limiter_shares_state(
    monkeypatch,
):
    limiter_a = RedisRateLimiter()
    limiter_b = RedisRateLimiter()

    client_id = (
        f"integration-{uuid.uuid4()}"
    )

    key = limiter_a._key(
        client_id
    )

    monkeypatch.setattr(
        settings,
        "rate_limit_requests",
        2,
    )

    monkeypatch.setattr(
        settings,
        "rate_limit_window_seconds",
        60,
    )

    try:
        await limiter_a.client.delete(
            key
        )

        await limiter_a.check(
            client_id
        )

        await limiter_b.check(
            client_id
        )

        with pytest.raises(
            HTTPException
        ) as exc_info:
            await limiter_a.check(
                client_id
            )

        assert (
            exc_info.value.status_code
            == 429
        )

        assert (
            "Retry-After"
            in exc_info.value.headers
        )

    finally:
        await limiter_a.client.delete(
            key
        )

        await limiter_a.close()
        await limiter_b.close()
