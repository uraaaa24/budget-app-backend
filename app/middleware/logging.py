import logging
import time

from fastapi import Request as FastAPIRequest
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

logger = logging.getLogger("app.middleware")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log incoming requests and their responses"""

    async def dispatch(self, request: FastAPIRequest, call_next) -> Response:
        start_time = time.time()

        response = await call_next(request)

        process_time = time.time() - start_time

        status_emoji = self._get_status_emoji(response.status_code)

        logger.info(
            f"{status_emoji} {request.method} {request.url.path} → "
            f"{response.status_code} ({process_time:.3f}s)"
        )

        return response

    def _get_status_emoji(self, status_code: int) -> str:
        """Return an emoji based on the HTTP status code."""
        if status_code < 300:
            return "✅"
        elif status_code < 400:
            return "🔄"
        elif status_code < 500:
            return "⚠️"
        else:
            return "❌"
