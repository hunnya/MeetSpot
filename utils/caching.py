"""Simple thread-safe TTL caching utility for API responses."""
import time
from threading import Lock
from typing import Any, Optional


class TTLCache:
    """Thread-safe in-memory cache with Time-To-Live (TTL) expiration."""

    def __init__(self, default_ttl_seconds: int = 3600):
        self.default_ttl = default_ttl_seconds
        self._store = {}
        self._lock = Lock()

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            if key in self._store:
                val, expires_at = self._store[key]
                if time.time() < expires_at:
                    return val
                else:
                    del self._store[key]
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        with self._lock:
            expiration = time.time() + (ttl if ttl is not None else self.default_ttl)
            self._store[key] = (value, expiration)

    def clear(self):
        with self._lock:
            self._store.clear()


# Global singletons for cross-service caching
geo_cache = TTLCache(default_ttl_seconds=86400)      # 24 hours for addresses
routing_cache = TTLCache(default_ttl_seconds=7200)    # 2 hours for routes
places_cache = TTLCache(default_ttl_seconds=3600)     # 1 hour for nearby places
weather_cache = TTLCache(default_ttl_seconds=1800)    # 30 minutes for weather
