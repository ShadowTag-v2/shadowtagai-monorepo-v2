"""Security Middleware for ShadowTag-v4 Platform
Implements rate limiting, security headers, and request validation
"""

import logging
import time
from collections import defaultdict, deque

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Token bucket rate limiting middleware

    Implements per-IP rate limiting with separate limits for:
    - General API requests (requests per minute)
    - Upload endpoints (requests per hour)
    """

    def __init__(
        self,
        app: ASGIApp,
        requests_per_minute: int = 60,
        burst: int = 10,
        upload_per_hour: int = 20,
        enabled: bool = True,
    ):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.burst = burst
        self.upload_per_hour = upload_per_hour
        self.enabled = enabled

        # Token buckets: {client_ip: (tokens, last_update)}
        self.buckets: dict[str, tuple[float, float]] = {}

        # Upload tracking: {client_ip: deque of timestamps}
        self.uploads: dict[str, deque] = defaultdict(lambda: deque(maxlen=upload_per_hour))

        # Cleanup old entries every 5 minutes
        self.last_cleanup = time.time()
        self.cleanup_interval = 300  # 5 minutes

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request"""
        # Check X-Forwarded-For header (from load balancer)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()

        # Check X-Real-IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # Fallback to direct connection IP
        if request.client:
            return request.client.host

        return "unknown"

    def _cleanup_old_entries(self):
        """Remove stale entries from buckets and uploads"""
        now = time.time()

        # Cleanup buckets (remove entries older than 2 minutes)
        stale_ips = [ip for ip, (_, last_update) in self.buckets.items() if now - last_update > 120]
        for ip in stale_ips:
            del self.buckets[ip]

        # Cleanup upload trackers (remove IPs with no recent uploads)
        hour_ago = now - 3600
        stale_upload_ips = [
            ip
            for ip, timestamps in self.uploads.items()
            if not timestamps or all(ts < hour_ago for ts in timestamps)
        ]
        for ip in stale_upload_ips:
            del self.uploads[ip]

        logger.debug(f"Cleaned up {len(stale_ips)} stale rate limit entries")

    def _refill_tokens(self, client_ip: str) -> float:
        """Refill tokens based on elapsed time"""
        now = time.time()

        # Cleanup periodically
        if now - self.last_cleanup > self.cleanup_interval:
            self._cleanup_old_entries()
            self.last_cleanup = now

        if client_ip not in self.buckets:
            # New client, give full burst
            self.buckets[client_ip] = (self.burst, now)
            return self.burst

        tokens, last_update = self.buckets[client_ip]

        # Calculate tokens to add based on elapsed time
        elapsed = now - last_update
        tokens_to_add = elapsed * (self.requests_per_minute / 60.0)

        # Refill tokens up to burst limit
        new_tokens = min(self.burst, tokens + tokens_to_add)

        self.buckets[client_ip] = (new_tokens, now)
        return new_tokens

    def _check_upload_limit(self, client_ip: str) -> bool:
        """Check if client has exceeded upload rate limit"""
        now = time.time()
        hour_ago = now - 3600

        # Remove timestamps older than 1 hour
        upload_times = self.uploads[client_ip]
        while upload_times and upload_times[0] < hour_ago:
            upload_times.popleft()

        # Check if limit exceeded
        if len(upload_times) >= self.upload_per_hour:
            return False

        # Add current upload
        upload_times.append(now)
        return True

    async def dispatch(self, request: Request, call_next):
        """Process request with rate limiting"""
        if not self.enabled:
            return await call_next(request)

        client_ip = self._get_client_ip(request)

        # Special handling for upload endpoints
        is_upload = request.method == "POST" and "/ingestion/jobs" in str(request.url.path)

        if is_upload:
            # Check upload-specific limit
            if not self._check_upload_limit(client_ip):
                logger.warning(f"Upload rate limit exceeded for {client_ip}")
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": "Rate limit exceeded",
                        "message": f"Upload limit: {self.upload_per_hour} per hour",
                        "retry_after": 3600,  # 1 hour
                    },
                    headers={"Retry-After": "3600"},
                )

        # Check general rate limit
        tokens = self._refill_tokens(client_ip)

        if tokens < 1.0:
            # Rate limit exceeded
            wait_time = int((1.0 - tokens) / (self.requests_per_minute / 60.0))
            logger.warning(f"Rate limit exceeded for {client_ip}")

            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "message": f"Too many requests. Limit: {self.requests_per_minute}/minute",
                    "retry_after": wait_time,
                },
                headers={"Retry-After": str(wait_time)},
            )

        # Consume one token
        self.buckets[client_ip] = (tokens - 1.0, time.time())

        # Add rate limit headers to response
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(int(tokens - 1))
        response.headers["X-RateLimit-Reset"] = str(int(time.time() + 60))

        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses

    Implements OWASP recommendations for secure HTTP headers
    """

    async def dispatch(self, request: Request, call_next):
        """Add security headers to response"""
        try:
            response = await call_next(request)
        except Exception as e:
            logger.error(f"Unhandled exception in middleware: {e}")
            response = JSONResponse(status_code=500, content={"detail": "Internal Server Error"})

        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"

        # Prevent MIME sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Enable XSS protection
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Strict Transport Security (HTTPS only)
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        # Content Security Policy
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "img-src 'self' data: https:; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline';"
        )

        # Referrer Policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Permissions Policy (formerly Feature-Policy)
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

        return response


class RequestValidationMiddleware(BaseHTTPMiddleware):
    """Validate incoming requests for security issues

    Checks:
    - Request size limits
    - Content-Type validation
    - Suspicious patterns
    """

    def __init__(
        self,
        app: ASGIApp,
        max_request_size: int = 10 * 1024 * 1024,  # 10MB default
        max_upload_size: int = 500 * 1024 * 1024,  # 500MB for uploads
    ):
        super().__init__(app)
        self.max_request_size = max_request_size
        self.max_upload_size = max_upload_size

    async def dispatch(self, request: Request, call_next):
        """Validate request before processing"""
        # Check content length
        content_length = request.headers.get("content-length")
        if content_length:
            size = int(content_length)

            # Different limits for upload endpoints
            is_upload = "/ingestion/jobs" in str(request.url.path)
            max_size = self.max_upload_size if is_upload else self.max_request_size

            if size > max_size:
                logger.warning(f"Request size {size} exceeds limit {max_size}")
                return JSONResponse(
                    status_code=413,
                    content={
                        "error": "Payload too large",
                        "message": f"Maximum size: {max_size / (1024 * 1024):.0f}MB",
                    },
                )

        # Validate Content-Type for POST/PUT requests
        if request.method in ["POST", "PUT"]:
            content_type = request.headers.get("content-type", "")

            # Allow multipart for uploads
            if "/ingestion/jobs" in str(request.url.path):
                if not content_type.startswith("multipart/form-data"):
                    logger.warning(f"Invalid content-type for upload: {content_type}")
                    return JSONResponse(
                        status_code=415,
                        content={
                            "error": "Unsupported media type",
                            "message": "Uploads must use multipart/form-data",
                        },
                    )

        return await call_next(request)
