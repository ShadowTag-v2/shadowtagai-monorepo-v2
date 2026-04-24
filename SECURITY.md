# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| main    | ✅ Active          |
| < main  | ❌ Not supported   |

## Reporting a Vulnerability

**DO NOT** open a public GitHub issue for security vulnerabilities.

### Preferred Method

Email: **security@shadowtag.ai**

### What to Include

1. **Description** of the vulnerability
2. **Steps to reproduce** (proof of concept if possible)
3. **Impact assessment** — what an attacker could achieve
4. **Affected component** — which app/service/workflow

### Response Timeline

| Stage | SLA |
|-------|-----|
| Acknowledgment | 48 hours |
| Triage + severity assessment | 5 business days |
| Fix deployed (Critical/High) | 14 calendar days |
| Fix deployed (Medium/Low) | 30 calendar days |
| Public disclosure | After fix is deployed + 30 days |

### Scope

The following are **in scope**:

- `apps/counselconduit/` — CounselConduit API (Cloud Run)
- `apps/kovelai/` — KovelAI web application (Firebase Hosting)
- `apps/aiyou_stack/` — AiYou stack services
- `.github/workflows/` — CI/CD pipeline configurations
- `infra/` — Infrastructure-as-code (OpenTofu)
- Firebase Security Rules (Firestore, Storage)
- Authentication and authorization flows
- API endpoints and webhook handlers
- Stripe payment integration

The following are **out of scope**:

- `docs/` — Documentation (no runtime impact)
- `labs/` — Local R&D experiments
- `tools/GitNexus/` — Local development tooling
- `data/` — Ingested reference data
- Third-party services we don't control

### Safe Harbor

We support responsible disclosure. If you act in good faith:

- We will not pursue legal action
- We will work with you to understand and resolve the issue
- We will credit you in the advisory (unless you prefer anonymity)

### Security Controls

This repository enforces:

- **Pre-commit**: Betterleaks (Gitleaks successor) + detect-private-key + Bandit
- **CI**: CodeQL analysis, dependency review, security audit
- **Runtime**: Cloud Armor WAF, CSP headers, HSTS
- **Secrets**: GCP Secret Manager (production), kernel-locked `.env` (local)
- **Auth**: Firebase Auth + GitHub App PEM (no PATs)
- **OWASP LLM Top 10**: Prompt injection isolation, PII stripping, token budgets

### PGP Key

Not yet available. Contact security@shadowtag.ai for encrypted communication setup.
