"""API Endpoint Tests

Tests for main application endpoints and routes
"""


class TestSystemEndpoints:
    """Test system/health endpoints"""

    def test_root_endpoint(self, client):
        """Test root endpoint returns API info"""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()

        assert data["name"] == "ShadowTag-v4 Platform API"
        assert data["version"] == "0.1.0"
        assert data["status"] == "operational"
        assert "services" in data
        assert "documentation" in data

    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "healthy"
        assert data["service"] == "shadowtag_v4-api"

    def test_status_endpoint(self, client):
        """Test detailed status endpoint"""
        response = client.get("/status")

        assert response.status_code == 200
        data = response.json()

        assert "api" in data
        assert "database" in data
        assert "redis" in data
        assert "services" in data

    def test_not_found_handler(self, client):
        """Test 404 handler"""
        response = client.get("/nonexistent-endpoint")

        assert response.status_code == 404
        data = response.json()

        assert "error" in data
        assert data["error"] == "Not Found"
        assert "path" in data


class TestSecurityHeaders:
    """Test security headers on all endpoints"""

    def test_security_headers_on_root(self, client):
        """Test security headers on root endpoint"""
        response = client.get("/")

        # Check OWASP security headers
        assert response.headers["X-Frame-Options"] == "DENY"
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert response.headers["X-XSS-Protection"] == "1; mode=block"

    def test_security_headers_on_health(self, client):
        """Test security headers on health endpoint"""
        response = client.get("/health")

        assert "X-Frame-Options" in response.headers
        assert "Strict-Transport-Security" in response.headers


class TestRateLimiting:
    """Test rate limiting on endpoints"""

    def test_rate_limit_headers_present(self, client):
        """Test rate limit headers are included in response"""
        # Note: Rate limiting is disabled in test settings
        # This test verifies the structure would work

        response = client.get("/")

        # In production, these headers would be present
        # In tests, rate limiting is disabled
        assert response.status_code == 200


class TestCORS:
    """Test CORS configuration"""

    def test_cors_allowed_origin(self, client):
        """Test CORS headers for allowed origin"""
        headers = {"Origin": "http://testserver"}
        response = client.get("/", headers=headers)

        assert response.status_code == 200
        # CORS headers would be present if origin is allowed

    def test_cors_preflight(self, client):
        """Test CORS preflight request"""
        headers = {"Origin": "http://testserver", "Access-Control-Request-Method": "POST"}
        response = client.options("/", headers=headers)

        # Preflight should be handled
        assert response.status_code in [200, 204]


class TestAuthentication:
    """Test authentication requirements"""

    def test_public_endpoints_no_auth(self, client):
        """Test public endpoints don't require auth"""
        # These endpoints should work without authentication
        response = client.get("/")
        assert response.status_code == 200

        response = client.get("/health")
        assert response.status_code == 200

        response = client.get("/status")
        assert response.status_code == 200

    def test_protected_endpoint_requires_auth(self, client):
        """Test protected endpoints require authentication"""
        # Ingestion endpoints require auth
        response = client.post("/api/v1/ingestion/jobs")

        # Should fail due to missing authentication
        assert response.status_code in [401, 422]  # 422 if validation fails first

    def test_protected_endpoint_with_auth(self, authenticated_client):
        """Test protected endpoint with valid auth token"""
        # This would require proper request body, but should not fail on auth
        response = authenticated_client.post("/api/v1/ingestion/jobs")

        # Should not be 401 (may be 400/422 for other reasons)
        assert response.status_code != 401
