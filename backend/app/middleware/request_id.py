"""
Request ID Middleware
Adds unique request ID to each request for tracing
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
import uuid


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Add unique request ID to each request"""

    async def dispatch(self, request: Request, call_next):
        # Generate or extract request ID
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

        # Add to request state
        request.state.request_id = request_id

        # Process request
        response = await call_next(request)

        # Add to response headers
        response.headers["X-Request-ID"] = request_id

        return response
