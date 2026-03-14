"""Simple in-memory statistics collector."""

import time
import threading
from collections import defaultdict
from typing import Optional


class StatsCollector:
    """Thread-safe in-memory stats collector."""

    def __init__(self):
        self.lock = threading.Lock()
        self.start_time = time.time()
        self.requests = 0
        self.errors = 0
        self.cache_hits = 0
        self.cache_misses = 0
        self.languages: dict = defaultdict(int)
        self.engines: dict = defaultdict(int)

    def record_request(self, language: str = None, engine: str = None):
        """Record a successful romanization request."""
        with self.lock:
            self.requests += 1
            if language:
                self.languages[language] += 1
            if engine:
                self.engines[engine] += 1

    def record_error(self):
        """Record a failed request."""
        with self.lock:
            self.errors += 1

    def record_cache(self, hit: bool):
        """Record a cache hit or miss."""
        with self.lock:
            if hit:
                self.cache_hits += 1
            else:
                self.cache_misses += 1

    def get_stats(self) -> dict:
        """Get current stats snapshot."""
        with self.lock:
            uptime = time.time() - self.start_time
            cache_total = self.cache_hits + self.cache_misses
            cache_rate = self.cache_hits / cache_total if cache_total > 0 else 0

            return {
                "uptime_seconds": int(uptime),
                "total_requests": self.requests,
                "errors": self.errors,
                "cache": {
                    "hits": self.cache_hits,
                    "misses": self.cache_misses,
                    "hit_rate": round(cache_rate, 3),
                },
                "languages": dict(self.languages),
                "engines": dict(self.engines),
            }


_stats: Optional[StatsCollector] = None


def get_stats() -> StatsCollector:
    """Get stats collector singleton."""
    global _stats
    if _stats is None:
        _stats = StatsCollector()
    return _stats
