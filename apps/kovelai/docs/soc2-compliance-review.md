# SOC 2 Evidence Review — Compliance Counsel Briefing

> **Item #21**: Review SOC 2 evidence with compliance counsel.

---

## Overview

KovelAI has implemented automated SOC 2 Type II evidence collection covering four Trust Services Criteria. This document is prepared for review by compliance counsel.

---

## Evidence Collection Framework

| TSC | Control | Evidence Type | Path |
|-----|---------|--------------|------|
| CC6.1 | Encryption at Rest | Automated | `lib/crypto/byok-client.ts` — AES-256-GCM |
| CC6.3 | Network Security | Automated | `lib/security/cloud-armor.ts` — OWASP CRS v3.3 |
| CC6.6 | Access Controls | Automated | `lib/auth/seu-token.ts` — S.E.U. sandbox binding |
| CC7.2 | Monitoring | Semi-automated | `lib/compliance/soc2-evidence.ts` — Evidence collector |

---

## What Compliance Counsel Should Verify

### 1. Data Classification
- [ ] Confirm all client search queries are classified as **CONFIDENTIAL** under Heppner doctrine
- [ ] Confirm Kovel attestation receipts are classified as **PRIVILEGED**
- [ ] Confirm intent vault signals are classified as **INTERNAL** (aggregated, no PII)

### 2. Retention Policies
- [ ] 30-day GDPR TTL on all ephemeral session data — CORRECT?
- [ ] Kovel receipts retained indefinitely (hash-only) — CORRECT?
- [ ] SOC 2 evidence artifacts retained for 7 years — CORRECT?

### 3. Access Controls
- [ ] S.E.U. tokens: 300-second TTL, single-use, IP-bound — SUFFICIENT?
- [ ] Dead Man's Switch: 5-minute inactivity timeout — ACCEPTABLE for Bar Association?
- [ ] BYOK: Client-side AES-256-GCM with PBKDF2 (600K iterations) — MEETS standard?

### 4. Incident Response
- [ ] Current response time target: 24 hours for security incidents
- [ ] Notification path: Cloud Monitoring → Gmail API → Partner email
- [ ] Counsel to define: What constitutes a reportable incident vs. operational event?

### 5. Third-Party Assessment
- [ ] Recommend SOC 2 Type II assessor (CPA firm)?
- [ ] Target assessment window: Q3 2026?
- [ ] Pre-assessment readiness review needed?

---

## Open Questions for Counsel

1. Does our Kovel attestation receipt (SHA-256 content hash + HMAC-SHA256 integrity code) meet the evidentiary standard for proving privilege attachment?

2. Under the Heppner framework, is our 30-day GDPR retention window for ephemeral data sufficient, or should we implement immediate deletion upon session close?

3. For the CLE certificate module — what jurisdiction-specific requirements (MCLE, CLE) must we meet for accreditation?

4. Do we need a separate Data Processing Agreement (DPA) for each law firm, or can we use a standard DPA template?

5. Should the SOC 2 report be shared with client firms, or is a SOC 2 attestation letter sufficient?

---

## Next Steps

1. Schedule 60-min review call with compliance counsel
2. Provide access to evidence collection test suite
3. Draft DPA template for counsel review
4. Identify SOC 2 Type II assessor candidates
5. Prepare evidence package for pre-assessment

---

*Prepared by KovelAI Engineering. For compliance counsel eyes only.*
