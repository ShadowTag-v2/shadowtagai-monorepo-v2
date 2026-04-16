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
- v8.5 canonicalized: 2026-04-16
- Latest production commit: `32fb1341fc6` (2026-04-16)
- Lighthouse: A100 / BP100 / SEO100 (desktop)
- Structural tests: 30/30
- Dead code: clean (vulture + ruff) — Kosmos dead code noted, production paths clean

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
