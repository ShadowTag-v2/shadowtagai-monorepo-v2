# API Security & Validation Patterns

## Purpose

Enforce 100% security coverage for all API endpoints following defense-in-depth principles. Security is absolute—no exceptions, no compromises.

## When to Use This Skill

Activate when:

- Reviewing any API endpoint code

- Implementing authentication/authorization

- Adding input validation

- Conducting security audits

- Responding to security findings

## Core Security Absolute

**Non-negotiable truth**: One security breach destroys more value than 1000 features create. Security is the operational gate—if lost, all other work stops until restored.

## Defense-in-Depth Layers

### Layer 1: Network & Infrastructure

```python

# app/core/config.py

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Security-first configuration"""

    # HTTPS enforcement
    FORCE_HTTPS: bool = True
    SECURE_COOKIES: bool = True

    # CORS configuration (restrictive by default)
    ALLOWED_ORIGINS: list[str] = ["https://yourdomain.com"]
    ALLOW_CREDENTIALS: bool = True

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_BURST: int = 10

    # Security headers
    HSTS_MAX_AGE: int = 31536000  # 1 year
    CSP_POLICY: str = "default-src 'self'"

    class Config:
        env_file = ".env"
        case_sensitive = True


# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app = FastAPI()

# Force HTTPS in production

if settings.FORCE_HTTPS:
    app.add_middleware(HTTPSRedirectMiddleware)

# Trusted host protection

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["yourdomain.com", "*.yourdomain.com"]
)

# CORS with strict defaults

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=settings.ALLOW_CREDENTIALS,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
    max_age=3600,
)

# Security headers

@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["Strict-Transport-Security"] = f"max-age={settings.HSTS_MAX_AGE}"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Content-Security-Policy"] = settings.CSP_POLICY
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response

```

### Layer 2: Authentication

**OAuth2 with JWT Pattern:**

```python

# app/core/security.py

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

# Password hashing (use Argon2 for production)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

# JWT configuration

SECRET_KEY = os.getenv("JWT_SECRET_KEY")  # Never hardcode!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15  # Short-lived
REFRESH_TOKEN_EXPIRE_DAYS = 7


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash password [VAPORIZED_PWD]"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict):
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Extract and validate current user from JWT"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")

        if user_id is None or token_type != "access":
            raise credentials_exception

        # Verify token not revoked (check Redis/DB)
        if await is_token_revoked(token):
            raise credentials_exception

        user = await get_user_from_db(user_id)
        if user is None:
            raise credentials_exception

        return user

    except JWTError:
        raise credentials_exception


async def get_current_active_user(
    current_user = Depends(get_current_user)
):
    """Ensure user is active"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

```

**API Key Pattern (for service-to-service):**

```python

# app/core/api_keys.py

from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(api_key: str = Security(api_key_header)):
    """Verify API key from header"""
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key"
        )

    # Check against database (hashed)
    key_data = await get_api_key_from_db(api_key)

    if not key_data or not key_data.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or inactive API key"
        )

    # Rate limit by API key
    await check_api_key_rate_limit(api_key)

    # Track usage for billing
    await track_api_key_usage(key_data.id)

    return key_data

```

### Layer 3: Authorization (Role-Based Access Control)

```python

# app/core/permissions.py

from enum import Enum
from fastapi import Depends, HTTPException, status

class UserRole(str, Enum):
    """User role hierarchy"""
    ADMIN = "admin"
    PREMIUM = "premium"
    USER = "user"
    GUEST = "guest"


class Permission(str, Enum):
    """Granular permissions"""
    READ_OWN = "read:own"
    READ_ALL = "read:all"
    WRITE_OWN = "write:own"
    WRITE_ALL = "write:all"
    DELETE_OWN = "delete:own"
    DELETE_ALL = "delete:all"
    ADMIN_PANEL = "admin:panel"


# Role -> Permissions mapping

ROLE_PERMISSIONS = {
    UserRole.ADMIN: list(Permission),  # All permissions
    UserRole.PREMIUM: [
        Permission.READ_OWN,
        Permission.READ_ALL,
        Permission.WRITE_OWN,
        Permission.DELETE_OWN,
    ],
    UserRole.USER: [
        Permission.READ_OWN,
        Permission.WRITE_OWN,
    ],
    UserRole.GUEST: [
        Permission.READ_OWN,
    ],
}


def require_permission(permission: Permission):
    """Dependency to enforce permission"""
    async def check_permission(current_user = Depends(get_current_active_user)):
        user_permissions = ROLE_PERMISSIONS.get(current_user.role, [])

        if permission not in user_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Upgrade to access this feature."
            )

        return current_user

    return check_permission


def require_role(minimum_role: UserRole):
    """Dependency to enforce minimum role"""
    role_hierarchy = {
        UserRole.GUEST: 0,
        UserRole.USER: 1,
        UserRole.PREMIUM: 2,
        UserRole.ADMIN: 3,
    }

    async def check_role(current_user = Depends(get_current_active_user)):
        user_level = role_hierarchy.get(current_user.role, 0)
        required_level = role_hierarchy.get(minimum_role, 0)

        if user_level < required_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires {minimum_role.value} role or higher"
            )

        return current_user

    return check_role


# Usage in endpoints

@router.delete("/resources/{resource_id}")
async def delete_resource(
    resource_id: int,
    current_user = Depends(require_permission(Permission.DELETE_OWN))
):
    """Delete resource (requires delete:own permission)"""
    # Check ownership
    resource = await get_resource(resource_id)
    if resource.owner_id != current_user.id:
        # Check if user has delete:all permission
        if Permission.DELETE_ALL not in ROLE_PERMISSIONS[current_user.role]:
            raise HTTPException(status_code=403, detail="Not your resource")

    await delete_resource_from_db(resource_id)
    return {"status": "deleted"}

```

### Layer 4: Input Validation

**Pydantic Models with Strict Validation:**

```python

# app/models/validation.py

from pydantic import BaseModel, Field, validator, constr, conint
from typing import Optional
import re

class StrictEmail(BaseModel):
    """Email with strict validation"""
    email: str = Field(..., max_length=255)

    @validator('email')
    def validate_email(cls, v):
        # RFC 5322 compliant regex (simplified)
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, v):
            raise ValueError('Invalid email format')
        return v.lower()


class SecureUsername(BaseModel):
    """Username with security constraints"""
    username: constr(min_length=3, max_length=32, regex=r'^[a-zA-Z0-9_-]+$')

    @validator('username')
    def no_reserved_names(cls, v):
        reserved = ['admin', 'root', 'system', 'api']
        if v.lower() in reserved:
            raise ValueError('Username not available')
        return v


class SafeTextInput(BaseModel):
    """Text input with XSS prevention"""
    text: str = Field(..., max_length=10000)

    @validator('text')
    def sanitize_text(cls, v):
        # Remove potential XSS patterns
        dangerous_patterns = [
            r'<script',
            r'javascript:',
            r'onerror=',
            r'onclick=',
            r'onload=',
        ]
        for pattern in dangerous_patterns:
            if re.search(pattern, v, re.IGNORECASE):
                raise ValueError('Potentially dangerous content detected')
        return v


class FileUpload(BaseModel):
    """Secure file upload validation"""
    filename: str = Field(..., max_length=255)
    content_type: str
    size_bytes: conint(gt=0, le=10_000_000)  # Max 10MB

    @validator('filename')
    def safe_filename(cls, v):
        # Allow only safe characters
        if not re.match(r'^[a-zA-Z0-9._-]+$', v):
            raise ValueError('Invalid filename characters')
        # Prevent path traversal
        if '..' in v or '/' in v or '\\' in v:
            raise ValueError('Invalid filename')
        return v

    @validator('content_type')
    def allowed_content_type(cls, v):
        allowed = [
            'image/jpeg',
            'image/png',
            'image/gif',
            'application/pdf',
        ]
        if v not in allowed:
            raise ValueError(f'Content type {v} not allowed')
        return v


class PaginationParams(BaseModel):
    """Secure pagination to prevent resource exhaustion"""
    page: conint(ge=1) = 1
    page_size: conint(ge=1, le=100) = 20  # Max 100 items per page

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size

```

**SQL Injection Prevention:**

```python

# app/db/queries.py

from sqlalchemy.orm import Session
from sqlalchemy import text

# ✅ SAFE: Using ORM

def get_user_safe(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

# ✅ SAFE: Parameterized query

def get_user_safe_raw(db: Session, email: str):
    query = text("SELECT * FROM users WHERE email = :email")
    return db.execute(query, {"email": email}).fetchone()

# ❌ UNSAFE: String interpolation (NEVER DO THIS)

def get_user_unsafe(db: Session, email: str):
    query = f"SELECT * FROM users WHERE email = '{email}'"  # SQL INJECTION!
    return db.execute(text(query)).fetchone()

```

### Layer 5: Rate Limiting

```python

# app/core/rate_limit.py

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
import redis
from datetime import timedelta

redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)


async def rate_limit_by_ip(
    request: Request,
    max_requests: int = 60,
    window_seconds: int = 60
):
    """Rate limit by IP address"""
    client_ip = request.client.host
    key = f"rate_limit:ip:{client_ip}"

    current = redis_client.incr(key)

    if current == 1:
        redis_client.expire(key, window_seconds)

    if current > max_requests:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Try again later.",
            headers={"Retry-After": str(window_seconds)}
        )


async def rate_limit_by_user(
    user_id: int,
    max_requests: int = 100,
    window_seconds: int = 60
):
    """Rate limit by authenticated user"""
    key = f"rate_limit:user:{user_id}"

    current = redis_client.incr(key)

    if current == 1:
        redis_client.expire(key, window_seconds)

    if current > max_requests:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Upgrade for higher limits.",
            headers={"Retry-After": str(window_seconds)}
        )

    # Add remaining quota to response headers
    return {
        "X-RateLimit-Limit": max_requests,
        "X-RateLimit-Remaining": max(0, max_requests - current),
        "X-RateLimit-Reset": window_seconds
    }


# Usage in endpoint

@router.post("/api/v1/resources")
async def create_resource(
    request: Request,
    current_user = Depends(get_current_active_user)
):
    await rate_limit_by_ip(request, max_requests=30, window_seconds=60)
    await rate_limit_by_user(current_user.id, max_requests=100, window_seconds=60)

    # ... rest of endpoint logic

```

### Layer 6: Secrets Management

```python

# app/core/secrets.py

from google.cloud import secretmanager
import os

class SecretsManager:
    """Secure secrets handling for GCP"""

    def __init__(self):
        self.client = secretmanager.SecretManagerServiceClient()
        self.project_id = os.getenv("GCP_PROJECT_ID")

    def get_secret(self, secret_name: str, version: str = "latest") -> str:
        """Retrieve secret from Google Secret Manager"""
        name = f"projects/{self.project_id}/secrets/{secret_name}/versions/{version}"
        response = self.client.access_secret_version(request={"name": name})
        return response.payload.data.decode("UTF-8")


# Usage

secrets = SecretsManager()
DATABASE_URL = secrets.get_secret("database-url")
JWT_SECRET = secrets.get_secret("jwt-secret-key")
API_KEY = secrets.get_secret("external-api-key")

# ❌ NEVER do this:

# DATABASE_URL = "postgresql://user:password@localhost/db"  # Hardcoded!

```

## Security Audit Checklist

**Before deploying any endpoint:**


- [ ] Authentication enforced (unless explicitly public)

- [ ] Authorization checked (user can access THIS resource)

- [ ] All inputs validated (Pydantic models)

- [ ] SQL injection prevented (use ORM or parameterized queries)

- [ ] XSS prevented (validate/sanitize text inputs)

- [ ] CSRF protection (for state-changing operations)

- [ ] Rate limiting implemented

- [ ] Secrets in Secret Manager (never in code/env files in repo)

- [ ] Error messages don't leak sensitive info

- [ ] Logging doesn't include PII/secrets

- [ ] HTTPS enforced (production)

- [ ] Security headers configured

- [ ] Dependencies scanned (no critical CVEs)

- [ ] API documented with security requirements

## Common Vulnerabilities to Prevent

### 1. Broken Authentication

```python

# ❌ BAD: Weak password [VAPORIZED_PWD]

password: str = Field(...)

# ✅ GOOD: Strong password policy

from pydantic import validator
import re

class PasswordCreate(BaseModel):
    password: str = Field(..., min_length=12, max_length=128)

    @validator('password')
    def strong_password(cls, v):
        if not re.search(r'[A-Z]', v):
            raise ValueError('Must contain uppercase')
        if not re.search(r'[a-z]', v):
            raise ValueError('Must contain lowercase')
        if not re.search(r'[0-9]', v):
            raise ValueError('Must contain digit')
        if not re.search(r'[!@#$%^&*]', v):
            raise ValueError('Must contain special character')
        return v

```

### 2. Insecure Direct Object References (IDOR)

```python

# ❌ BAD: No ownership check

@router.get("/documents/{doc_id}")
async def get_document(doc_id: int):
    return await get_doc_from_db(doc_id)  # Anyone can access any doc!

# ✅ GOOD: Verify ownership

@router.get("/documents/{doc_id}")
async def get_document(
    doc_id: int,
    current_user = Depends(get_current_active_user)
):
    doc = await get_doc_from_db(doc_id)
    if doc.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc

```

### 3. Mass Assignment

```python

# ❌ BAD: Accepting arbitrary fields

@router.patch("/users/me")
async def update_user(data: dict, current_user = Depends(get_current_user)):
    await update_user_in_db(current_user.id, **data)  # User can set is_admin=True!

# ✅ GOOD: Explicit allowed fields

class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    bio: Optional[str] = Field(None, max_length=1000)
    # is_admin explicitly NOT included

@router.patch("/users/me")
async def update_user(
    data: UserUpdate,
    current_user = Depends(get_current_user)
):
    await update_user_in_db(current_user.id, data.dict(exclude_unset=True))

```

## Testing Security

```python

# tests/test_security.py

import pytest

def test_unauthenticated_access_denied():
    """Should reject requests without auth"""
    response = client.get("/api/v1/protected")
    assert response.status_code == 401

def test_insufficient_permissions():
    """Should reject user without required permission"""
    token = create_token_for_user(role="user")
    response = client.delete(
        "/api/v1/admin/users/123",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403

def test_sql_injection_prevention():
    """Should prevent SQL injection"""
    malicious_input = "'; DROP TABLE users; --"
    response = client.get(f"/api/v1/search?q={malicious_input}")
    assert response.status_code in [200, 400, 422]
    # Verify users table still exists
    assert user_table_exists()

def test_xss_prevention():
    """Should sanitize XSS attempts"""
    xss_payload = "<script>alert('xss')</script>"
    response = client.post(
        "/api/v1/comments",
        json={"text": xss_payload}
    )
    assert response.status_code == 422

def test_rate_limiting():
    """Should enforce rate limits"""
    for i in range(100):
        response = client.get("/api/v1/public")
        if i < 60:
            assert response.status_code == 200
        else:
            assert response.status_code == 429

```

## Monitoring & Alerting

```python

# app/core/security_monitoring.py

import logging
from datetime import datetime

security_logger = logging.getLogger("security")

async def log_security_event(
    event_type: str,
    user_id: Optional[int],
    details: dict,
    severity: str = "INFO"
):
    """Log security events for monitoring"""
    event = {
        "timestamp": datetime.utcnow().isoformat(),
        "type": event_type,
        "user_id": user_id,
        "severity": severity,
        "details": details
    }

    security_logger.log(
        getattr(logging, severity),
        f"Security event: {event_type}",
        extra=event
    )

    # Alert on critical events
    if severity in ["ERROR", "CRITICAL"]:
        await send_alert_to_ops(event)


# Usage

await log_security_event(
    "failed_login_attempt",
    user_id=None,
    details={"email": email, "ip": request.client.host},
    severity="WARNING"
)

await log_security_event(
    "privilege_escalation_attempt",
    user_id=current_user.id,
    details={"endpoint": request.url.path, "attempted_role": "admin"},
    severity="CRITICAL"
)

```

## Security Review Process (SOP-D)

**Every PR must include:**


1. **Security Impact Assessment**

   - What data is accessed?

   - What permissions are required?

   - What's the blast radius if compromised?


2. **Threat Model**

   - Who might attack this?

   - What would they gain?

   - How would they attack?


3. **Mitigation Evidence**

   - Tests demonstrating security controls work

   - Scan results (Bandit, Safety, etc.)

   - Manual review confirmation


4. **Incident Response Plan**

   - How to detect breach?

   - How to contain?

   - How to recover?

---

**Remember**: Security is non-negotiable. One breach can destroy years of work. When in doubt, choose the more secure option.
