"""Security Middleware Tests

Tests for rate limiting, security headers, and request validation
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.shadowtag_v4.middleware.security import (
    RateLimitMiddleware,
    RequestValidationMiddleware,
    SecurityHeadersMiddleware,
)


@pytest.fixture
def basic_app():
    """Create basic FastAPI app for middleware testing"""
    app = FastAPI()

    @app.get("/test")
    async def test_endpoint():
        return {"message": "success"}

    @app.post("/upload")
    async def upload_endpoint():
        return {"message": "uploaded"}

    @app.post("/ingestion/jobs")
    async def ingestion_endpoint():
        return {"message": "ingestion started"}

    return app


class TestRateLimitMiddleware:
    """Test rate limiting middleware"""

    def test_rate_limit_allows_within_limit(self, basic_app):
        """Test requests within rate limit are allowed"""
        basic_app.add_middleware(
            RateLimitMiddleware,
            requests_per_minute=60,
            burst=10,
            enabled=True,
        )

        client = TestClient(basic_app)

        # Make 5 requests (well within limit)
        for _i in range(5):
            response = client.get("/test")
            assert response.status_code == 200

            # Check rate limit headers
            assert "X-RateLimit-Limit" in response.headers
            assert "X-RateLimit-Remaining" in response.headers

    def test_rate_limit_blocks_over_limit(self, basic_app):
        """Test requests over burst limit are blocked"""
        basic_app.add_middleware(
            RateLimitMiddleware,
            requests_per_minute=60,
            burst=3,  # Low burst for testing
            enabled=True,
        )

        client = TestClient(basic_app)

        # Make requests up to burst limit
        for _i in range(3):
            response = client.get("/test")
            assert response.status_code == 200

        # Next request should be rate limited
        response = client.get("/test")
        assert response.status_code == 429
        assert "Retry-After" in response.headers

        data = response.json()
        assert "error" in data
        assert "rate limit" in data["error"].lower()

    def test_rate_limit_upload_limit(self, basic_app):
        """Test upload-specific rate limiting"""
        basic_app.add_middleware(
            RateLimitMiddleware,
            requests_per_minute=60,
            upload_per_hour=2,  # Only 2 uploads per hour
            enabled=True,
        )

        client = TestClient(basic_app)

        # Make 2 upload requests (should succeed)
        for _i in range(2):
            response = client.post("/ingestion/jobs")
            assert response.status_code == 200

        # Third upload should be blocked
        response = client.post("/ingestion/jobs")
        assert response.status_code == 429

        data = response.json()
        assert "upload" in data["message"].lower()

    def test_rate_limit_disabled(self, basic_app):
        """Test rate limiting can be disabled"""
        basic_app.add_middleware(
            RateLimitMiddleware,
            requests_per_minute=1,  # Very restrictive
            burst=1,
            enabled=False,  # But disabled
        )

        client = TestClient(basic_app)

        # Should allow many requests even with restrictive limits
        for _i in range(10):
            response = client.get("/test")
            assert response.status_code == 200

    def test_rate_limit_per_ip_isolation(self, basic_app):
        """Test rate limits are isolated per IP"""
        basic_app.add_middleware(RateLimitMiddleware, requests_per_minute=60, burst=2, enabled=True)

        client = TestClient(basic_app)

        # Simulate different IPs using X-Forwarded-For
        headers1 = {"X-Forwarded-For": "1.2.3.4"}
        headers2 = {"X-Forwarded-For": "5.6.7.8"}

        # Each IP should have separate limit
        for _ in range(2):
            response = client.get("/test", headers=headers1)
            assert response.status_code == 200

        for _ in range(2):
            response = client.get("/test", headers=headers2)
            assert response.status_code == 200

        # Now both IPs should be rate limited
        response = client.get("/test", headers=headers1)
        assert response.status_code == 429

        response = client.get("/test", headers=headers2)
        assert response.status_code == 429


class TestSecurityHeadersMiddleware:
    """Test security headers middleware"""

    def test_security_headers_present(self, basic_app):
        """Test all security headers are added"""
        basic_app.add_middleware(SecurityHeadersMiddleware)

        client = TestClient(basic_app)
        response = client.get("/test")

        # Check all OWASP recommended headers
        assert response.headers["X-Frame-Options"] == "DENY"
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert response.headers["X-XSS-Protection"] == "1; mode=block"
        assert "Strict-Transport-Security" in response.headers
        assert "max-age=31536000" in response.headers["Strict-Transport-Security"]
        assert "Content-Security-Policy" in response.headers
        assert "Referrer-Policy" in response.headers
        assert "Permissions-Policy" in response.headers

    def test_security_headers_on_errors(self, basic_app):
        """Test security headers added even on error responses"""
        basic_app.add_middleware(SecurityHeadersMiddleware)

        @basic_app.get("/error")
        async def error_endpoint():
            raise Exception("Test error")

        client = TestClient(basic_app, raise_server_exceptions=False)

        # Even on 500 error, security headers should be present
        response = client.get("/error")
        assert response.status_code == 500
        assert "X-Frame-Options" in response.headers
        assert "X-Content-Type-Options" in response.headers

    def test_csp_header_restrictive(self, basic_app):
        """Test Content-Security-Policy is restrictive"""
        basic_app.add_middleware(SecurityHeadersMiddleware)

        client = TestClient(basic_app)
        response = client.get("/test")

        csp = response.headers["Content-Security-Policy"]

        # Check key CSP directives
        assert "default-src 'self'" in csp
        assert "img-src 'self'" in csp


class TestRequestValidationMiddleware:
    """Test request validation middleware"""

    def test_request_size_limit_enforced(self, basic_app):
        """Test requests exceeding size limit are rejected"""
        basic_app.add_middleware(
            RequestValidationMiddleware,
            max_request_size=1024,  # 1KB limit
            max_upload_size=10240,  # 10KB for uploads
        )

        client = TestClient(basic_app)

        # Request with Content-Length exceeding limit
        headers = {"Content-Length": "2048"}  # 2KB
        response = client.post("/test", headers=headers)

        assert response.status_code == 413
        data = response.json()
        assert "payload too large" in data["error"].lower()

    def test_upload_size_limit_separate(self, basic_app):
        """Test upload endpoints have higher size limits"""
        basic_app.add_middleware(
            RequestValidationMiddleware,
            max_request_size=1024,  # 1KB for regular
            max_upload_size=1024 * 100,  # 100KB for uploads
        )

        client = TestClient(basic_app)

        # Regular endpoint with 2KB should fail
        headers = {"Content-Length": "2048"}
        response = client.post("/test", headers=headers)
        assert response.status_code == 413

        # Upload endpoint with 2KB should succeed (within 100KB limit)
        response = client.post("/ingestion/jobs", headers=headers)
        # Note: Will fail for other reasons (no file), but not 413
        assert response.status_code != 413

    def test_content_type_validation_upload(self, basic_app):
        """Test upload endpoints require multipart/form-data"""
        basic_app.add_middleware(RequestValidationMiddleware)

        client = TestClient(basic_app)

        # Upload with wrong content-type
        headers = {"Content-Type": "application/json"}
        response = client.post("/ingestion/jobs", headers=headers)

        assert response.status_code == 415
        data = response.json()
        assert "unsupported media type" in data["error"].lower()

    def test_content_type_validation_allows_multipart(self, basic_app):
        """Test upload endpoints allow multipart/form-data"""
        basic_app.add_middleware(RequestValidationMiddleware)

        client = TestClient(basic_app)

        # Upload with correct content-type
        headers = {"Content-Type": "multipart/form-data; boundary=----"}
        response = client.post("/ingestion/jobs", headers=headers)

        # Should not fail validation (may fail for other reasons)
        assert response.status_code != 415


class TestMiddlewareIntegration:
    """Test multiple middleware working together"""

    def test_middleware_stack(self, basic_app):
        """Test full middleware stack integration"""
        # Add all middleware (order matters!)
        basic_app.add_middleware(RequestValidationMiddleware)
        basic_app.add_middleware(
            RateLimitMiddleware,
            requests_per_minute=60,
            burst=10,
            enabled=True,
        )
        basic_app.add_middleware(SecurityHeadersMiddleware)

        client = TestClient(basic_app)
        response = client.get("/test")

        # Should have both rate limit and security headers
        assert response.status_code == 200
        assert "X-RateLimit-Limit" in response.headers
        assert "X-Frame-Options" in response.headers
        assert "X-Content-Type-Options" in response.headers

    def test_rate_limit_then_validation(self, basic_app):
        """Test rate limit is checked before validation"""
        basic_app.add_middleware(RequestValidationMiddleware, max_request_size=1024)
        basic_app.add_middleware(
            RateLimitMiddleware,
            requests_per_minute=60,
            burst=1,  # Only 1 request allowed
            enabled=True,
        )

        client = TestClient(basic_app)

        # First request succeeds
        response = client.get("/test")
        assert response.status_code == 200

        # Second request should be rate limited (before validation)
        headers = {"Content-Length": "2048"}  # Would fail validation
        response = client.post("/test", headers=headers)

        # Should be rate limited, not validation error
        assert response.status_code == 429
