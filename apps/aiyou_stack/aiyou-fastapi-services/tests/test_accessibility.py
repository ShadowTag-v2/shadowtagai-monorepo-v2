"""Accessibility compliance tests.

Tests verify WCAG 2.1 Level AA compliance for API:
- Error response structure
- Clear, user-friendly messages
- Semantic HTTP status codes
- Complete API documentation
- Proper headers
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestErrorResponses:
    """Test that all errors follow accessibility standards."""

    def test_validation_error_has_required_fields(self):
        """All error responses must have required accessibility fields."""
        # Send invalid data to trigger validation error
        response = client.post("/api/v1/users", json={"email": "invalid-email"})

        assert response.status_code == 422
        data = response.json()

        # Required fields for accessibility
        assert "status" in data, "Error response missing 'status' field"
        assert "code" in data, "Error response missing 'code' field"
        assert "message" in data, "Error response missing 'message' field"
        assert "timestamp" in data, "Error response missing 'timestamp' field"
        assert "request_id" in data, "Error response missing 'request_id' field"
        assert "details" in data, "Error response missing 'details' field"

        # Verify field values
        assert data["status"] == "error"
        assert isinstance(data["code"], str)
        assert isinstance(data["message"], str)
        assert len(data["message"]) > 0

    def test_error_message_is_user_friendly(self):
        """Error messages should be understandable to non-technical users."""
        response = client.post("/api/v1/users", json={})

        data = response.json()
        message = data["message"].lower()

        # Should NOT contain technical jargon
        assert "traceback" not in message, "Error message contains 'traceback'"
        assert "exception" not in message, "Error message contains 'exception'"
        assert "stack" not in message, "Error message contains 'stack'"
        assert "internal" not in message or "error" in message  # Allow "internal error"

        # Should be helpful
        assert len(message) > 10, "Error message too short to be helpful"

    def test_validation_error_includes_field_details(self):
        """Validation errors should specify which fields are invalid."""
        response = client.post("/api/v1/users", json={"email": "invalid", "name": "A", "age": 999})

        data = response.json()

        assert "details" in data
        assert "errors" in data["details"]
        assert len(data["details"]["errors"]) > 0

        # Each error should have field information
        for error in data["details"]["errors"]:
            assert "field" in error
            assert "message" in error

    def test_not_found_error_format(self):
        """404 errors should follow standard format."""
        response = client.get("/api/v1/users/99999")

        assert response.status_code == 404
        data = response.json()

        # Standard error format
        assert data["status"] == "error"
        assert data["code"] == "NOT_FOUND"
        assert "message" in data
        assert "request_id" in data

        # Should include helpful details
        assert "details" in data
        assert len(data["message"]) > 0

    def test_conflict_error_format(self):
        """409 conflict errors should be clear and helpful."""
        # Create a user
        user_data = {"name": "Test User", "email": "redacted@shadowtag-v4.local", "age": 25}
        client.post("/api/v1/users", json=user_data)

        # Try to create duplicate
        response = client.post("/api/v1/users", json=user_data)

        assert response.status_code == 409
        data = response.json()

        assert data["code"] == "CONFLICT"
        assert "email" in data["message"].lower()
        assert "details" in data


class TestHTTPSemantics:
    """Test that endpoints use proper HTTP semantics."""

    def test_health_check_returns_200(self):
        """Health check should return 200 OK."""
        response = client.get("/health")
        assert response.status_code == 200

    def test_get_returns_200_or_404(self):
        """GET requests should return 200 (found) or 404 (not found)."""
        response = client.get("/api/v1/users/1")
        assert response.status_code in [200, 404]

    def test_create_returns_201(self):
        """POST that creates resource should return 201 Created."""
        response = client.post(
            "/api/v1/users",
            json={"name": "New User", "email": "redacted@shadowtag-v4.local", "age": 30},
        )
        assert response.status_code == 201

    def test_update_returns_200_or_404(self):
        """PUT should return 200 (updated) or 404 (not found)."""
        response = client.put(
            "/api/v1/users/1",
            json={"name": "Updated Name", "email": "redacted@shadowtag-v4.local"},
        )
        assert response.status_code in [200, 404]

    def test_delete_returns_204_or_404(self):
        """DELETE should return 204 (deleted) or 404 (not found)."""
        response = client.delete("/api/v1/users/999")
        assert response.status_code in [204, 404]

    def test_invalid_method_returns_405(self):
        """Invalid HTTP method should return 405 Method Not Allowed."""
        response = client.patch("/health")  # PATCH not supported on health endpoint
        assert response.status_code == 405


class TestAPIDocumentation:
    """Test that API documentation is complete and accessible."""

    def test_openapi_schema_available(self):
        """OpenAPI schema should be accessible."""
        response = client.get("/api/openapi.json")
        assert response.status_code == 200

        schema = response.json()
        assert "openapi" in schema
        assert "info" in schema
        assert "paths" in schema

    def test_all_endpoints_have_summaries(self):
        """All endpoints must have summary descriptions."""
        response = client.get("/api/openapi.json")
        schema = response.json()

        for path, methods in schema["paths"].items():
            for method, details in methods.items():
                assert "summary" in details, f"{method.upper()} {path} missing summary"
                assert len(details["summary"]) > 0, f"{method.upper()} {path} has empty summary"

    def test_all_endpoints_have_descriptions(self):
        """All endpoints must have detailed descriptions."""
        response = client.get("/api/openapi.json")
        schema = response.json()

        for path, methods in schema["paths"].items():
            for method, details in methods.items():
                assert "description" in details, f"{method.upper()} {path} missing description"

    def test_schemas_are_documented(self):
        """Response schemas must be defined in OpenAPI."""
        response = client.get("/api/openapi.json")
        schema = response.json()

        assert "components" in schema
        assert "schemas" in schema["components"]
        assert len(schema["components"]["schemas"]) > 0

        # Check key schemas exist
        schemas = schema["components"]["schemas"]
        assert "HealthResponse" in schemas
        assert "UserResponse" in schemas
        assert "ErrorResponse" in schemas

    def test_error_responses_documented(self):
        """Error responses should be documented for endpoints."""
        response = client.get("/api/openapi.json")
        schema = response.json()

        # Check user endpoints have error responses documented
        user_get = schema["paths"]["/api/v1/users/{user_id}"]["get"]
        assert "responses" in user_get
        assert "404" in user_get["responses"]


class TestAccessibilityHeaders:
    """Test that responses include accessibility-related headers."""

    def test_request_id_header_present(self):
        """All responses should include X-Request-ID for tracing."""
        response = client.get("/health")
        assert "X-Request-ID" in response.headers
        assert len(response.headers["X-Request-ID"]) > 0

    def test_content_type_header_correct(self):
        """Content-Type should be application/json with charset."""
        response = client.get("/health")
        content_type = response.headers.get("Content-Type", "")
        assert "application/json" in content_type
        assert "charset" in content_type.lower() or "utf-8" in content_type.lower()

    def test_security_headers_present(self):
        """Security headers should be present (improves accessibility)."""
        response = client.get("/health")

        assert "X-Content-Type-Options" in response.headers
        assert response.headers["X-Content-Type-Options"] == "nosniff"

        assert "X-Frame-Options" in response.headers
        assert "X-XSS-Protection" in response.headers

    def test_process_time_header_present(self):
        """Response time should be tracked in headers."""
        response = client.get("/health")
        assert "X-Process-Time" in response.headers


class TestInputValidation:
    """Test that input validation provides helpful feedback."""

    def test_missing_required_fields_error(self):
        """Missing required fields should return clear error."""
        response = client.post("/api/v1/users", json={})

        assert response.status_code == 422
        data = response.json()

        # Should list all missing fields
        assert "details" in data
        assert "errors" in data["details"]
        assert len(data["details"]["errors"]) > 0

    def test_invalid_email_format_error(self):
        """Invalid email should return helpful error."""
        response = client.post(
            "/api/v1/users",
            json={"name": "Test", "email": "not-an-email", "age": 25},
        )

        assert response.status_code == 422
        data = response.json()

        # Should mention email field
        errors = data["details"]["errors"]
        email_error = next((e for e in errors if "email" in e.get("field", "")), None)
        assert email_error is not None

    def test_age_validation_error(self):
        """Invalid age should return clear bounds error."""
        response = client.post(
            "/api/v1/users",
            json={"name": "Test", "email": "redacted@shadowtag-v4.local", "age": 999},
        )

        assert response.status_code == 422
        data = response.json()

        # Should mention age field
        errors = data["details"]["errors"]
        age_error = next((e for e in errors if "age" in e.get("field", "")), None)
        assert age_error is not None

    def test_name_length_validation(self):
        """Name too short should return helpful error."""
        response = client.post(
            "/api/v1/users",
            json={"name": "A", "email": "redacted@shadowtag-v4.local", "age": 25},
        )

        assert response.status_code == 422
        data = response.json()

        # Should mention name field
        errors = data["details"]["errors"]
        name_error = next((e for e in errors if "name" in e.get("field", "")), None)
        assert name_error is not None


class TestResponseConsistency:
    """Test that responses follow consistent structure."""

    def test_success_response_structure(self):
        """Successful responses should have consistent structure."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()

        # Health endpoint should return expected fields
        assert "status" in data
        assert "timestamp" in data
        assert "version" in data

    def test_list_response_structure(self):
        """List endpoints should return arrays."""
        response = client.get("/api/v1/users")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_pagination_parameters_work(self):
        """Pagination should work correctly."""
        # Create some users
        for i in range(5):
            client.post(
                "/api/v1/users",
                json={"name": f"User {i}", "email": f"user{i}@example.com", "age": 20 + i},
            )

        # Test pagination
        response = client.get("/api/v1/users?skip=0&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 2

    def test_root_endpoint_provides_links(self):
        """Root endpoint should provide navigation links."""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()

        assert "documentation" in data or "message" in data
        assert "version" in data


class TestWCAGCompliance:
    """Test specific WCAG 2.1 Level AA requirements."""

    def test_perceivable_error_messages(self):
        """Error messages must be text, not just codes (WCAG 3.3.1)."""
        response = client.get("/api/v1/users/99999")

        data = response.json()
        assert isinstance(data["message"], str)
        assert len(data["message"]) > 5  # More than just a code

    def test_understandable_field_names(self):
        """Field names should be descriptive (WCAG 3.2.4)."""
        response = client.get("/api/openapi.json")
        schema = response.json()

        user_schema = schema["components"]["schemas"]["UserResponse"]
        properties = user_schema["properties"]

        # Field names should be clear, not abbreviated
        for field_name in properties:
            assert len(field_name) > 1  # Not just single letters
            # Common abbreviations to avoid: usr, nm, eml, etc.

    def test_robust_json_responses(self):
        """All responses must be valid JSON (WCAG 4.1.1)."""
        endpoints = [
            "/",
            "/health",
            "/api/v1/users",
        ]

        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code == 200

            # Should be valid JSON
            try:
                data = response.json()
                assert data is not None
            except Exception as e:
                pytest.fail(f"Invalid JSON from {endpoint}: {e}")

    def test_consistent_navigation(self):
        """API structure should be consistent (WCAG 3.2.3)."""
        response = client.get("/api/openapi.json")
        schema = response.json()

        # All /api/v1/users endpoints should follow pattern
        user_paths = [p for p in schema["paths"] if "/users" in p]

        for path in user_paths:
            # Check consistent HTTP methods
            methods = schema["paths"][path]
            for method in methods:
                assert "summary" in methods[method]
                assert "description" in methods[method]
