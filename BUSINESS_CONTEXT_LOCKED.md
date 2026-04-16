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
- v8.4 canonicalized: 2026-04-13
- Commit: `c279f820037`
- Lighthouse: A97 / BP100 / SEO100
- Structural tests: 30/30
- Dead code: clean (vulture + ruff)


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
