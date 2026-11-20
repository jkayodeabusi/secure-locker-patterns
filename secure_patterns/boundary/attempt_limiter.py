"""Pattern 01 · Attempt Limiter.

One-liner: caps tries, so brute force and credential stuffing stall.
Stage: 1, at the boundary.  Foundation: Proxy.  Prevents: CWE-307.

Count attempts per key (one key per account or resource AND one per source),
and refuse further attempts in the window once the limit is passed.
"""
from __future__ import annotations

import threading
import time
from typing import Protocol


class TooManyAttempts(Exception):
    def __init__(self, retry_after: int) -> None:
        super().__init__(f"too many attempts; retry after {retry_after}s")
        self.retry_after = retry_after


class CounterStore(Protocol):
    def incr(self, key: str, ttl: int) -> int:
        """Atomically increment key and return the new count; set its expiry on first use."""
        ...


class InMemoryCounterStore:
    """Single-process store for tests and the local demo. Thread-safe."""

    def __init__(self, clock=time.monotonic) -> None:
        self._clock = clock
        self._lock = threading.Lock()
        self._data: dict[str, tuple[int, float]] = {}

    def incr(self, key: str, ttl: int) -> int:
        now = self._clock()
        with self._lock:
            count, expires = self._data.get(key, (0, now + ttl))
            if now >= expires:
                count, expires = 0, now + ttl
            count += 1
            self._data[key] = (count, expires)
            return count


class RedisCounterStore:
    """Shared store for several app instances.

    INCR and EXPIRE run in one MULTI/EXEC transaction, so parallel requests
    can't slip past the limit, and EXPIRE NX keeps the window from sliding.
    Requires Redis 7 or later.
    """

    def __init__(self, client) -> None:
        self._r = client

    def incr(self, key: str, ttl: int) -> int:
        pipe = self._r.pipeline(transaction=True)
        pipe.incr(key)
        pipe.expire(key, ttl, nx=True)
        count, _ = pipe.execute()
        return int(count)


class AttemptLimiter:
    def __init__(self, store: CounterStore, limit: int = 5, window_seconds: int = 60, *, enforce: bool = True) -> None:
        self.store = store
        self.limit = limit
        self.window = window_seconds
        self.enforce = enforce  # False only in demo break mode (BREAK_PATTERNS=01)

    def check(self, *keys: str) -> None:
        """Count one attempt against every key; refuse if any key is over the limit."""
        for key in keys:
            count = self.store.incr(key, ttl=self.window)
            if count > self.limit and self.enforce:  # the check
                raise TooManyAttempts(retry_after=self.window)
