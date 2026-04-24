# ADR-005: Backend Encryption as Default for Agent State

**Status:** Accepted
**Date:** 2026-04-24
**Source:** TACSOP 0 (Building Websites), Cor.30 Security Rules, CounselConduit Privilege Architecture

## Context

CounselConduit handles attorney-client privileged communications. Agent state (session context, tool call results, intermediate reasoning) MUST be encrypted at rest and in transit. The question is whether encryption is opt-in or default.

## Decision

**Encryption is DEFAULT for all agent state persistence.** Opt-out requires explicit documentation with legal review.

### Encryption Layers

| Layer | Mechanism | Key Management |
|-------|-----------|----------------|
| Transit | TLS 1.3 (Cloud Run enforced) | Google-managed certificates |
| Firestore at-rest | AES-256 (Google default CMEK) | Google Cloud KMS |
| Application-level | AES-256-GCM per-tenant | Per-firm key in Secret Manager |
| Session state | Encrypted cookie + server-side | Rotating session key (15-min TTL) |
| Transcript archive | AES-256-GCM + immutable audit hash | Firm-specific archive key |

### Implementation Rules

1. **Firestore documents** in collections `transcripts/`, `sessions/`, `kovel_attestations/` MUST use application-level encryption (not just Google's default at-rest)
2. **Session state** passed via SSE MUST NOT contain raw privileged content — only encrypted references
3. **Oracle Memo output** is encrypted before Firestore write, decrypted only on authenticated read
4. **Kovel Attestation receipts** use HMAC-SHA256 with per-firm secret (already implemented in v3.2.0)
5. **LiteLLM proxy tokens** are encrypted ephemeral tokens with tenant+session+TTL binding

### Key Rotation

- Application keys rotate every 90 days via Cloud KMS automatic rotation
- Session keys rotate every 15 minutes (access token TTL)
- Archive keys rotate annually with backward-compatible decryption

## Consequences

- All Firestore write operations must include encryption step (adds ~2ms latency)
- Key management complexity increases (mitigated by Cloud KMS)
- Backup/restore procedures must include key export (documented in ops runbook)
- Performance impact is negligible (<5ms per operation)

## Alternatives Rejected

- **Opt-in encryption**: Unacceptable for privileged communications — too easy to forget
- **Client-side encryption only**: Server needs to process data for Oracle pipeline
- **Homomorphic encryption**: Not mature enough for production, prohibitive latency
