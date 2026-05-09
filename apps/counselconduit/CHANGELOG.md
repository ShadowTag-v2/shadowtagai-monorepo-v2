# Changelog

All notable changes to CounselConduit are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Empathy templates expanded from 24 → 36 variants (domain-specific coverage)
- OpenAPI 3.1 specification for all 33+ endpoints
- CHANGELOG.md (this file)
- ELEVATOR_PITCH.md, CLE_SEMINAR.md, PERPLEXITY_PARADIGM.md, DIGITAL_PRIVILEGE_SHIELD.md
- VALUATION.md v3.0 with SaaS comparables and IP asset inventory
- FRONTEND_SCOPE.md with Invisible Meter, warm handoff, and session recap specs
- V11_SPRINT.md sprint plan
- S.E.U./LiteLLM round-trip integration test

## [10.0.0] - 2026-04-22

### Added
- **S.E.U. Framework** — Safety → Empathy → Utility ordering for all client-facing LLM responses
- `empathy_templates.py` — 24 randomized empathy openers, warm closes, check-ins, one-more-thing hooks
- `wrap_seu_prompt()` — S.E.U. prompt wrapper composing Safety + Empathy + Utility layers
- `fingerprint_output()` — Post-generation empathy fingerprinting (Risk #63 mitigation)
- 24 S.E.U. conformance tests (all passing)
- BUSINESS_CONTEXT_LOCKED.md v10.0 — Hard Redesign with full emotional arbitrage + S.E.U. architecture
- Emotional Arbitrage pricing model integrated into spec docs

### Changed
- `oracle_studio.py` — S.E.U. wrapper integration with 7-stage pipeline
- `dispatch_router.py` — Empathy layer injection for all dispatch paths
- `vent_mode.py` — S.E.U. ordering applied to emotional release valve responses
- PRICING.md v2.0 — Updated with attorney tier structure and emotional arbitrage framing
- MVP.md v2.0 — Reframed around emotional arbitrage thesis

## [3.2.0] - 2026-04-18

### Added
- `ucmj_discipline.py` — UCMJ discipline enforcement module
- `null_model_validator.py` — Null model validation guard
- `blast_radius.py` — Blast radius assessment for model failures
- `silent_detector.py` — Dead-Man's Switch silence detection
- OG Social Images (`og-image-shield.png`, `og-kovelai.png`)
- CSP headers hardened across Firebase Hosting
- Dependabot configuration
- 68/68 structural tests passing

### Changed
- Lighthouse scores improved: P93+ / A93+ / BP100 / SEO100
- Pre-commit hooks expanded: Gitleaks + Ruff + Bandit + detect-private-key

## [3.1.0] - 2026-04-18

### Added
- **IaC**: OpenTofu 1.11.6 with 13 resources provisioned
- **Secret Management**: 23 secrets in GCP Secret Manager, 9 imported to OpenTofu state
- API Key restriction enforcement
- GCA Batch Reviewer + Pre-push GCA Hook
- SM-First Auth pattern
- OTEL sampling configuration
- Lighthouse CI integration
- Cloud Build pipeline
- Staging branch deployment
- Email alert channels (9 policies)
- Cloud Scheduler for GDPR cleanup cron
- Firestore backup automation
- PubSub topic for event processing
- Production Runbook
- Secret rotation procedures
- Heartbeat tests
- 10 PRs resolved + auto-merge

## [3.0.0] - 2026-04-18

### Added
- **25-Rule Security Contract** (Cor.30 v2.5)
- 15 security defaults enforced
- Headless CLI Protocol
- Canary traffic split on Cloud Run
- GDPR cleanup cron job
- OpenTelemetry integration
- Cloud Armor WAF (`counselconduit-waf`)

### Changed
- Cloud Run revision: `counselconduit-00010-s74` (100% traffic)
- Mobile networking spec finalized

## [2.0.0] - 2026-04-18

### Added
- Google Workspace alerts (Gmail API + Chat API)
- Secret Manager migration (from .env to SM-first)
- Terraform IaC foundation
- `gws` CLI integration
- Org-level storage policy
- GCS lifecycle rules
- Deployment runbook

## [1.0.0] - 2026-04-16

### Added
- **Core API**: FastAPI on Cloud Run with JWT auth
- Firebase Auth integration
- Docker containerization
- Video compression pipeline
- Transcript viewer
- GDPR export UI
- Dead-Man's Switch
- Attorney onboarding flow
- Intake summarizer
- Webhook signatures (HMAC)
- Mobile spec
- Session heartbeat
- CSP + Permissions-Policy headers
- WebP image optimization
- Custom 404 pages
- DNS prefetch configuration
- Preview channels
- Google Search Console integration
- Firebase Storage
- GCS CORS configuration
- Cloud Monitoring (9 alert policies)
- `captureLead()` frontend function
- Hero video preload
- Git SSH authentication
