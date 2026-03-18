"""Redis caching layer for romanization results."""

import os
import hashlib
import json
from typing import Optional


try:
    import redis as _redis_lib

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


class CacheManager:
    """Redis cache manager for romanization results."""

    def __init__(self, redis_url: str = None):
        self.redis_url = redis_url or os.getenv("REDIS_URL")
        self.client = None
        self.enabled = False
        self._connect()

    def _connect(self):
        """Connect to Redis/Valkey."""
        if not REDIS_AVAILABLE or not self.redis_url:
            return

        try:
            self.client = _redis_lib.from_url(
                self.redis_url,
                decode_responses=True,
                socket_timeout=5,
                socket_connect_timeout=5,
            )
            self.client.ping()
            self.enabled = True
        except Exception:
            self.enabled = False

    def _make_key(self, text: str, style: str = "standard") -> str:
        """Create cache key from text and style."""
        text_hash = hashlib.sha256(text.encode()).hexdigest()[:16]
        return f"romanize:{text_hash}:{style}"

    def get(self, text: str, style: str = "standard") -> Optional[dict]:
        """Get cached result."""
        if not self.enabled:
            return None

        try:
            key = self._make_key(text, style)
            cached = self.client.get(key)
            if cached:
                return json.loads(cached)
        except Exception:
            pass
        return None

    def set(
        self,
        text: str,
        romanized: str,
        metadata: dict,
        style: str = "standard",
        ttl: int = 604800,
    ):
        """Set cached result (default TTL: 7 days)."""
        if not self.enabled:
            return

        try:
            key = self._make_key(text, style)
            data = {
                "romanized": romanized,
                "metadata": metadata,
            }
            self.client.setex(key, ttl, json.dumps(data))
        except Exception:
            pass

    def clear(self):
        """Clear all romanize cache entries."""
        if not self.enabled:
            return

        try:
            keys = self.client.keys("romanize:*")
            if keys:
                self.client.delete(*keys)
        except Exception:
            pass


_cache: Optional[CacheManager] = None


def get_cache() -> CacheManager:
    """Get cache manager singleton."""
    global _cache
    if _cache is None:
        _cache = CacheManager()
    return _cache
