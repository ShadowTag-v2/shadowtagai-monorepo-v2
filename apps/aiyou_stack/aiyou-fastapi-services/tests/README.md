# ShadowTag-v4 Platform Test Suite

Comprehensive test suite for the ShadowTag-v4 platform covering unit tests, integration tests, and security tests.

## Running Tests

### Run All Tests

```bash
pytest

```

### Run Specific Test Categories

```bash

# Unit tests only (fast)

pytest -m unit

# Security tests

pytest -m security

# Authentication tests

pytest -m auth

# API endpoint tests

pytest -m api

```

### Run Specific Test Files

```bash

# Authentication tests

pytest tests/test_auth.py

# Security middleware tests

pytest tests/test_security_middleware.py

# Configuration tests

pytest tests/test_config.py

```

### Run with Coverage

```bash

# Generate coverage report

pytest --cov=src/shadowtag_v4 --cov-report=html

# View coverage report

open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux

```

### Run Tests in Verbose Mode

```bash
pytest -v

```

### Run Tests with Output

```bash

# Show print statements

pytest -s

# Show local variables on failure

pytest -l

```

## Test Structure

```

tests/
├── conftest.py              # Shared fixtures and test configuration
├── test_auth.py             # Authentication and JWT tests
├── test_security_middleware.py  # Security middleware tests
├── test_api_endpoints.py    # API endpoint tests
├── test_config.py           # Configuration tests
└── README.md                # This file

```

## Test Coverage Goals



- **Overall**: 60% minimum (enforced)


- **Critical modules**: 80%+


  - Authentication (auth.py)


  - Security middleware


  - Database models


  - API routes

## Fixtures Available

### Database Fixtures



- `test_db_engine`: In-memory SQLite database engine


- `test_db_session`: Database session for tests


- `test_user`: Standard test user


- `test_admin_user`: Admin test user

### Authentication Fixtures



- `user_access_token`: JWT token for test user


- `admin_access_token`: JWT token for admin user


- `authenticated_client`: Test client with user auth


- `admin_client`: Test client with admin auth

### Client Fixtures



- `client`: Basic test client (no auth)


- `authenticated_client`: Authenticated test client


- `admin_client`: Admin authenticated client

### Mock Fixtures



- `mock_gemini_client`: Mocked Gemini AI client


- `mock_shadowtag_verifier`: Mocked ShadowTag verifier

### Test Data Fixtures



- `sample_image_file`: Test image file


- `sample_video_file`: Test video file

## Writing Tests

### Basic Test Structure

```python
import pytest

class TestYourFeature:
    """Test your feature"""

    def test_something(self, client):
        """Test that something works"""
        response = client.get("/endpoint")
        assert response.status_code == 200

```

### Using Fixtures

```python
def test_with_auth(self, authenticated_client, test_user):
    """Test authenticated endpoint"""
    response = authenticated_client.get("/protected")
    assert response.status_code == 200
    assert response.json()["user_id"] == test_user.id

```

### Testing Async Functions

```python
@pytest.mark.asyncio
async def test_async_function(self):
    """Test async function"""
    result = await some_async_function()
    assert result is not None

```

### Using Mocks

```python
def test_with_mock(self, mock_gemini_client):
    """Test with mocked external service"""
    result = mock_gemini_client.analyze_image("test.jpg")
    assert result["labels"] is not None

```

## Test Markers

Use markers to categorize tests:

```python
@pytest.mark.unit
def test_unit_test():
    """Fast, isolated unit test"""
    pass

@pytest.mark.integration
def test_integration():
    """Test with database or external services"""
    pass

@pytest.mark.security
def test_security_feature():
    """Security-focused test"""
    pass

@pytest.mark.slow
def test_slow_operation():
    """Long-running test"""
    pass

```

## Continuous Integration

Tests run automatically on:


- Every commit (pre-commit hook)


- Pull requests (GitHub Actions)


- Before deployment (CI/CD pipeline)

### Pre-commit Hook

```bash

# Install pre-commit hook

cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash

pytest -m "not slow" --cov-fail-under=60
EOF
chmod +x .git/hooks/pre-commit

```

## Troubleshooting

### Import Errors

If you get import errors, ensure you're running from the project root:

```bash
cd /path/to/shadowtag_v4-fastapi-services
pytest

```

### Database Errors

Tests use in-memory SQLite. If you get database errors:

```bash

# Clear test database artifacts

rm -rf htmlcov .pytest_cache .coverage
pytest

```

### Coverage Not Updating

```bash

# Clear coverage data

rm .coverage
pytest --cov=src/shadowtag_v4

```

## Best Practices



1. **Isolation**: Each test should be independent


2. **Fast**: Keep unit tests fast (<100ms each)


3. **Clear**: Use descriptive test names


4. **Arrange-Act-Assert**: Follow AAA pattern


5. **Mock External**: Mock external services (Gemini, etc.)


6. **Clean Up**: Use fixtures for setup/teardown

## Resources



- [Pytest Documentation](https://docs.pytest.org/)


- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)


- [Coverage.py](https://coverage.readthedocs.io/)
