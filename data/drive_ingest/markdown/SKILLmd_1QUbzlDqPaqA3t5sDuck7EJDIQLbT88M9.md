# Security Enforcement Skill

**Purpose:** Block code that violates ShadowTagAi security requirements
**Enforcement:** `"block"` - Prevents edits that fail security checks
**Priority:** `"critical"`
**Version:** 1.0.0

---

## Overview

This skill enforces ShadowTagAi's zero-trust security architecture and ensures all code meets military-grade security standards (Army RM Stage IV compliance). It automatically activates when you work with authentication, APIs, databases, or any code involving sensitive data.

**Auto-Activation Triggers:**
- Keywords: `auth`, `encrypt`, `secret`, `password`, `token`, `api`, `deploy`
- Files: `.ts`, `.py`, `.env`, `auth/**/*`, `api/**/*`
- Content: Detects `password`, `apiKey`, `SECRET`, database connections

---

## Mandatory Security Requirements

### 1. Encryption at Rest
**Requirement:** AES-256-GCM for ALL stored data containing sensitive information

```typescript
// ❌ BLOCKED - No encryption
await db.user.create({ data: { password: userPassword } });

// ✅ APPROVED - AES-256 encryption
import { encrypt } from '@/lib/crypto';
const encryptedPassword = await encrypt(userPassword, 'AES-256-GCM');
await db.user.create({ data: { password: encryptedPassword } });
```

**See:** [resources/encryption.md](resources/encryption.md) for implementation details

### 2. Encryption in Transit
**Requirement:** TLS 1.3 ONLY (no TLS 1.2, no HTTP)

```typescript
// ❌ BLOCKED - HTTP connection
const response = await fetch('http://api.example.com/data');

// ❌ BLOCKED - TLS 1.2
const httpsAgent = new https.Agent({ minVersion: 'TLSv1.2' });

// ✅ APPROVED - TLS 1.3
const httpsAgent = new https.Agent({
  minVersion: 'TLSv1.3',
  ciphers: 'TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256'
});
const response = await fetch('https://api.example.com/data', { agent: httpsAgent });
```

**See:** [resources/tls-config.md](resources/tls-config.md) for cipher suites

### 3. Zero-Trust Authentication
**Requirement:** EVERY service-to-service call must be authenticated

```typescript
// ❌ BLOCKED - Unauthenticated internal call
const result = await fetch('http://internal-service/data');

// ✅ APPROVED - JWT-authenticated
const token = await generateServiceToken('internal-service');
const result = await fetch('https://internal-service/data', {
  headers: { Authorization: `Bearer ${token}` }
});
```

**See:** [resources/zero-trust.md](resources/zero-trust.md) for service mesh setup

### 4. Secret Management
**Requirement:** NO secrets in code (use environment variables + Google Secret Manager)

```typescript
// ❌ BLOCKED - Hardcoded secret
const apiKey = 'YOUR_API_KEY_HERE';

// ❌ BLOCKED - Secret in config file
export const config = { apiKey: 'YOUR_API_KEY_HERE' };

// ✅ APPROVED - Environment variable
const apiKey = process.env.API_KEY;
if (!apiKey) throw new Error('API_KEY not set');

// ✅ APPROVED - Google Secret Manager
import { SecretManagerServiceClient } from '@google-cloud/secret-manager';
const client = new SecretManagerServiceClient();
const [version] = await client.accessSecretVersion({ name: 'projects/shadowtagai/secrets/api-key/versions/latest' });
const apiKey = version.payload.data.toString();
```

**See:** [resources/secrets-management.md](resources/secrets-management.md) for setup

### 5. Error Tracking
**Requirement:** ALL exceptions captured via Sentry.captureException()

```typescript
// ❌ BLOCKED - Silent failure
try {
  await riskyOperation();
} catch (error) {
  console.log('Error:', error);
}

// ✅ APPROVED - Sentry tracking
import * as Sentry from '@sentry/node';

try {
  await riskyOperation();
} catch (error) {
  Sentry.captureException(error, {
    tags: { operation: 'riskyOperation' },
    extra: { context: 'Additional debugging info' }
  });
  throw error; // Re-throw after logging
}
```

---

## Common Violations & Fixes

### Database Queries Without Parameterization

```typescript
// ❌ BLOCKED - SQL injection risk
const query = `SELECT * FROM users WHERE id = ${userId}`;
await db.$queryRaw(query);

// ✅ APPROVED - Parameterized query
await db.user.findUnique({ where: { id: userId } });
// OR with raw SQL:
await db.$queryRaw`SELECT * FROM users WHERE id = ${userId}`;
```

### Weak Password Hashing

```python
# ❌ BLOCKED - MD5/SHA1/SHA256 not sufficient
import hashlib
hashed = hashlib.sha256(password.encode()).hexdigest()

# ✅ APPROVED - Argon2id (OWASP recommended)
from argon2 import PasswordHasher
ph = PasswordHasher(
    time_cost=2,
    memory_cost=65536,
    parallelism=4,
    hash_len=32,
    salt_len=16
)
hashed = ph.hash(password)
```

### Exposed Sensitive Data in Logs

```typescript
// ❌ BLOCKED - Logging sensitive data
console.log('User logged in:', { email, password, token });
Sentry.captureMessage(`Login: ${email} ${password}`);

// ✅ APPROVED - Redacted logging
console.log('User logged in:', { email, passwordHash: '[REDACTED]' });
Sentry.captureMessage(`Login: ${email}`, {
  tags: { event: 'login' },
  // Never log passwords/tokens
});
```

---

## Progressive Disclosure Resources

Load these files for specific security topics:

- **[resources/auth-patterns.md](resources/auth-patterns.md)** - OAuth 2.0, JWT signing, refresh tokens
- **[resources/encryption.md](resources/encryption.md)** - AES-256-GCM implementation, key rotation
- **[resources/secrets-management.md](resources/secrets-management.md)** - Environment variables, Google Secret Manager
- **[resources/zero-trust.md](resources/zero-trust.md)** - Service mesh, mTLS, certificate management
- **[resources/tls-config.md](resources/tls-config.md)** - TLS 1.3 cipher suites, certificate pinning

---

## When This Skill Auto-Activates

**Keyword Triggers:**
- `auth`, `authenticate`, `authorization`
- `encrypt`, `encryption`, `decrypt`
- `secret`, `password`, `token`, `apiKey`
- `api`, `endpoint`, `deploy`, `production`
- `database`, `db`, `prisma`, `query`

**File Pattern Triggers:**
- `**/*.ts`, `**/*.py`, `**/*.js`
- `**/auth/**/*`, `**/api/**/*`
- `**/.env*`, `**/config/**/*`

**Content Pattern Triggers:**
- `password`, `apiKey`, `SECRET`, `token`
- `http://` (non-HTTPS connections)
- `prisma`, `fetch()`, `axios`

---

## Security Checklist (Before Deployment)

Use this checklist when implementing authentication/API features:

- [ ] All secrets in Google Secret Manager (not in code/config)
- [ ] All database queries parameterized (no string concatenation)
- [ ] All API calls use HTTPS with TLS 1.3
- [ ] All passwords hashed with Argon2id
- [ ] All service-to-service calls authenticated (JWT/mTLS)
- [ ] All exceptions captured with Sentry
- [ ] No sensitive data in logs (emails ok, passwords/tokens never)
- [ ] All `.env` files in `.gitignore`
- [ ] Security review completed (run `/ShadowTag-v2jr-gate`)
- [ ] Rollback plan documented (in dev docs)

---

## Integration with ShadowTag-v2JR

This skill is part of the **Brakes Gate** in the ShadowTag-v2JR decision framework:

- **Purpose:** Does this serve founder goals? → Other skills handle this
- **Reasons:** Financial validation (ROI, LTV:CAC) → Other skills handle this
- **Brakes:** Risk management (security, reversibility) → **THIS SKILL**

If this skill blocks your code, it means you're about to introduce a security vulnerability. DO NOT override without consulting security documentation.

---

## Troubleshooting

**Q: Skill blocked my code but I think it's a false positive. What do I do?**
A: Read the specific resource file for your use case. If still unclear, ask: "Load security-enforcement skill, explain why [specific code] was blocked"

**Q: I'm working on a prototype, can I skip security temporarily?**
A: No. Security violations compound. Fix it now or rewrite later. Prototypes become production code.

**Q: How do I test authentication locally without production secrets?**
A: Use `.env.development` with test credentials. Never commit this file. See [resources/secrets-management.md](resources/secrets-management.md)

---

**Last Updated:** 2025-11-15
**Maintained By:** ShadowTagAi Security Team (Erik)
**Compliance:** Army RM Stage IV, OWASP Top 10, Zero-Trust Architecture