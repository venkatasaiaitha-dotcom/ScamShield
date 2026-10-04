import time
from collections import defaultdict, deque
from fastapi import Request, HTTPException, status
from typing import Dict, Deque

class InMemoryRateLimiter:
    """
    Sliding window in-memory rate limiter.
    Designed with a standard key-bucket architecture so it can be swapped
    for Redis in distributed production clusters.
    """
    def __init__(self):
        # Maps bucket_key -> deque of timestamps
        self._buckets: Dict[str, Deque[float]] = defaultdict(deque)

    def is_allowed(self, key: str, max_requests: int, window_seconds: int) -> bool:
        now = time.time()
        cutoff = now - window_seconds
        bucket = self._buckets[key]

        # Prune outdated timestamps
        while bucket and bucket[0] < cutoff:
            bucket.popleft()

        if len(bucket) >= max_requests:
            return False

        bucket.append(now)
        return True

    def get_retry_after(self, key: str, window_seconds: int) -> int:
        now = time.time()
        bucket = self._buckets[key]
        if not bucket:
            return 1
        oldest = bucket[0]
        retry_after = int(oldest + window_seconds - now)
        return max(retry_after, 1)

    def reset(self):
        self._buckets.clear()

limiter = InMemoryRateLimiter()

def rate_limit(max_requests: int, window_seconds: int, group: str = "default"):
    """
    FastAPI dependency factory enforcing rate limits per client IP / endpoint group.
    Returns 429 Too Many Requests with Retry-After header if limit exceeded.
    """
    async def dependency(request: Request):
        # Client identifier: forwarded-for or client.host
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            ip = forwarded.split(",")[0].strip()
        else:
            ip = request.client.host if request.client else "127.0.0.1"

        key = f"{group}:{ip}"
        if not limiter.is_allowed(key, max_requests=max_requests, window_seconds=window_seconds):
            retry_after = limiter.get_retry_after(key, window_seconds=window_seconds)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded for {group}. Please wait {retry_after} seconds before retrying.",
                headers={"Retry-After": str(retry_after)}
            )
        return True

    return dependency
