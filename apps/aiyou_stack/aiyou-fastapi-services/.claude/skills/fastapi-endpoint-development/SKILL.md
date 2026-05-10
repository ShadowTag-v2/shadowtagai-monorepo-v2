# FastAPI Endpoint Development with TDD

## Purpose

Develop FastAPI endpoints following ShadowTag-v2JR doctrine: security-first, revenue-aware, test-driven development with 2× speed and −90% error rate.

## When to Use This Skill

Activate when:

- Creating new API endpoints

- Implementing business logic in FastAPI

- Adding features to existing services

- Refactoring API routes

## Core Principles


1. **Security Absolute**: Every endpoint validated, sanitized, auth-checked before deployment

2. **Revenue Aware**: Every feature evaluated for monetization potential (tiers, usage tracking, upsells)

3. **Test-Driven**: Write tests first, implement second, verify third

4. **Army RM Framework**: Apply risk brakes (probability A-E × severity I-IV → EH/H/M/L)

5. **Boy Scout Rule**: Leave code cleaner than found

## Development Workflow

### Phase 1: Plan (SOP-C Decision Protocol)

**Before writing any code:**


1. **Define the business value**

   - What problem does this endpoint solve?

   - Revenue impact: Direct (monetizable feature) or Indirect (retention/growth driver)?

   - Expected ROI: Target ≥3× in 18 months


2. **Identify security boundaries**

   - Authentication required? (OAuth2, API keys, JWT)

   - Authorization levels? (user roles, permissions)

   - Input validation requirements

   - Rate limiting needs

   - Data sensitivity classification


3. **Risk assessment**

   - Probability of failure: A (>90%) to E (<10%)

   - Severity of impact: I (catastrophic) to IV (minimal)

   - Risk level: EH/H/M/L

   - Mitigation strategy if H or EH


4. **Define API contract**

   - HTTP method (GET/POST/PUT/DELETE/PATCH)

   - Path structure: `/api/v{version}/{resource}`

   - Request schema (Pydantic models)

   - Response schema (success + error cases)

   - Status codes: 200, 201, 400, 401, 403, 404, 422, 500

### Phase 2: Test-Driven Development (SOP-D Code Review Gate)

**Checklist:**

- [ ] Create Pydantic request/response models with validation

- [ ] Write test for authentication/authorization

- [ ] Write test for valid input (happy path)

- [ ] Write test for invalid input (validation failures)

- [ ] Write test for edge cases (empty, null, boundary values)

- [ ] Write test for error handling (500, network failures)

- [ ] Write test for rate limiting (if applicable)

- [ ] Implement endpoint to pass tests

- [ ] Verify all tests pass

- [ ] Run security scan (dependency check, SQL injection, XSS)

**Test Structure:**

```python

# tests/test_api_<resource>.py

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestResourceEndpoint:
    """Test suite for /api/v1/resource endpoint"""

    def test_create_resource_success(self):
        """Should create resource with valid input"""
        # Arrange
        payload = {"name": "test", "value": 100}

        # Act
        response = client.post("/api/v1/resource", json=payload)

        # Assert
        assert response.status_code == 201
        assert response.json()["name"] == "test"

    def test_create_resource_unauthorized(self):
        """Should reject request without auth token"""
        response = client.post("/api/v1/resource", json={})
        assert response.status_code == 401

    def test_create_resource_invalid_input(self):
        """Should reject malformed input"""
        payload = {"name": "", "value": -1}
        response = client.post("/api/v1/resource", json=payload)
        assert response.status_code == 422

```

### Phase 3: Implementation (Boy Scout Rule)

**Code Structure:**

```python

# app/models/resource.py

from pydantic import BaseModel, Field, validator

class ResourceCreate(BaseModel):
    """Request schema for creating resource"""
    name: str = Field(..., min_length=1, max_length=255)
    value: int = Field(..., ge=0, le=1000000)

    @validator('name')
    def name_must_not_contain_special_chars(cls, v):
        if not v.replace(' ', '').isalnum():
            raise ValueError('Name must be alphanumeric')
        return v

class ResourceResponse(BaseModel):
    """Response schema for resource"""
    id: int
    name: str
    value: int
    created_at: datetime

    class Config:
        from_attributes = True


# app/api/v1/endpoints/resource.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.security import get_current_user
from app.models.resource import ResourceCreate, ResourceResponse
from app.db.session import get_db

router = APIRouter(prefix="/api/v1/resource", tags=["resource"])

@router.post(
    "/",
    response_model=ResourceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new resource",
    description="Creates a new resource with validation and auth"
)
async def create_resource(
    resource: ResourceCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Create resource endpoint.

    Security: Requires authentication
    Rate limit: 100/hour per user
    Revenue: Tier-gated (Premium+ only)
    """
    try:
        # Revenue gate: Check user tier
        if not current_user.has_permission("create_resource"):
            raise HTTPException(
                status_code=403,
                detail="Upgrade to Premium to create resources"
            )

        # Business logic
        db_resource = create_resource_in_db(db, resource, current_user.id)

        # Track for analytics/billing
        track_usage(current_user.id, "resource_created")

        return db_resource

    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        log_error(e, context={"user_id": current_user.id})
        raise HTTPException(status_code=500, detail="Internal server error")

```

### Phase 4: Revenue Integration

**Checklist:**

- [ ] Add usage tracking (meter for billing)

- [ ] Implement tier gates (free/pro/enterprise)

- [ ] Add rate limiting (prevent abuse, upsell opportunity)

- [ ] Create analytics events (conversion funnel tracking)

- [ ] Document monetization in endpoint docstring

- [ ] Add to pricing page documentation

**Revenue Patterns:**

- **Freemium**: Basic endpoint free, advanced params gated

- **Usage-based**: Track calls, charge after quota

- **Tier-based**: Feature available only in higher tiers

- **Add-ons**: Optional expensive operations as upsells

### Phase 5: Verification (SOP-A Upload Triage)

**Pre-commit Checklist:**

- [ ] All tests pass (`pytest tests/ -v`)

- [ ] Code coverage ≥80% (`pytest --cov=app`)

- [ ] Type checking passes (`mypy app/`)

- [ ] Linting passes (`ruff check app/`)

- [ ] Security scan clean (`bandit -r app/`)

- [ ] API docs updated (`/docs` endpoint)

- [ ] Risk assessment documented in PR

- [ ] Revenue impact noted in PR description

### Phase 6: Deployment (SOP-B Change & Release)

**Checklist:**

- [ ] Database migrations tested (if applicable)

- [ ] Environment variables documented

- [ ] Vertex AI Workbench staging test passed

- [ ] GKE deployment manifest updated

- [ ] Monitoring/alerts configured

- [ ] Rollback plan documented

- [ ] Performance benchmarks recorded

- [ ] Security review completed

## Error Handling Standards

**Always handle:**

1. **Authentication errors**: 401 with clear message

2. **Authorization errors**: 403 with upgrade path

3. **Validation errors**: 422 with field-specific details

4. **Not found errors**: 404 with suggestion

5. **Rate limit errors**: 429 with retry-after header

6. **Server errors**: 500 with tracking ID (no internal details leaked)

## Security Checklist (Non-Negotiable)


- [ ] Input validation on all parameters

- [ ] SQL injection prevention (use ORMs, parameterized queries)

- [ ] XSS prevention (escape output, use Pydantic)

- [ ] CSRF tokens (for state-changing operations)

- [ ] Rate limiting (per-user, per-endpoint)

- [ ] Authentication on all non-public endpoints

- [ ] Authorization checks before business logic

- [ ] Secrets in environment variables (never hardcoded)

- [ ] HTTPS only (enforce in production)

- [ ] Security headers (CORS, CSP, HSTS)

## Simplicity Mandate

**Every endpoint should:**

- Have ONE clear responsibility

- Functions ≤20 lines (extract helpers)

- No nested ternaries or complex conditionals

- Clear variable names (no abbreviations)

- Docstrings explaining WHY (not what)

- No external libs without team approval

## Quality Gates (Will Fail PR If Not Met)


1. **Security**: No high/critical vulnerabilities

2. **Tests**: Coverage ≥80%, all passing

3. **Performance**: Response time ≤200ms (p95)

4. **Documentation**: API contract fully documented

5. **Revenue**: Monetization strategy noted (if applicable)

## Success Metrics


- **Velocity**: 2× faster development (target)

- **Quality**: −90% error rate (target)

- **Security**: 100% endpoints validated

- **Revenue**: Every feature evaluated for monetization

## Common Pitfalls to Avoid


1. **Skipping tests**: "I'll add them later" = never happens

2. **Weak validation**: Trusting client input = security nightmare

3. **Missing auth**: "Just for internal use" = eventual breach

4. **No rate limits**: Abuse + runaway costs

5. **Ignoring revenue**: Leaving money on table

6. **Complex endpoints**: Single endpoint doing multiple things

7. **Poor errors**: Generic messages frustrate users and support

## Example: Complete Endpoint Development

See `/examples/fastapi-endpoint-complete.py` for a reference implementation showing all principles applied.

## Resources


- FastAPI Security: https://fastapi.tiangolo.com/tutorial/security/

- Pydantic Validation: https://docs.pydantic.dev/latest/usage/validators/

- Army RM Framework: ATP 5-19 Risk Management

- Revenue Patterns: /docs/monetization-strategies.md

---

**Remember**: Security is non-negotiable. Revenue awareness is mandatory. Tests come first. Simplicity wins.
