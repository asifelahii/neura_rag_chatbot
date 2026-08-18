import math
import secrets
import time
from collections import defaultdict, deque

import redis.asyncio as redis
from fastapi import HTTPException

from app.core.config import settings


RATE_LIMIT_MESSAGE = (
    "Too many requests. Please try again shortly."
)


class InMemoryRateLimiter:

    def __init__(self):
        self._requests = defaultdict(deque)

    async def check(self, client_id: str) -> None:
        if not settings.rate_limit_enabled:
            return

        now = time.monotonic()
        window = settings.rate_limit_window_seconds

        bucket = self._requests[client_id]
        cutoff = now - window

        while bucket and bucket[0] <= cutoff:
            bucket.popleft()

        if len(bucket) >= settings.rate_limit_requests:
            retry_after = max(
                1,
                math.ceil(
                    window - (now - bucket[0])
                ),
            )

            raise HTTPException(
                status_code=429,
                detail=RATE_LIMIT_MESSAGE,
                headers={
                    "Retry-After": str(retry_after),
                },
            )

        bucket.append(now)

    async def ping(self) -> bool:
        return True

    async def close(self) -> None:
        pass

    def reset(self) -> None:
        self._requests.clear()


class RedisRateLimiter:

    _SCRIPT = """
local key = KEYS[1]

local limit = tonumber(ARGV[1])
local window_ms = tonumber(ARGV[2])
local member = ARGV[3]

local now_parts = redis.call("TIME")

local now_ms =
    (tonumber(now_parts[1]) * 1000)
    + math.floor(
        tonumber(now_parts[2]) / 1000
    )

local cutoff = now_ms - window_ms

redis.call(
    "ZREMRANGEBYSCORE",
    key,
    "-inf",
    cutoff
)

local count = redis.call(
    "ZCARD",
    key
)

if count >= limit then
    local oldest = redis.call(
        "ZRANGE",
        key,
        0,
        0,
        "WITHSCORES"
    )

    local retry_after_ms = window_ms

    if oldest[2] then
        retry_after_ms = math.max(
            1,
            math.ceil(
                tonumber(oldest[2])
                + window_ms
                - now_ms
            )
        )
    end

    redis.call(
        "PEXPIRE",
        key,
        window_ms
    )

    return {
        0,
        retry_after_ms
    }
end

redis.call(
    "ZADD",
    key,
    now_ms,
    member
)

redis.call(
    "PEXPIRE",
    key,
    window_ms
)

return {
    1,
    0
}
"""

    def __init__(self):
        self.client = redis.Redis.from_url(
            settings.redis_url,
            decode_responses=True,
        )

    def _key(
        self,
        client_id: str,
    ) -> str:
        return (
            f"{settings.rate_limit_key_prefix}"
            f"{client_id}"
        )

    async def check(
        self,
        client_id: str,
    ) -> None:
        if not settings.rate_limit_enabled:
            return

        window_ms = (
            settings.rate_limit_window_seconds
            * 1000
        )

        member = secrets.token_hex(16)

        result = await self.client.eval(
            self._SCRIPT,
            1,
            self._key(client_id),
            settings.rate_limit_requests,
            window_ms,
            member,
        )

        allowed = bool(
            int(result[0])
        )

        if allowed:
            return

        retry_after_ms = int(
            result[1]
        )

        retry_after = max(
            1,
            math.ceil(
                retry_after_ms / 1000
            ),
        )

        raise HTTPException(
            status_code=429,
            detail=RATE_LIMIT_MESSAGE,
            headers={
                "Retry-After": str(retry_after),
            },
        )

    async def ping(self) -> bool:
        return bool(
            await self.client.ping()
        )

    async def close(self) -> None:
        await self.client.aclose()


def create_rate_limiter():
    store_type = (
        settings.rate_limit_store.lower()
    )

    if store_type == "memory":
        return InMemoryRateLimiter()

    if store_type == "redis":
        return RedisRateLimiter()

    raise RuntimeError(
        f"Unsupported rate limit store: "
        f"{store_type}"
    )


rate_limiter = create_rate_limiter()
