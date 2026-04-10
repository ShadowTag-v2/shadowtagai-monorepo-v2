# Security Documentation

## Overview

ShadowTag-v2 FastAPI Services is built with **security-first architecture**. This document outlines security features, best practices, and deployment guidelines.

---

## Security Features Implemented

### 1. Authentication & Authorization ✅

#### JWT-Based Authentication
- **Algorithm**: HS256 (configurable)
- **Token Types**:
  - Access tokens (short-lived, 30 min default)
  - Refresh tokens (long-lived, 7 days default)
- **Token Rotation**: Refresh token endpoint for secure rotation
- **Claims Validation**: Type, expiration, and issuer validation

**Location**: `app/core/security.py`

#### Password Security
- **Hashing**: Bcrypt with cost factor 12
- **Strength Requirements**:
  - Minimum 12 characters
  - At least one uppercase letter
  - At least one lowercase letter
  - At least one digit
  - At least one special character
- **Protection**: Timing-safe comparison prevents timing attacks

**Location**: `app/core/security.py:hash_password`, `app/core/security.py:validate_password_strength`

#### Account Protection
- **Failed Login Tracking**: Automatic tracking of failed attempts
- **Account Locking**: Locks after 5 failed attempts
- **Soft Delete**: Preserves audit trail when accounts are deleted

**Location**: `app/models/user.py:User`, `app/api/v1/endpoints/auth.py:login`

---

### 2. Input Validation ✅

#### Pydantic Schemas
- **Type Safety**: All inputs validated via Pydantic
- **Length Limits**: Maximum lengths enforced on all string fields
- **Email Validation**: RFC-compliant email validation
- **XSS Prevention**: Dangerous characters stripped from user inputs

**Location**: `app/schemas/user.py`, `app/schemas/auth.py`

#### SQL Injection Prevention
- **ORM-Only**: SQLAlchemy ORM used exclusively (no raw SQL)
- **Prepared Statements**: All queries use parameterized statements
- **Type Safety**: Database models enforce type constraints

**Location**: `app/models/user.py`, `app/models/subscription.py`

---

### 3. Middleware Security ✅

#### Security Headers
Implementation of OWASP-recommended headers:

| Header | Value | Purpose |
|--------|-------|---------|
| `Content-Security-Policy` | Strict CSP | Prevents XSS, injection attacks |
| `X-Content-Type-Options` | nosniff | Prevents MIME sniffing |
| `X-Frame-Options` | DENY | Prevents clickjacking |
| `X-XSS-Protection` | 1; mode=block | Legacy XSS protection |
| `Strict-Transport-Security` | 1 year | Forces HTTPS |
| `Referrer-Policy` | strict-origin-when-cross-origin | Privacy protection |
| `Permissions-Policy` | Restricted features | Disables unnecessary browser APIs |

**Location**: `app/middleware/security_headers.py`

#### CORS Configuration
- **Whitelist-Only**: No wildcard origins in production
- **Validation**: Origins validated at startup
- **Credentials**: Supports credentials with specific origins only

**Location**: `app/main.py`, `app/core/config.py:ALLOWED_ORIGINS`

#### Rate Limiting
- **Per-Minute**: 60 requests/minute (default)
- **Per-Hour**: 1000 requests/hour (default)
- **Protection**: Prevents brute force and DoS attacks
- **Response**: 429 Too Many Requests with Retry-After header

**Location**: `app/middleware/rate_limit.py`

**Production Note**: Replace in-memory rate limiter with Redis for multi-instance deployments.

---

### 4. Secrets Management ✅

#### Environment Variables
- **No Hardcoded Secrets**: All secrets via environment variables
- **Validation**: Pydantic settings validate secrets at startup
- **Minimum Strength**: SECRET_KEY must be 32+ characters
- **Example File**: `.env.example` provided (never commit `.env`)

**Critical Settings**:
```bash
SECRET_KEY="<MUST-BE-32-CHARS-MIN>"
DATABASE_URL="postgresql+asyncpg://..."
STRIPE_SECRET_KEY="sk_live_..."
```

**Location**: `app/core/config.py`, `.env.example`

#### Secret Key Generation
```bash
python -c 'import secrets; print(secrets.token_urlsafe(32))'
```

---

### 5. Data Protection ✅

#### Sensitive Data Handling
- **Password Storage**: Only bcrypt hashes stored (never plaintext)
- **Token Storage**: Tokens never persisted in database
- **Response Filtering**: Sensitive fields excluded from API responses
- **Logging**: Passwords/tokens redacted from logs

**Location**: `app/schemas/user.py:UserResponse`, `app/utils/logger.py:sanitize_log_data`

#### Database Security
- **Connection Pooling**: Limits concurrent connections
- **Timeout Protection**: Query timeouts prevent resource exhaustion
- **SSL Support**: PostgreSQL SSL connections supported
- **Audit Trail**: `created_at`, `updated_at`, `deleted_at` on all models

**Location**: `app/db/session.py`

---

### 6. Error Handling ✅

#### Production Error Responses
- **No Stack Traces**: Stack traces only in debug mode
- **Generic Messages**: Generic "Internal Server Error" in production
- **Detailed Logging**: Full errors logged server-side
- **Validation Errors**: Clear validation errors without exposing internals

**Location**: `app/main.py:exception_handlers`

---

## OWASP Top 10 Mitigation

| OWASP Risk | Mitigation | Status |
|------------|------------|--------|
| **A01: Broken Access Control** | JWT authentication, tier-based authorization | ✅ |
| **A02: Cryptographic Failures** | Bcrypt password hashing, HTTPS enforcement | ✅ |
| **A03: Injection** | SQLAlchemy ORM, Pydantic validation | ✅ |
| **A04: Insecure Design** | Security-first architecture, threat modeling | ✅ |
| **A05: Security Misconfiguration** | Secure defaults, validation at startup | ✅ |
| **A06: Vulnerable Components** | Dependency pinning, regular updates | ⚠️ |
| **A07: Authentication Failures** | Account locking, rate limiting, strong passwords | ✅ |
| **A08: Data Integrity Failures** | Input validation, signature verification | ✅ |
| **A09: Logging Failures** | Structured logging, audit trail | ✅ |
| **A10: SSRF** | No user-controlled URLs, input validation | ✅ |

⚠️ **Action Required**: Set up automated dependency scanning (Dependabot, Snyk)

---

## Deployment Security

### Prerequisites

1. **Generate Strong Secret Key**:
   ```bash
   python -c 'import secrets; print(secrets.token_urlsafe(32))'
   ```

2. **Configure Environment Variables**:
   ```bash
   cp .env.example .env
   # Edit .env with production values
   ```

3. **Database Setup**:
   ```bash
   # Create PostgreSQL database
   createdb ShadowTag-v2_db

   # Run migrations (future: use Alembic)
   # For now, tables auto-created on startup
   ```

### Docker Deployment

#### Local Development
```bash
docker-compose up -d
```

#### Production Build
```bash
# Build
docker build -t ShadowTag-v2-api:latest .

# Run
docker run -d \
  --name ShadowTag-v2-api \
  -p 8000:8000 \
  --env-file .env \
  ShadowTag-v2-api:latest
```

### Google Cloud (GKE) Deployment

#### 1. Build and Push to GCR
```bash
# Authenticate
gcloud auth configure-docker

# Build
docker build -t gcr.io/YOUR_PROJECT_ID/ShadowTag-v2-api:v1.0.0 .

# Push
docker push gcr.io/YOUR_PROJECT_ID/ShadowTag-v2-api:v1.0.0
```

#### 2. Create GKE Cluster
```bash
gcloud container clusters create ShadowTag-v2-cluster \
  --region us-central1 \
  --num-nodes 3 \
  --machine-type n1-standard-2 \
  --enable-autoscaling \
  --min-nodes 2 \
  --max-nodes 10
```

#### 3. Create Kubernetes Secret
```bash
kubectl create secret generic ShadowTag-v2-secrets \
  --from-literal=SECRET_KEY="your-secret-key" \
  --from-literal=DATABASE_URL="postgresql+asyncpg://..." \
  --from-literal=STRIPE_SECRET_KEY="sk_live_..."
```

#### 4. Deploy Application
```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ShadowTag-v2-api
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: api
        image: gcr.io/YOUR_PROJECT_ID/ShadowTag-v2-api:v1.0.0
        envFrom:
        - secretRef:
            name: ShadowTag-v2-secrets
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
```

Apply:
```bash
kubectl apply -f k8s/deployment.yaml
```

---

## Security Checklist

### Before Production Deployment

- [ ] **SECRET_KEY** changed from default (32+ chars)
- [ ] **DATABASE_URL** uses SSL (`?sslmode=require`)
- [ ] **ALLOWED_ORIGINS** contains exact origins (no wildcards)
- [ ] **DEBUG** set to `false`
- [ ] **Stripe keys** use `sk_live_` (not test keys)
- [ ] **HTTPS** enforced (HSTS enabled)
- [ ] **API docs** disabled in production (`/docs`, `/redoc`)
- [ ] **Rate limiting** tested and tuned
- [ ] **Database backups** configured
- [ ] **Logging** sent to GCP Cloud Logging
- [ ] **Secrets** stored in GCP Secret Manager (not env files)
- [ ] **Container** scanned for vulnerabilities
- [ ] **Dependencies** updated and scanned

### Ongoing Security

- [ ] **Rotate SECRET_KEY** every 90 days
- [ ] **Update dependencies** monthly
- [ ] **Review logs** for suspicious activity
- [ ] **Scan for vulnerabilities** weekly
- [ ] **Audit user accounts** quarterly
- [ ] **Test disaster recovery** quarterly
- [ ] **Penetration testing** annually

---

## Security Incident Response

### If Breach Suspected

1. **Isolate**: Scale down to 0 replicas immediately
   ```bash
   kubectl scale deployment ShadowTag-v2-api --replicas=0
   ```

2. **Investigate**: Review logs in GCP Cloud Logging
   ```bash
   gcloud logging read "resource.type=k8s_container AND resource.labels.container_name=api"
   ```

3. **Rotate Secrets**: Generate new SECRET_KEY, rotate database credentials
4. **Notify Users**: If user data compromised, follow breach notification requirements
5. **Patch**: Fix vulnerability, deploy patched version
6. **Post-Mortem**: Document incident, update security procedures

### Contact

**Security Issues**: Report to security@ShadowTag-v2.com (replace with actual email)

---

## Future Security Enhancements

### Recommended Additions

1. **Redis Rate Limiting**: Replace in-memory limiter for multi-instance
2. **2FA/MFA**: Add two-factor authentication option
3. **OAuth2 Providers**: Google, GitHub login
4. **Audit Logging**: Detailed audit trail for all actions
5. **Anomaly Detection**: ML-based fraud detection
6. **WAF**: Web Application Firewall (GCP Cloud Armor)
7. **Secret Rotation**: Automatic secret rotation
8. **SIEM Integration**: Security Information and Event Management
9. **Penetration Testing**: Regular third-party security audits
10. **Bug Bounty**: Public security researcher program

---

## Compliance

### Current Status

- ✅ **OWASP Top 10**: Mitigated
- ⚠️ **GDPR**: Partial (right to deletion implemented, data export needed)
- ⚠️ **PCI DSS**: Stripe handles payments (PCI compliance via Stripe)
- ⚠️ **SOC 2**: Not certified (GCP is SOC 2 compliant)

### For Full Compliance

Consult legal counsel and compliance specialists for:
- GDPR data export and consent management
- HIPAA (if handling health data)
- SOC 2 Type II certification
- ISO 27001 certification

---

## Security Architecture Diagram

```
┌─────────────────────────────────────────────────┐
│  Client (Browser/Mobile)                        │
│  - HTTPS Only                                   │
│  - JWT Tokens                                   │
└───────────────┬─────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────┐
│  GCP Load Balancer                              │
│  - SSL Termination                              │
│  - DDoS Protection                              │
└───────────────┬─────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────┐
│  GKE Cluster (Kubernetes)                       │
│  ┌───────────────────────────────────────────┐ │
│  │  FastAPI Pods (3+ replicas)               │ │
│  │  - Rate Limiting                          │ │
│  │  - Security Headers                       │ │
│  │  - JWT Verification                       │ │
│  │  - Input Validation                       │ │
│  └───────────────┬───────────────────────────┘ │
└──────────────────┼─────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│  Cloud SQL (PostgreSQL)                         │
│  - SSL Connections                              │
│  - Automated Backups                            │
│  - Private IP                                   │
└─────────────────────────────────────────────────┘
```

---

## Contact & Support

- **Security Issues**: security@ShadowTag-v2.com
- **Documentation**: See `README.md`
- **Support**: support@ShadowTag-v2.com

**Last Updated**: 2025-11-17
**Version**: 1.0.0