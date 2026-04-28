# BUSINESS_CONTEXT_LOCKED — v10.0

> **Hard Redesign applied 2026-04-22** — Full Emotional Arbitrage + S.E.U. Architecture integrated.

---

## Identity

CounselConduit is the **"Shopify for Legal AI"** — a privilege-preserving routing tier between law firms and foundational LLMs (Gemini, Claude, ChatGPT, Grok, Perplexity) protected under *United States v. Heppner* (S.D.N.Y., Feb. 10, 2026).

**Hard Redesign Thesis**: CounselConduit is not a legal research tool. It is an **emotional arbitrage engine** — the client pays because they feel safe, heard, and understood. The AI does the thinking; the brand does the holding.

**Messaging Model (Locked v10.2)**: The **attorney is the buyer**. The **client is the beneficiary**. Like a police chief buying bulletproof vests for the force. The attorney deploys CounselConduit as privileged search infrastructure for their clients. The client searches freely inside the privilege umbrella — relaxing enough to recall all the facts of their case. The attorney sits in the loop: monitoring sessions, providing the first legal opinion, and billing automatically. We protect the client from themselves — from discoverable Google searches, from incorrect AI-generated legal opinions, and from ambushing their own attorney with unvetted research.

---

## §1 — Core Tiers (Updated v10.0)

### Consumer Syndicate
- Price: `$149/mo`
- Margin: `95%`
- Architecture: `Centralized Hive Mind Oracle + Stateless Micro-Edge`

### Enterprise Base SLA
- Price: `$20,000/mo`
- Margin: `69–71%`
- Core value: `Zero-latency AST risk mitigation`
- Isolation: `Dedicated GCP sidecar`

### Enterprise EU26 Premium
- Price: `$28,333/mo`
- Margin: `76–78%`
- Core value: `Higher-assurance compliance and enterprise isolation posture`

### Sovereign Scale
- Customer pays `100% compute pass-through`
- Software margin retained on the base license

---

## §2 — Dual-Billing Engine (Stripe Connect)

1. **Client → Lawyer**: Client subscribes to AI portal with credit card. Funds flow to lawyer's Stripe account. Lawyer gets paid upfront for each query.
2. **Lawyer → Us**: Auto-scaling tiered subscription (Solo $299, Practice $599, Enterprise $999). Tiers cover ALL LLM API costs + 85%+ margin. Auto-bump on usage (like Claude Code billing).
3. **Fee Isolation**: We never touch the client-lawyer fee arrangement.

### Stripe Live Configuration
- Account: `acct_1Syh9JEHnWpykeMi` (US, charges+payouts enabled)
- Products: `prod_UM2XwCF1byjegL` (Trial), `prod_UM2X10cpyay52e` (Pro), `prod_UM2XMVp9Er7A0i` (Enterprise)
- Pro Monthly: `price_1TNKSREHnWpykeMiRMDlVgLl` ($149/mo)
- Pro Annual: `price_1TNKSjEHnWpykeMi0S9GCVjy` ($1,428/yr)
- Enterprise: `price_1TNKSREHnWpykeMi8mrDf4rI` ($20K/mo)
- Beta Coupon: `3wseBY7Z` (50% off, 3 months, max 100)
- Portal: `bpc_1TNKSjEHnWpykeMi0qQPoaHm`
- Webhook: `we_1TNKSjEHnWpykeMiQZqmpy3X` → `https://counselconduit-api.run.app/webhooks/stripe`

---

## §3 — Architectural Split

- Consumer path: centralized intelligence + stateless micro-edge
- Enterprise path: tenant-isolated sidecars + stronger controls + mTLS
- **Rule**: Do not mix these lanes casually. Consumer and enterprise economics are different products.

### Latency Doctrine
- Target: `p99 <= 90ms total application path` where architecture permits

---

## §4 — The "Intake Engine" Hard Redesign

### 4.1 Emotional Arbitrage

> "Nobody is buying 'AI attorney research'. They are paying for **the feeling that someone smart has their back**.
> That's the entire product. Everything else is infrastructure."

The gap between what the AI costs to provide and what emotional security is worth = **emotional arbitrage**.

- Legal AI costs: ~$0.02/query
- Client perception: "A brilliant attorney who works 24/7 just for me"
- Charge: $149–$999/mo
- Margin: ♾️ (the raw cost is noise)

### 4.2 The Invisible Meter

**Must-hit metric**: Avg client spends **>45 min/session** inside the portal.

Design principles:
1. **Session timer is hidden** — never show how long they've been in
2. **No "are you still there?"** prompts — dead-man's switch architecture
3. **Ambient micro-animations** — typing indicators, subtle glow, pulsing orbs
4. **Progressive depth** — start with reassurance, gradually surface actionable intelligence
5. **"One More Thing" cadence** — end every response with a gentle hook to the next topic
6. **Warm close** — "You're doing the right thing by understanding this" (never "goodbye")

### 4.3 The Psychological & Therapeutic Layer

#### Design Canon
1. Client must FEEL heard first, informed second
2. Every AI response opens with an empathy acknowledgment — then pivots to legal
3. Legal jargon auto-detected and footnoted inline with LAYMAN_TRANSLATION
4. "How are you feeling about this?" check-in auto-inserted every 3rd response
5. Ambient "you're not alone" social proof microdata (anonymized: "837 people explored this today")
6. Session recaps framed as emotional victories: "Here's what you now understand that you didn't before"
7. Warm handoff: escalation to a real attorney framed as "we've found a specialist who can take this further for you"

#### Intake Flow (S.E.U. Framework)

**S.E.U. = Safety → Empathy → Utility**

Every client session must traverse these layers in order:

```
┌──────────────────────────────────────────────────┐
│ LAYER 1: SAFETY                                  │
│ "You're in the right place."                     │
│ - Kovel attestation badge visible                │
│ - "Attorney-client privilege applies here" banner│
│ - Calm, dark UI — no jarring colors              │
│ - No visible timer. No "hurry up" cues.          │
├──────────────────────────────────────────────────┤
│ LAYER 2: EMPATHY                                 │
│ "We understand this is stressful."               │
│ - Opening prompt: "Tell us what's happening"     │
│ - AI empathy acknowledger before every response  │
│ - "How are you feeling?" check-in every 3 turns  │
│ - Social proof: "437 clients explored this today"│
├──────────────────────────────────────────────────┤
│ LAYER 3: UTILITY                                 │
│ "Here's what this means for you."                │
│ - Legal analysis in plain English first           │
│ - Jargon footnoted, not replaced                 │
│ - Action items surfaced last                     │
│ - Warm handoff to attorney if complexity > θ     │
└──────────────────────────────────────────────────┘
```

#### Emotional Loop Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Intake     │────▶│   Oracle    │────▶│   Output    │
│  (empathy)   │     │ (analysis)  │     │ (reassure)  │
└─────────────┘     └─────────────┘     └─────────────┘
       │                                       │
       └──────────── "One More Thing" ◀────────┘
```

### 4.4 Vent Mode (Upgraded)

Vent Mode is the **emotional release valve**. Client speaks unstructured grievances. AI:
1. Validates emotionally
2. Extracts legal entities/claims silently
3. Summarizes into structured intake
4. Attorney sees clean brief, client felt heard

Key metrics:
- Avg vent duration: target 15+ minutes
- Extraction accuracy: >90% entity coverage
- Client satisfaction: NPS > 70 post-vent

---

## §5 — Four Corners Sweep (Business Plan v2.0)

### 5.1 Product Architecture

| Component | Purpose | Status |
|-----------|---------|--------|
| CounselConduit API | Cloud Run FastAPI (33 endpoints) | ✅ LIVE v3.2.0 |
| KovelAI Frontend | Firebase Hosting (attorney-facing) | ✅ LIVE |
| ShadowTagAI | Firebase Hosting (client-facing) | ✅ LIVE |
| Oracle Studio | 7-stage LLM pipeline | ✅ Built |
| Vent Mode | SSE streaming emotional intake | ✅ Built |
| Judge 6 | Policy gate (ATP 5-19) | ✅ Built |
| NadirClaw Dispatch | 3-tier model router w/ circuit breaker | ✅ Built |
| Dead-Man's Switch | Ephemeral session protection | ✅ Built |
| Kovel Attestation | HMAC-SHA256 privilege receipts | ✅ Built |
| Stripe Connect | Dual-billing onboarding flow | ✅ Built |
| GDPR Module | Article 15/17/20 + Cloud Tasks 30-day TTL | ✅ Built |

### 5.2 Market Position

- **TAM**: $18.5B (US legal tech, growingat 9.1% CAGR)
- **SAM**: $1.2B (small-mid law firms using AI tools)
- **SOM Year 1**: $2.4M (200 firms × $999/mo avg)
- **SOM Year 3**: $18M (1,500 firms × $1,000/mo avg)

### 5.3 Competitive Moat (4 Layers)

1. **Privilege Layer**: *Heppner* precedent — only platform with Kovel attestation receipts
2. **Emotional Layer**: S.E.U. framework — competitors do research, we do reassurance
3. **Switching Cost**: Attorney workflows + client data locked behind privilege wall
4. **Network Effect**: More attorneys → more client trust → more referrals

### 5.4 Revenue Model

| Year | Firms | ARPU/mo | MRR | ARR | Margin |
|------|-------|---------|-----|-----|--------|
| Y1 | 200 | $999 | $200K | $2.4M | 85% |
| Y2 | 800 | $1,100 | $880K | $10.6M | 87% |
| Y3 | 1,500 | $1,200 | $1.8M | $21.6M | 89% |
| Y4 | 3,000 | $1,400 | $4.2M | $50.4M | 90% |
| Y5 | 5,000 | $1,500 | $7.5M | $90M | 91% |

### 5.5 Exit Thesis

| Path | Multiplier | Valuation | Timeline |
|------|-----------|-----------|----------|
| SaaS Acquisition (Thomson Reuters, LexisNexis) | 15-20x ARR | $1.35B–$1.8B @ Y5 ARR | 5-7 years |
| Strategic PE (Vista, Thoma Bravo) | 12-15x ARR | $1.08B–$1.35B | 4-6 years |
| IPO | 20-25x ARR | $1.8B–$2.25B | 7-10 years |

### 5.6 Funding Strategy (If Pursued)

- **Pre-seed**: Self-funded / bootstrapped → current state
- **Seed**: $2-3M @ $15M post-money → first 50 firms, hire 3 engineers
- **Series A**: $10-15M @ $80M post-money → 500 firms, enterprise launch
- **Series B**: $30-50M @ $300M post-money → 2,000 firms, international

> **Default mode**: Bootstrap to $5M ARR before considering outside capital. Emotional arbitrage margins support this.

---

## §6 — Hardened Production State

### v10.0 → v10.2 canonicalized: 2026-04-28
- Latest production commit: `76e39472c` (2026-04-28)
- Lighthouse LHCI (KovelAI): A100 / BP100 / SEO100 (0 failed audits)
- Lighthouse LHCI (ShadowTagAI): A95 / BP96 / SEO100
- Tests: 504 collected, 498 passed, 3 xfailed, 3 skipped (82.10s)
- Dead code: clean (ruff 0.15.11 F401/F841 — 0 errors)
- CounselConduit: v3.2.0 LIVE on Cloud Run rev `counselconduit-00037-7mf`
- Cloud Armor WAF: `counselconduit-waf` (XSS + SQLi + rate limiting active)
- Cloud Monitoring: 9 alert policies + email channel
- SLO: CounselConduit 99.5% Availability, 30-day rolling
- Firestore TTL: session_pins.expire_at ACTIVE
- Firestore PITR: ENABLED on both databases (7-day retention)
- Security: Cor.30 v2.5 + OWASP LLM10 enforced
- Pre-commit: Betterleaks + Ruff + Bandit + detect-private-key + check-yaml + trailing-whitespace
- Secret Manager: 22 secrets (5 orphans deleted)
- OpenTofu: 19 resources provisioned
- RISK_REGISTER: v10.9 (86+ tracked risks)
- Cloud Functions: 4 active (analyticalWebhook, captureContact, captureLead, cspReport)
- Firestore: 2 databases (default nam5, shadowtag-engine us-central1) — delete-protection ENABLED
- Stripe: Payment Link URLs PENDING — Price IDs wired, need Dashboard Payment Link creation for Pro Monthly/Annual
- Messaging Model: Attorney-buyer / Client-beneficiary cascade complete (9 components)
- Open PRs: 0

### CounselConduit Cloud Run
| Service | URL | Rev |
|---------|-----|-----|
| Production | https://counselconduit-767252945109.us-central1.run.app | counselconduit-00037-7mf (100% traffic) |
| Staging | https://counselconduit-staging-767252945109.us-central1.run.app | counselconduit-staging-00003-l9h |

### Deployed Hosting Targets
| Target | URL | Status |
|--------|-----|--------|
| KovelAI Live | https://kovelai.web.app | ✅ |
| ShadowTagAI Live | https://shadowtagai.web.app | ✅ |
| Default Site | https://shadowtag-omega-v4.web.app | ✅ |

---

## §7 — Webhook vs Firestore Pricing Matrix

Because we moved away from Redis cache over to Firestore `system_idempotency_keys` for Zod validation locks, high frequency polling will cost approximately $0.18 per 100k requests read/writes against the GCP document quota. We remain heavily profitable beneath the $5K Base Tier barrier. Edge Sovereign node ingress remains $0.00 bandwidth locked within our private peering subnet.

---

## §8 — Canonical Production Assets (Locked 2026-04-16)

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

---

## §9 — Wave Delivery History

### Wave 9.3 (2026-04-18)
- OG Social Images, CSP Hardening, Lighthouse BP 100, New Modules (silent_detector, blast_radius, null_model_validator, ucmj_discipline), Dead Code purge, Dependabot, CHANGELOG.md, 68/68 tests, 33 API modules

### Wave 9 (2026-04-18)
- IaC Apply (13 resources), IaC Import (9 secrets), API Key Restriction, GCA Batch Reviewer, Pre-push GCA Hook, SM-First Auth, OTEL Sampling, Lighthouse CI, Cloud Build, Staging Branch, Email Alerts, Cloud Scheduler, Firestore Backup, PubSub Topic, Production Runbook, Secret Rotation, Heartbeat Tests, 10 PRs Resolved, Auto-merge, Risk Register v9.0

### Wave 8 (2026-04-18)
- 25-Rule Security Contract, 15 Security Defaults, Headless CLI Protocol, Cloud Run Rev 00010-s74, Canary Traffic Split, GDPR Cleanup Cron, OpenTelemetry, OpenTofu 1.11.6, Mobile Networking Spec

### Wave 7 (2026-04-18)
- Google Workspace Alerts, Secret Manager Migration, Terraform IaC, gws CLI, Org-Level Storage Policy, GCS Lifecycle, Deployment Runbook

### Wave 4-5 (2026-04-18)
- Firebase Auth JWT, Docker Import Paths, Video Compression, Transcript Viewer, GDPR Export UI, Dead-Man's Switch, Attorney Onboarding, Intake Summarizer, Webhook Signatures, Mobile Spec, OpenTelemetry, Firestore Health, Session Heartbeat

### Production Hardening (2026-04-16)
- CSP Headers, Permissions-Policy, WebP Optimization, Custom 404 Pages, DNS Prefetch, Preview Channels, Google Search Console, Firebase Storage, GCS CORS, Cloud Monitoring, captureLead, Hero Preload, Git Auth

---

## §10 — Marketing Channels (Locked 2026-04-28)

### Google Pomelli Integration
| Property | Value |
|----------|-------|
| Platform | Google Labs Pomelli (https://labs.google.com/pomelli) |
| Business DNA Source | https://kovelai.web.app |
| Campaign Prompt | "Legal tech SaaS that shields clients from discoverable AI research under attorney-client privilege" |
| Photoshoot (Imagen) | TACSOP 7-compliant product imagery generation with provenance tracking |
| Mobile Support | ✅ Available for on-the-go campaign creation |
| Status | Active — Business DNA requires re-ingestion after each major messaging pivot |

### Marketing Asset Pipeline
1. **Pomelli Campaigns**: Generate social media cards, ad copy, and landing page variants
2. **Photoshoot (Imagen)**: Professional product imagery — hero images, feature illustrations, social assets
3. **Content Themes**: Attorney-client privilege, post-Heppner compliance, client protection from discoverable searches
4. **Distribution**: LinkedIn (attorney buyers), Twitter/X, legal tech newsletters, ABA Journal

### Campaign Messaging Framework
- **Primary Buyer**: Attorney / Managing Partner
- **Primary Beneficiary**: Client (protected from discoverable AI searches)
- **Core Thesis**: "Protect your clients from themselves — deploy privileged search infrastructure"
- **Emotional Hook**: "Your client is Googling their case at 2 AM. Make those searches privileged."
- **Compliance Anchor**: *United States v. Heppner* (S.D.N.Y., Feb. 10, 2026)
