import math
import time
from collections import defaultdict, deque

from fastapi import HTTPException

from app.core.config import settings


class InMemoryRateLimiter:
    def __init__(self):
        self._requests = defaultdict(deque)

    def check(self, client_id: str) -> None:
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
                detail="Too many requests. Please try again shortly.",
                headers={
                    "Retry-After": str(retry_after),
                },
            )

        bucket.append(now)

    def reset(self) -> None:
        self._requests.clear()


rate_limiter = InMemoryRateLimiter()
