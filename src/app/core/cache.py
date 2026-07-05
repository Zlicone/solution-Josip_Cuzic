"""Jednostavan in-memory TTL cache (bez vanjske infrastrukture).

Za /stats: rezultat se pamti kratko vrijeme; svaki write čisti cache.
U produkciji bi se lako zamijenio Redisom (isto get/set/clear sučelje).
"""

import time
from typing import Any

from app.config import settings


class TTLCache:
    def __init__(self, ttl_seconds: int) -> None:
        self._ttl = ttl_seconds
        self._store: dict[str, tuple[float, Any]] = {}

    def get(self, key: str) -> Any | None:
        item = self._store.get(key)
        if item is None:
            return None
        expires_at, value = item
        if time.monotonic() > expires_at:
            del self._store[key]
            return None
        return value

    def set(self, key: str, value: Any) -> None:
        self._store[key] = (time.monotonic() + self._ttl, value)

    def clear(self) -> None:
        self._store.clear()


cache = TTLCache(settings.cache_ttl_seconds)
