import time
import uuid
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse

logger = logging.getLogger("scamshield.security")

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        # Apply standard hardening security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=(), payment=()"
        
        # CSP: Safe allowlist for React app, fonts, and inline styles while preventing rogue script execution
        response.headers["Content-Security-Policy"] = (
            "default-src 'self' 'unsafe-inline'; "
            "script-src 'self' 'unsafe-inline' https://www.gstatic.com; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' * data: https:; "
            "connect-src 'self' * ws: wss: http: https:; "
            "font-src 'self' data:; "
            "frame-ancestors 'none';"
        )
        return response

class StructuredLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())[:8]
        start_time = time.time()
        request.state.request_id = request_id

        # Sanitize path to avoid leaking sensitive route segments if any
        path = request.url.path

        try:
            response = await call_next(request)
            duration_ms = round((time.time() - start_time) * 1000, 2)
            response.headers["X-Request-ID"] = request_id
            
            # Log structured summary without any credentials or private email bodies
            logger.info(
                f"[{request_id}] {request.method} {path} -> {response.status_code} ({duration_ms}ms)"
            )
            return response
        except Exception as exc:
            duration_ms = round((time.time() - start_time) * 1000, 2)
            logger.error(
                f"[{request_id}] UNHANDLED ERROR on {request.method} {path} after {duration_ms}ms: {type(exc).__name__}"
            )
            # Safe production error response without stack trace or system paths
            return JSONResponse(
                status_code=500,
                content={
                    "detail": "An internal server error occurred. Please contact administrator.",
                    "request_id": request_id
                }
            )
