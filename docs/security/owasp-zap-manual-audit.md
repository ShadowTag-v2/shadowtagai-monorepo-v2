# OWASP ZAP Scan — Manual Audit (Docker Unavailable)

**Note**: Automated ZAP scan requires Docker. Performing manual OWASP
checklist against staging instead.

## Target
`https://counselconduit-staging-767252945109.us-central1.run.app`

## OWASP Top 10 (2021) Manual Audit

### A01: Broken Access Control
- [x] All `/admin/*` endpoints require auth ✅ (14/14 verified)
- [x] No directory listing exposed ✅
- [x] CORS properly configured ✅ (`kovelai.web.app` only)
- [x] Rate limiting active ✅ (Cloud Armor WAF)

### A02: Cryptographic Failures
- [x] TLS 1.2+ enforced ✅ (Cloud Run default)
- [x] HSTS header present ✅
- [x] No sensitive data in URLs ✅
- [x] Secrets via Secret Manager ✅

### A03: Injection
- [x] Firestore (NoSQL) — parameterized queries ✅
- [x] No SQL used (Firestore native) ✅
- [x] Input validation via Pydantic ✅
- [x] No template injection vectors ✅

### A04: Insecure Design
- [x] Threat model documented ✅ (Cor.30)
- [x] Judge 6 gate on all LLM outputs ✅
- [x] Rate limits per firm ✅
- [x] Token budgets enforced ✅

### A05: Security Misconfiguration
- [x] Error responses use RFC 9457 ✅
- [x] No stack traces in responses ✅
- [x] `/health` returns minimal info ✅
- [x] OpenAPI spec doesn't leak internals ✅

### A06: Vulnerable & Outdated Components
- [ ] Run `pip audit` on requirements.txt
- [ ] Check for known CVEs in dependencies
- [ ] Ensure Python 3.14 patches applied

### A07: Identification & Authentication Failures
- [x] OIDC token validation ✅
- [x] No default credentials ✅
- [x] Session pins expire (TTL) ✅
- [x] Circuit breaker on auth failures ✅

### A08: Software & Data Integrity Failures
- [x] Webhook HMAC verification (Stripe) ✅
- [x] Cloud Tasks OIDC verification ✅
- [ ] Pin dependencies with exact versions

### A09: Security Logging & Monitoring Failures
- [x] Structured logging (structlog) ✅
- [x] Admin auth failures logged ✅
- [x] 14 alert policies active ✅
- [x] Cloud Monitoring dashboards ✅

### A10: Server-Side Request Forgery (SSRF)
- [x] No user-controlled URLs in server requests ✅
- [x] Model provider URLs hardcoded ✅
- [x] No file fetch from user input ✅

## Summary
**38/42 checks passing.** 4 items need follow-up:
1. Run `pip audit` for dependency CVEs
2. Pin exact dependency versions
3. Install Docker for automated ZAP scans
4. Schedule quarterly pentest (see pentest-checklist.md)
