"""Rate limiting middleware."""

import os
import time
import logging
from collections import defaultdict
from threading import Lock

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse

logger = logging.getLogger("omnirom")


class RateLimiter:
    """Simple in-memory rate limiter using sliding window."""

    def __init__(self, requests: int = 100, window_seconds: int = 60):
        self.requests = requests
        self.window_seconds = window_seconds
        self.clients: dict = defaultdict(list)
        self.lock = Lock()

    def is_allowed(self, client_id: str) -> bool:
        """Check if request is allowed for client."""
        now = time.time()
        window_start = now - self.window_seconds

        with self.lock:
            # Clean old requests outside the window
            self.clients[client_id] = [
                ts for ts in self.clients[client_id] if ts > window_start
            ]

            # Check if under limit
            if len(self.clients[client_id]) < self.requests:
                self.clients[client_id].append(now)
                return True

            return False

    def get_remaining(self, client_id: str) -> int:
        """Get remaining requests for client."""
        now = time.time()
        window_start = now - self.window_seconds

        with self.lock:
            current = len([ts for ts in self.clients[client_id] if ts > window_start])
            return max(0, self.requests - current)


# Initialize rate limiter from environment
def _get_int_env(name: str, default: int) -> int:
    """Safely parse an integer from environment variables.

    Falls back to `default` and logs a warning if the value is not a valid integer.
    """
    raw_value = os.getenv(name)
    if raw_value is None:
        return default
    try:
        return int(raw_value)
    except ValueError:
        logger.warning(
            "Invalid value for %s=%r; falling back to default %d",
            name,
            raw_value,
            default,
        )
        return default


def _get_rate_limiter() -> RateLimiter:
    """Get rate limiter instance from environment config."""
    # Defaults preserve current behavior: disabled if not explicitly > 0
    requests = _get_int_env("RATE_LIMIT_REQUESTS", 0)
    window = _get_int_env("RATE_LIMIT_WINDOW", 60)

    if requests <= 0:
        return None  # Rate limiting disabled

    return RateLimiter(requests=requests, window_seconds=window)


_rate_limiter = _get_rate_limiter()


def _get_client_ip(request: Request) -> str:
    """Best-effort extraction of the real client IP from the request."""
    # Prefer X-Forwarded-For (first IP is the original client)
    x_forwarded_for = request.headers.get("X-Forwarded-For")
    if x_forwarded_for:
        # The header may contain multiple comma-separated IPs
        first_ip = x_forwarded_for.split(",")[0].strip()
        if first_ip:
            return first_ip

    # Fallback to X-Real-IP if present
    x_real_ip = request.headers.get("X-Real-IP")
    if x_real_ip:
        return x_real_ip

    # Finally, fall back to the connection's client host if available
    if request.client:
        return request.client.host

    return "unknown"


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware."""

    async def dispatch(self, request: Request, call_next):
        # Skip if rate limiting is disabled
        if _rate_limiter is None:
            return await call_next(request)

        # Get client identifier (IP address)
        client_ip = _get_client_ip(request)

        # Check rate limit
        if not _rate_limiter.is_allowed(client_ip):
            logger.warning(f"Rate limit exceeded for {client_ip}")
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Rate limit exceeded",
                    "limit": _rate_limiter.requests,
                    "window_seconds": _rate_limiter.window_seconds,
                },
            )

        response = await call_next(request)

        # Add rate limit headers
        remaining = _rate_limiter.get_remaining(client_ip)
        response.headers["X-RateLimit-Limit"] = str(_rate_limiter.requests)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Window"] = str(_rate_limiter.window_seconds)

        return response


def get_rate_limiter() -> RateLimiter:
    """Get the rate limiter instance (for checking config)."""
    return _rate_limiter
