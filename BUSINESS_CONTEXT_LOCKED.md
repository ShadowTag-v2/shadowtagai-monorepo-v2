# BUSINESS_CONTEXT_LOCKED — v8.4

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
- v8.6 canonicalized: 2026-04-18
- Latest production commit: `ccb291e322d` (2026-04-18)
- Lighthouse Desktop (KovelAI): P98 / A100 / BP100 / SEO100
- Lighthouse Mobile (ShadowTagAI): P93 / A93 / BP100 / SEO100
- Structural tests: 64/64
- Dead code: clean (vulture + ruff) — Kosmos dead code noted, production paths clean
- CounselConduit: v3.1.0 LIVE on Cloud Run (20 API modules)
- Cloud Armor WAF: `counselconduit-waf` (XSS + SQLi rules active)
- Cloud Monitoring: 5xx alert policy active (ID: 18301790723072591820)
- Security: Cor.30 v2.5 + OWASP LLM10 enforced (docs/SECURITY_DOD.md)
- Pre-commit: Gitleaks + Ruff + Bandit + detect-private-key

### CounselConduit Cloud Run (2026-04-18)
| Service | URL | Rev |
|---------|-----|-----|
| Production | https://counselconduit-767252945109.us-central1.run.app | counselconduit-00008-wpf |
| Staging | https://counselconduit-staging-767252945109.us-central1.run.app | counselconduit-staging-00003-l9h |

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
