# Landing Page Manifest — Monorepo-Uphillsnowball

> **Invariant #92**: All landing pages MUST be classified as ACTIVE, DEPRECATED, or DEV-ONLY.
> Unclassified pages are BLOCKED from deployment.

**Last Updated**: 2026-04-11
**Total Pages**: 14

---

## Classification

| Status | Path | Product | Owner | Notes |
|--------|------|---------|-------|-------|
| ✅ **ACTIVE** | `apps/kovelai/public/index.html` | KovelAI Legal SaaS | @pikeymickey | Production. Deployed to kovelai.com |
| ✅ **ACTIVE** | `apps/shadowtagai/public/index.html` | ShadowTagAI Corporate | @pikeymickey | Production. Deployed to shadowtagai.com |
| ✅ **ACTIVE** | `apps/counselconduit/public/index.html` | CounselConduit Backend | @pikeymickey | Operational backend for KovelAI |
| 🔧 **DEV-ONLY** | `apps/aiyou_stack/.../omega-playground/index.html` | Omega Playground | internal | Dev debugging tool. Never deploy publicly |
| 🔧 **DEV-ONLY** | `apps/volatile-nova/index.html` | Volatile Nova | internal | R&D experiment page |
| ⚠️ **DEPRECATED** | `apps/aiyou_stack/.../landing-page/index.html` | AiYou Waitlist | — | Superseded by KovelAI. Contains TODO placeholders |
| ⚠️ **DEPRECATED** | `apps/aiyou_stack/.../gameport/nexusus/index.html` | Nexusus Gaming | — | Concept page. No backend. Hero buttons wired to alerts |
| ⚠️ **DEPRECATED** | `apps/aiyou_stack/.../products/memory_as_service.html` | Memory-as-a-Service | — | Product concept. 3 dead pricing CTAs |
| ⚠️ **DEPRECATED** | `apps/aiyou_stack/.../products/exguard_safety_sdk.html` | ExGuard SDK | — | Product concept. Links wired to GitHub placeholders |
| ⚠️ **DEPRECATED** | `apps/legaltrack/frontend/index.html` | LegalTrack | — | Early prototype. Superseded by KovelAI |

---

## Pages Requiring Investigation

| Path | Reason |
|------|--------|
| `apps/aiyou_stack/.../cosmic-crab-payload/public/index.html` | Canonical repo root — needs classification |
| `apps/aiyou_stack/.../Pipeline/public/index.html` | Canonical repo root — needs classification |
| `apps/aiyou_stack/.../nascent-apollo/public/index.html` | Canonical repo root — needs classification |
| `apps/aiyou-web-dashboard/public/index.html` | Next.js default — may not be a landing page |

---

## Migration Guide

### To adopt `libs/ui/`:

```html
<!-- Replace scattered inline styles with canonical imports -->
<link rel="stylesheet" href="/libs/ui/styles/buttons.css">
<link rel="stylesheet" href="/libs/ui/styles/layout.css">

<!-- Before (30+ variants): -->
<a class="btn-primary btn-full btn-glow" href="/signup">Get Started</a>

<!-- After (5 canonical variants): -->
<a class="st-btn st-btn--primary st-btn--lg st-btn--full st-btn--glow" href="/signup">Get Started</a>
```

### Class Migration Table

| Old Class(es) | New Class(es) |
|---------------|---------------|
| `.btn-primary` | `.st-btn.st-btn--primary` |
| `.btn-secondary` | `.st-btn.st-btn--secondary` |
| `.btn-ghost`, `.btn-nav` | `.st-btn.st-btn--ghost` |
| `.btn.outline` | `.st-btn.st-btn--outline` |
| `.btn-icon`, `.control-btn` | `.st-btn.st-btn--icon` |
| `.btn-primary.btn-glow` | `.st-btn.st-btn--primary.st-btn--glow` |
| `.btn-primary.btn-full` | `.st-btn.st-btn--primary.st-btn--full` |
| `.cta-button` | `.st-btn.st-btn--primary.st-btn--lg` |
| `.hero` | `.st-hero` |
| `.nav-links` | `.st-nav__links` |
| `.section` | `.st-section` |
| `.pricing-grid` | `.st-grid.st-grid--3` |

---

## Deployment Rules

1. **ACTIVE** pages: Deploy via Cloud Run / Firebase Hosting
2. **DEV-ONLY** pages: Never deploy to production domains
3. **DEPRECATED** pages: Do NOT deploy. Archive or delete after 30 days of inactivity
4. All new landing pages MUST import from `libs/ui/styles/` — no new inline button classes permitted
