# SOC 2 Type II Certification Timeline

> **Status:** Planning Phase
> **Owner:** TBD (Compliance Lead)
> **Last Updated:** 2026-04-24

## Current State

- Product copy hardened to "SOC 2 audit-ready" (commit `635b3e8e93`)
- Zero unqualified compliance claims in marketing or product
- Risk #86 opened in `RISK_REGISTER.md`

## Readiness Assessment

### Controls Already Implemented
- [x] Encrypted secrets via GCP Secret Manager (no `.env` files)
- [x] HMAC webhook signature verification (Stripe)
- [x] RBAC with tenant isolation (Firestore namespacing)
- [x] Betterleaks pre-commit secret scanning
- [x] Structured logging (no PII in logs)
- [x] RFC 9457 error responses (no stack traces)
- [x] Rate limiting (per-user, per-route, per-IP)
- [x] CSP / HSTS / CSRF protections
- [x] Short-lived access tokens (15-60 min)

### Controls Pending
- [ ] Formal access review process (quarterly)
- [ ] Vendor risk assessment documentation
- [ ] Business continuity / disaster recovery tested
- [ ] Firestore backup + restore drill completed
- [ ] Penetration test by third party
- [ ] Employee security training records
- [ ] Change management approval workflow documented

## Proposed Timeline

| Milestone | Target Date | Status |
|-----------|-------------|--------|
| Engage SOC 2 auditor (shortlist) | Q2 2026 | ⬜ Not started |
| Readiness assessment | Q3 2026 | ⬜ Not started |
| Gap remediation | Q3 2026 | ⬜ Not started |
| Type II observation window begins | Q4 2026 | ⬜ Not started |
| Type II audit report issued | Q1 2027 | ⬜ Not started |
| Certification achieved | Q1 2027 | ⬜ Not started |

## Auditor Shortlist

| Firm | Specialization | Notes |
|------|---------------|-------|
| Vanta | Automated SOC 2 | SaaS-native, continuous monitoring |
| Drata | Compliance automation | Good for startups |
| Secureframe | SOC 2 + HIPAA | Dual certification possible |
| KPMG | Big 4 | Enterprise credibility |

## Budget Estimate

- **Automated platform (Vanta/Drata):** $15K-25K/year
- **Auditor fees:** $20K-50K (Type II)
- **Total Year 1:** ~$35K-75K

## Notes

- Update product copy to reflect actual certification date once achieved
- Consider SOC 2 + HIPAA bundle if healthcare vertical materializes
- Vanta/Drata can pre-validate controls before formal audit
