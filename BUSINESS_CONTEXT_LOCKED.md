# BUSINESS_CONTEXT_LOCKED — v9.0

## Consumer Syndicate
- Price: `$149/mo`
- Margin: `95%`
- Architecture: `Centralized Hive Mind Oracle + Stateless Micro-Edge`

## Enterprise Base SLA
- Price: `$20,000/mo`
- Margin: `69–71%`
- Core value: `Zero-latency AST risk mitigation`
- Isolation: `Dedicated GCP sidecar`

## Enterprise EU26 Premium
- Price: `$28,333/mo`
- Margin: `76–78%`
- Core value: `higher-assurance compliance and enterprise isolation posture`

## Sovereign Scale
- Customer pays `100% compute pass-through`
- Software margin retained on the base license

## Latency doctrine
- Target: `p99 <= 90ms total application path` where the architecture permits

## Architectural split
- Consumer path: centralized intelligence + stateless micro-edge
- Enterprise path: tenant-isolated sidecars + stronger controls + mTLS

## Rule
Do not mix these lanes casually. Consumer and enterprise economics are different products.

## Hardened State
- v9.0 canonicalized: 2026-04-18
- Latest production commit: `afb244705d5` (2026-04-18)
- Lighthouse LHCI (KovelAI): P93+ / A93+ / BP100 / SEO100
- Lighthouse LHCI (ShadowTagAI): P93+ / A93+ / BP96 / SEO100
- Structural tests: 68/68
- Dead code: clean (vulture + ruff) — Kosmos dead code noted, production paths clean
- CounselConduit: v3.2.0 LIVE on Cloud Run (23 API modules, 33 endpoints)
- Cloud Armor WAF: `counselconduit-waf` (XSS + SQLi + rate limiting active)
- Cloud Monitoring: 9 alert policies + email channel (17531835029676919705) + SLO burn rate alert (17434870411493760882)
- SLO: CounselConduit 99.5% Availability, 30-day rolling (service: F2cVj-pyTHmSv7dcU8LrBA, slo: -jycE9GTQGKQmincRmp3pA)
- Firestore TTL: session_pins.expire_at ACTIVE (auto-delete expired sessions)
- Security: Cor.30 v2.5 + OWASP LLM10 enforced (docs/SECURITY_DOD.md)
- Pre-commit: Gitleaks + Ruff + Bandit + detect-private-key
- Secret Manager: 23 secrets, 9 imported to OpenTofu state
- OpenTofu: 19 resources provisioned (IAM + alerts + log metrics)
- Terraform IaC: infra/terraform/counselconduit-monitoring/main.tf (339 LOC)
- RISK_REGISTER: v9.0 (35 tracked risks)
- Open PRs: 0

### CounselConduit Cloud Run (2026-04-18)
| Service | URL | Rev |
|---------|-----|-----|
| Production | https://counselconduit-767252945109.us-central1.run.app | counselconduit-00010-s74 (100% traffic) |
| Staging | https://counselconduit-staging-767252945109.us-central1.run.app | counselconduit-staging-00003-l9h |

### Wave 9.3 Deliverables (2026-04-18)
- **OG Social Images**: Generated + deployed for KovelAI and ShadowTagAI (visible on Facebook/LinkedIn)
- **CSP Hardening**: Removed `unsafe-eval` + `cdn.tailwindcss.com` from both sites
- **Lighthouse BP 100**: Fixed favicon 404s → console errors eliminated
- **New Modules**: `silent_detector.py`, `blast_radius.py`, `null_model_validator.py`, `ucmj_discipline.py`
- **Dead Code**: `discord_alerts.py` deleted (replaced by `workspace_alerts.py`)
- **Dependabot**: `.github/dependabot.yml` — weekly grouped updates
- **CHANGELOG.md**: Complete Wave 4→9 history
- **Tests**: 68/68 passed (0 skipped)
- **API Modules**: 33 total
- **GEMINI.md**: v9.0
- **Git Repack**: 46GB → 33GB

### Wave 9 Deliverables (2026-04-18)
- **IaC Apply**: 13 resources created (IAM bindings + log metric + alert policy)
- **IaC Import**: 9 existing secrets imported to OpenTofu state
- **API Key Restriction**: Key 2 restricted 72→16 APIs
- **GCA Batch Reviewer**: `scripts/run_gca_batch.py` — batch Dependabot PR review + auto-merge
- **GCA CI Fallback**: `.github/workflows/gca-review.yml` — 4-agent review on PRs
- **Pre-push GCA Hook**: `.git/hooks/pre-push` — advisory gate (soft-fail relock)
- **SM-First Auth**: `auth_github_app.py` 5-tier PEM fallback (SM→keys→Downloads→.ssh→$env)
- **OTEL Sampling**: `OTEL_TRACE_SAMPLING_RATE` configurable (10% default, 100% staging)
- **Lighthouse CI**: `.lighthouserc.json` — P90/A90/BP100/SEO100 budget gates
- **Cloud Build**: `cloudbuild.yaml` + `cloudbuild-staging.yaml` (source-based deploy)
- **Staging Branch**: `staging` created + pushed to origin
- **Email Alerts**: Notification channel wired to 7 alert policies
- **Cloud Scheduler**: `firestore-backup-verify` daily 06:00 UTC health probe
- **Firestore Backup**: Daily schedule, 7d retention
- **PubSub Topic**: `secret-rotation-notifications`
- **Production Runbook**: `docs/PRODUCTION_RUNBOOK.md`
- **Secret Rotation**: `docs/SECRET_ROTATION.md`
- **Heartbeat Tests**: 4 new tests (TTL, dead-man's, rate limit)
- **FFmpeg Demo**: `scripts/ffmpeg_demo_record.sh`
- **10 PRs Resolved**: 8 Dependabot closed (head deleted), PR #48 closed, PR #55 closed (incorporated)
- **Auto-merge**: Enabled + delete-branch-on-merge for future PRs
- **Risk Register v9.0**: 4 new entries (#26-29)
- **Reference Repos**: 41 total (FFmpeg added)

### Wave 8 Deliverables (2026-04-18)
- **25-Rule Security Contract**: Non-negotiable security canon in AGENTS.md (auth, input validation, secrets)
- **15 Security Defaults**: Tokens, CORS, CSP, HSTS, rate limits, RLS, webhook HMAC, backups
- **Headless CLI Protocol**: PTY Buffer Trap prevention doctrine in GEMINI.md + SKILL.md
- **Cloud Run Rev 00010-s74**: Health probes (liveness + startup), autoscale 1-10, concurrency 80
- **Canary Traffic Split**: 90% rev-00009 / 10% rev-00010 (progressive rollout)
- **GDPR Cleanup Cron**: Cloud Scheduler `gdpr-30day-cleanup` daily 02:00 UTC (OIDC auth)
- **OpenTelemetry Cloud Trace**: telemetry.py OTLP exporter wired into FastAPI app
- **OpenTofu 1.11.6**: infra/terraform/ initialized, Google provider 7.28.0, plan: 19 resources
- **Staging .env.example**: 37-variable template for staging environment
- **Mobile Networking Spec**: Flutter/Dio 6-interceptor stack (docs/mobile_networking_spec.md)
- **OAuth Fix**: Desktop client g8e1 for gws CLI (redirect_uri_mismatch resolved)
- **Pitch-deck-agent Bucket**: Archived to ARCHIVE storage class
- **40 Reference Repos**: Terraform, Lighthouse, Flagger, OpenTofu, Semaphore (gitignored)
- **Lighthouse Post-Deploy**: P93 / A93 / BP100 / SEO100 (kovelai.web.app)
### Wave 7 Deliverables (2026-04-18)
- **Google Workspace Alerts**: Gmail API + Google Chat API replace Discord + Resend (workspace_alerts.py)
- **Secret Manager Migration**: 20+ secrets migrated from .env to Google Secret Manager
- **Terraform IaC**: infra/terraform/secrets.tf (secrets, IAM, anomaly alerts)
- **gws CLI v0.22.5**: Google Workspace CLI installed for agent-driven email/chat
- **Org-Level Storage Policy**: `constraints/storage.publicAccessPrevention` enforced
- **GCS Lifecycle**: 30-day auto-delete on Cloud Build source buckets
- **Deployment Runbook**: docs/DEPLOYMENT_RUNBOOK.md (pre-deploy, canary, rollback)
- **.gcloudignore**: Prevents 2GB Cloud Build tarball upload
- **Dead Code Audit**: 34 unused imports fixed via ruff --fix
- **Bandit Scan**: 0 medium/high severity findings across 4,074 LOC
- **Cloud Run Labels**: managed_by=opentofu, environment=production
- **Hero Videos on CDN**: Migrated to Firebase Hosting (apps/kovelai/public/videos/)
- **gcloud PATH Fix**: Cloud Code now finds Homebrew gcloud correctly
- **22 Reference Repos**: Terraform/IaC shallow clones (gitignored, 2.2 GB)

### Wave 4-5 Deliverables (2026-04-18)
- **Firebase Auth JWT**: Server-side verification via firebase-admin SDK
- **Docker Import Paths**: try/except fallbacks for monorepo vs /app/ Docker context
- **Video Compression**: hero-bg 82% smaller, sphere-holo 83% smaller (ffmpeg CRF 30-32)
- **Transcript Viewer**: 7-stage Oracle Studio viewer (transcripts.html)
- **GDPR Export UI**: Article 20 data portability page (export.html)
- **Dead-Man's Switch**: Client portal session replay protection + DevTools defeat
- **Attorney Onboarding**: 4-step wizard (firm info → plan → models → Stripe Connect)
- **Google Workspace Alerts**: Payment failure, security event, GDPR deletion (replaced Discord)
- **Intake Summarizer**: LLM-powered intake extraction for Vent Mode
- **Webhook Signatures**: Stripe + Kovel + Resend HMAC verification tests (9 tests)
- **Mobile Spec**: Flutter/Dio interceptor stack (auth, Kovel, rate limit, dead-man's switch)
- **OpenTelemetry**: Instrumentation added to requirements
- **Firestore Health**: /health endpoint verifies Firestore connectivity
- **Session Heartbeat**: /heartbeat endpoint for client keep-alive

### Production Hardening (2026-04-16)
- **CSP Headers**: Strict Content-Security-Policy deployed on both KovelAI and ShadowTagAI
- **CSP connect-src**: googletagmanager.com added to ShadowTagAI (BP 96→100 fix)
- **Permissions-Policy**: Camera, microphone, geolocation denied by default
- **WebP Optimization**: All hero/pitch images converted (79–98% payload reduction)
- **Custom 404 Pages**: Premium branded 404.html for both sites
- **DNS Prefetch**: `dns-prefetch` hints for CDN resources
- **Preview Channels**: kovelai-preview + shadowtagai-preview (7d TTL)
- **Google Search Console**: Verification meta tags added (placeholder — replace with actual codes)
- **Firebase Storage**: Initialized with zero-trust deny-all rules
- **GCS CORS**: Hotlink protection — 5 authorized origins only
- **Cloud Monitoring**: Error rate alert policy + email notification channel
- **captureLead**: ACTIVE v2 Cloud Function (reCAPTCHA-gated)
- **Hero Preload**: `<link rel="preload">` for ShadowTagAI hero image (LCP improvement)
- **Git Auth**: SSH deploy key registered via GitHub App API (write access)
- **Remote**: `git@github-shadowtag:ShadowTag-v2/Monorepo-Uphillsnowball.git`

### Deployed Hosting Targets (2026-04-16)
| Target | URL | Status |
|--------|-----|--------|
| KovelAI Live | https://kovelai.web.app | ✅ |
| ShadowTagAI Live | https://shadowtagai.web.app | ✅ |
| Default Site | https://shadowtag-omega-v4.web.app | ✅ |
| KovelAI Preview | https://kovelai--preview-8ezcbvse.web.app | ✅ 7d |
| ShadowTagAI Preview | https://shadowtagai--preview-32m75f3r.web.app | ✅ 7d |

## Webhook vs Firestore Pricing Matrix
Because we moved away from Redis cache over to Firestore `system_idempotency_keys` for Zod validation locks, high frequency polling will cost approximately $0.18 per 100k requests read/writes against the GCP document quota. We remain heavily profitable beneath the $5K Base Tier barrier. Edge Sovereign node ingress remains $0.00 bandwidth locked within our private peering subnet.

---

## Canonical Production Assets (Locked 2026-04-16)

### KovelAI Hero Video
| Property | Value |
|----------|-------|
| GCS Object | `gs://shadowtag-omega-v4-archive/hero-videos/legal-data-arch.mp4` |
| CDN Public URL | `https://storage.googleapis.com/shadowtag-omega-v4-archive/hero-videos/legal-data-arch.mp4` |
| Generation Model | `veo-3.1-generate-preview` |
| Duration | 8 seconds, seamless 4K loop |
| Visual Concept | "Abstract Data Architecture" — navy+gold neural lattice |
| Live Deployment | https://kovelai.web.app |
| Spec Document | `apps/kovelai/.stitch/kovelai-hero-video-spec.md` |

### KovelAI Design System
| Property | Value |
|----------|-------|
| Document | `apps/kovelai/DESIGN_SYSTEM.md` |
| Primary | `#0a0f1e` (deep navy) |
| Accent | `#c9a96e` (glowing gold) |
| Font | Inter 300–800 |
| Aesthetic | Structured Precision — Legal Tech |
