# CHANGELOG — Monorepo-Uphillsnowball

All notable changes to the ShadowTag-v2 monorepo.

## [v9.3] — 2026-04-18

### Canonicalization (Stage 3)
- **Truth Surface Alignment**: AGENTS.md + monorepo_manifest.yaml updated from v8.6 → v9.3
- **Version Parity**: All 6 truth surfaces now internally consistent
- **Stale Branches**: `feat/agent-external-43` + `feat/gca-multi-agent-review` deleted from remote
- **Test Count**: Corrected from "55/55" → "77 passed, 5 E2E skipped"
- **API Modules**: Updated from 16 → 33

### Hardening (Stage 4)
- **GitHub App PEM Exclusive**: `gh auth login` / PATs / deploy keys prohibited
- **PEM Canonical Path**: `~/Downloads/antigravity-shadowtag-manager.2026-03-17.private-key.pem`
- **Vulture Exclusions**: `external_repos/`, `control/legacy_workspaces/`, `reference_architectures/` added
- **Ruff 0.11.8**: 1211 total violations, 33 F401 (down from 340)
- **Bandit**: 0 high / 0 medium on CounselConduit (4,402 LOC)
- **Pre-commit**: Gitleaks v8.22.1 + Ruff v0.11.8 + Bandit v1.8.3 + detect-private-key
- **Merge Conflict**: `.agent/hybrid_scraper.py` resolved
- **SOVEREIGN_GOLD_MASTER**: Updated to latest HEAD

### CI/CD
- **GCA PR Review**: Security + perf agent prompts inlined (removed $BUNDLE dependency)
- **WebPageTest CI**: `.github/workflows/webpagetest-ci.yml` created

---

## [v9.0] — 2026-04-18

### Infrastructure
- **OpenTofu**: 19 resources provisioned (IAM bindings, log metric, alert policy)
- **Secret Manager**: 23 secrets total, 9 imported to IaC state
- **API Key Restriction**: Key 2 narrowed from 72 → 16 APIs
- **Cloud Scheduler**: `firestore-backup-verify` daily probe
- **Cloud Armor**: Rate limit rule (100 req/min/IP, 5min ban)
- **Firestore Alerts**: Read (10K/5min) + Write (5K/5min) policies
- **Email Channel**: `founder@shadowtagai.com` wired to 9 alert policies
- **PubSub**: `secret-rotation-notifications` topic

### CI/CD
- **GCA Batch Reviewer**: `scripts/run_gca_batch.py` — batch PR review + auto-merge
- **GCA CI Fallback**: `.github/workflows/gca-review.yml` — 4-agent Gemini review
- **Pre-push Hook**: GCA advisory gate with soft-fail relock
- **Cloud Build**: `cloudbuild.yaml` + `cloudbuild-staging.yaml` (source-based)
- **Staging Branch**: Created and synced to origin
- **Dependabot**: `.github/dependabot.yml` with grouped minor/patch updates
- **Lighthouse CI**: `.lighthouserc.json` budget gates (P90/A90/BP100/SEO100)

### Auth & Security
- **SM-First PEM**: `auth_github_app.py` 5-tier fallback (SM → local → env)
- **OTEL Sampling**: `OTEL_TRACE_SAMPLING_RATE` configurable (10% default)
- **Cloud Armor Rate Limit**: 100 req/min per IP
- **Bandit**: 0 high-severity findings on production code

### Code
- `tests/test_heartbeat.py`: 4 new tests (TTL, dead-man's switch, rate limit)
- `scripts/ffmpeg_demo_record.sh`: macOS screen recording script
- `docs/PRODUCTION_RUNBOOK.md`: incident response procedures
- `docs/SECRET_ROTATION.md`: rotation procedure for 23 secrets

### Resolved
- 10 PRs closed (8 Dependabot stale, PR #48 cryptography, PR #55 incorporated)
- Auto-merge + delete-branch-on-merge enabled
- `RISK_REGISTER.md` v9.0 (29 entries)
- `BUSINESS_CONTEXT_LOCKED.md` v9.0

### Tests
- **68/68** passed (4 new heartbeat tests)

---

## [v8.0] — 2026-04-18

### Infrastructure
- **Cloud Run**: Rev 00010-s74 on us-central1 (canary → 100%)
- **OpenTofu**: Initialized, Google provider 7.28.0
- **GDPR Cron**: Cloud Scheduler `gdpr-30day-cleanup` daily 02:00 UTC
- **OpenTelemetry**: Cloud Trace OTLP exporter wired into FastAPI

### Security
- **25-Rule Security Contract**: AGENTS.md (auth, validation, secrets)
- **15 Security Defaults**: Tokens, CORS, CSP, HSTS, rate limits
- **Headless CLI Protocol**: PTY Buffer Trap prevention
- **Cloud Armor WAF**: XSS + SQLi rules active

### Deliverables
- Staging `.env.example` (37 variables)
- Mobile Networking Spec (Flutter/Dio 6-interceptor stack)
- OAuth Desktop Client fix (redirect_uri_mismatch)
- 40 reference repos cloned (gitignored)
- Lighthouse: P93 / A93 / BP100 / SEO100

---

## [v7.0] — 2026-04-18

### Infrastructure
- **Google Workspace Alerts**: Gmail + Chat API replace Discord + Resend
- **Secret Manager Migration**: 20+ secrets from .env to SM
- **Terraform IaC**: `infra/terraform/secrets.tf`
- **gws CLI v0.22.5**: Agent-driven email/chat

### Security
- Org-level storage public access prevention
- GCS lifecycle: 30-day auto-delete on Cloud Build buckets
- Dead code audit: 34 unused imports fixed
- Bandit: 0 medium/high findings (4,074 LOC)

---

## [v4-5] — 2026-04-18

### Features
- Firebase Auth JWT verification
- Video compression (hero 82% smaller, sphere 83%)
- Transcript Viewer (7-stage Oracle Studio)
- GDPR Export UI (Article 20 portability)
- Dead-Man's Switch (session replay protection)
- Attorney Onboarding (4-step wizard)
- Intake Summarizer (LLM-powered)
- Webhook Signatures (Stripe + Kovel + Resend HMAC)

---

## [Production Hardening] — 2026-04-16

### Security
- CSP + Permissions-Policy on both sites
- WebP optimization (79–98% payload reduction)
- Custom 404 pages
- Firebase Storage zero-trust rules
- GCS CORS hotlink protection
- Cloud Monitoring error rate alerts
- `captureLead` v2 Cloud Function (reCAPTCHA-gated)
