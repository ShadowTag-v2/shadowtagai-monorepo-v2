# SOC 2 Type II Assessment — Scheduling Memo

## Overview

KovelAI targets SOC 2 Type II certification as a trust signal for enterprise law firm
customers. The assessment covers Trust Service Criteria (TSC) relevant to our
privilege-preserving AI router architecture.

---

## Assessor Selection

### Recommended Firms (SMB-Friendly, AI-Experienced)

| Firm | Estimated Cost | Timeline | AI Experience |
|------|---------------|----------|---------------|
| **Prescient Assurance** | $15-25K | 3 months | High — AI/SaaS startups |
| **Johanson Group** | $18-30K | 4 months | Medium — Cloud-native |
| **A-LIGN** | $25-40K | 3 months | High — Large portfolio |
| **Secureframe + Assessor** | $10-15K (platform) + $15K (audit) | 4 months | High — Automated evidence |
| **Vanta + Assessor** | $8-12K (platform) + $15K (audit) | 3 months | High — Automated evidence |

### Recommendation
**Vanta + partner assessor** — Automated evidence collection integrates directly with
GCP (Cloud Run, Firestore, Secret Manager). Reduces manual evidence gathering by ~60%.

---

## TSC Scope — KovelAI-Specific

### In Scope
| Criteria | Relevance |
|----------|-----------|
| **CC6.1 — Logical Access** | Firebase Auth + MFA gate + role-based access |
| **CC6.2 — System Authentication** | MFA enrollment for attorneys (TOTP/phone) |
| **CC6.3 — Access Revocation** | Session TTL (24h Heppner), token rotation |
| **CC7.1 — Security Monitoring** | Cloud Armor WAF + structured logging |
| **CC7.2 — Incident Response** | Dead man's switch + RKILL circuit breaker |
| **CC8.1 — Change Management** | Pre-commit hooks + CI/CD gates + Ruler drift |
| **A1.1 — Availability** | Cloud Run auto-scaling + health monitoring |
| **PI1.1 — Data Integrity** | Genesis Block SHA-256 chain + C2PA manifests |
| **P1-P8 — Privacy** | Zero-data router, GDPR TTL, ephemeral sessions |

### Out of Scope
- Physical security (Google manages Cloud Run infrastructure)
- Client data storage (zero-data architecture — we don't store client data)

---

## Pre-Audit Preparation Checklist

- [x] Structured logging operational (lib/observability/structured-logger.ts)
- [x] MFA gate deployed (lib/security/mfa-gate.ts)
- [x] Encryption at rest (Firestore default)
- [x] Encryption in transit (TLS 1.3 / HSTS)
- [x] Access control matrix documented
- [x] Incident response runbook (RKILL / Dead Man's Switch)
- [x] Change management (pre-commit + Ruler + CI)
- [ ] Data retention policy (GDPR TTL) — formalize document
- [ ] Vulnerability management program — formalize program
- [ ] Employee security training — sign-off tracker
- [ ] Risk assessment — annual cadence
- [ ] Vendor management — LLM provider risk assessments

---

## Timeline

| Phase | Date | Action |
|-------|------|--------|
| Platform Setup | 2026-05-01 | Onboard Vanta, connect GCP integrations |
| Policy Drafting | 2026-05-01–15 | Write required policies, formalize programs |
| Evidence Collection | 2026-05-15–07-15 | 2-month observation window minimum |
| Readiness Assessment | 2026-07-15 | Internal review with Vanta readiness score |
| Type II Audit Start | 2026-08-01 | Assessor engagement begins |
| Audit Complete | 2026-10-01 | Report delivered |
| Certification | 2026-10-15 | Badge on kovelai.com, share report with prospects |

---

## Budget

| Item | Cost |
|------|------|
| Vanta Annual | $10,000 |
| Assessor (Type II) | $15,000 |
| Policies + Training | $2,000 (internal effort) |
| **Total** | **$27,000** |

### ROI
- Enterprise law firm deals require SOC 2 → unlocks $20K+/mo contracts
- Payback period: 1-2 enterprise customers
