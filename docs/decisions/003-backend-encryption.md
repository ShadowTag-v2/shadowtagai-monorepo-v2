# ADR 003: Application-Layer Encryption for Privileged Content

**Status:** DECIDED
**Date:** 2026-04-22
**Deciders:** @pikeymickey, Antigravity Agent

## Context

CounselConduit streams privileged legal communications and PII over AG-UI SSE events. TLS alone is insufficient because:
1. TLS terminates at the Cloud Run load balancer/proxy
2. Internal GCP networking may route through intermediate services
3. Kovel privilege attestation requires cryptographic proof of communication integrity
4. OWASP LLM02 (Sensitive Info Disclosure) mandates defense-in-depth

## Decision

**All AG-UI event payloads containing PII or privileged content MUST be encrypted at the application layer before SSE encoding.**

### Three-Tier Encryption

| Tier | Scope | Method | Key Management |
|------|-------|--------|----------------|
| T1: Transport | All traffic | TLS 1.3 | Managed by GCP (automatic) |
| T2: Application | PII-bearing SSE events | Fernet (AES-128-CBC + HMAC) | Per-session key via Secret Manager |
| T3: Attestation | Kovel privilege receipts | HMAC-SHA256 | Rotating attestation key |

### Sensitive Event Classification

| AG-UI Event | Encrypted? | Reason |
|-------------|-----------|--------|
| `RUN_STARTED` | ❌ | Metadata only |
| `TEXT_MESSAGE_CONTENT` | ✅ | May contain privileged legal content |
| `TOOL_CALL_ARGS` | ✅ | Tool arguments may contain PII |
| `TOOL_CALL_END` | ✅ | Tool results may contain case data |
| `STATE_DELTA` | ✅ | State may contain user data |
| `RUN_FINISHED` | ❌ | Token counts only |

## Consequences

- Per-session Fernet keys stored in Firestore with 1-hour TTL
- Client retrieves session key via authenticated `/session/key` endpoint
- HMAC-SHA256 Kovel attestation receipts generated per privileged session
- PII patterns stripped from all log output (SSN, email, phone, credit card)
- Attestation key rotated monthly via GCP Secret Manager

## References

- Cor.30 Security Doctrine
- OWASP LLM Top 10 (2025)
- United States v. Kovel, 296 F.2d 918 (2d Cir. 1961)
- `skills/agent-encryption-doctrine/SKILL.md`
