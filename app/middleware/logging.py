"""Request/response logging middleware."""

import time
import logging

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("omnirom")


class LoggingMiddleware(BaseHTTPMiddleware):
    """Log all incoming requests and outgoing responses."""

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        logger.info("Request: %s %s", request.method, request.url.path)

        response = await call_next(request)

        duration_ms = int((time.time() - start_time) * 1000)
        logger.info(
            "Response: %s %s status=%d duration=%dms",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )

        response.headers["X-Process-Time"] = str(duration_ms)
        return response
