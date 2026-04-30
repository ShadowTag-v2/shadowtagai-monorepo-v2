---
name: resilient-backend
description: Use when building APIs, Auth flows, Server Actions, Cloud Functions, or Form handlers to ensure production readiness on Day 1.
---

# Resilient Backend — Production-Ready from Day One

> **Philosophy:** "The vibes end where the ops begin."
> **Cross-references:** `cor30-security-enforcer`, `fastapi-pro`, `firebase-basics`
> **Reference architectures:** `external_repos/dub-reference/` (Upstash rate limiting), `external_repos/resend-node/` (email alerting)

## Instructions

### 1. Rate Limiting (Day 1, Not Day N)
- Every API route, Cloud Function, and Server Action MUST be rate-limited before it ships.
- **Cloud Run / Python:** Use Google Cloud Armor WAF rules (already configured with 4 rules per AGENTS.md Core Truth).
- **Next.js / TypeScript:** Use Upstash Redis rate limiter. Reference implementation in `external_repos/dub-reference/apps/web/lib/api/`.
- Rate limit by IP, user, AND endpoint. Triple-layer is the minimum.

### 2. Session & Auth Hygiene
- Firebase Auth sessions must enforce strict `maxAge` timeouts.
- Stale cafe-laptop sessions must be invalidated automatically — never leave zombie sessions.
- All auth flows must use Firebase Auth or managed providers only (per Security Rule #8).
- Token lifecycle: short-lived access tokens (15-60 min), rotating refresh tokens.

### 3. Silent Failure Prevention (The "Lead Form" Rule)
- Every data mutation, form handler, and webhook must be wrapped in structured error handling:
  - **Python:** `try/except` with `logging.error()` + structured JSON payload.
  - **TypeScript:** `try/catch` with console.error + optional Resend email alert for critical paths.
- The catch block MUST:
  1. Log the full error context (request path, user ID, timestamp, stack trace).
  2. Return a user-friendly error response (RFC 9457 format).
  3. For critical paths (payments, auth, lead capture): trigger an alert (Cloud Monitoring, Resend email, or PagerDuty).
- **NEVER** swallow an error with an empty catch block. Zero silent failures.

### 4. Input Validation (Trust Nothing)
- All inputs validated with Pydantic (Python) or Zod (TypeScript). Never trust user input.
- Never return raw database objects. Serialize and select fields explicitly.
- Parameterized queries only. Never concatenate user input into queries.

### 5. Idempotency
- All mutating endpoints must be idempotent where possible.
- Use idempotency keys for payment operations (Stripe) and webhook handlers.
- Reference: `temporalio-idempotency-auditor` skill for Temporal workflows.

### 6. Health Checks & Observability
- Every service must expose a `/health` or `/healthz` endpoint.
- Structured logging (JSON format) for all production services.
- Error rates, latency percentiles (p50, p95, p99), and request counts must be observable.
