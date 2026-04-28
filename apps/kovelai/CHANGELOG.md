# KovelAI — Changelog

## [1.3.0] - 2026-04-28

### Validated
- **Production build**: Next.js 16.2.1 (Turbopack) — compiled in 1.83s, 4/4 static pages
- **Lighthouse**: A100 / BP100 / SEO100 (51 audits passed, 0 failed)
- **Ruff F401/F841**: All checks passed — zero dead Python code
- **Biome lint**: 28 files checked, 4 warnings (non-critical), format auto-fixed
- **Guillotine v9.0**: Full dead-code sweep — all passes clean

### Infrastructure
- **Cloud Run**: CounselConduit `counselconduit-00045-kjp` active, Ready=True
- **Firebase Hosting**: CSP headers hardened (Stripe, GA, GTM, Cloudflare domains)
- **HSTS**: `max-age=63072000; includeSubDomains; preload`
- **COOP/CORP**: `same-origin` enforced

### Design System
- **Sovereign Architect** v1.0 tokens aligned (`DESIGN.md`)
- Stitch Asset: `assets/16076fab918644088a3d948067760e83`
- No-line rule enforced, Inter typography active

### Stripe Integration
- Pro Monthly (`price_1TNKSREHnWpykeMiRMDlVgLl`) wired
- Pro Annual (`price_1TNKSjEHnWpykeMi0S9GCVjy`) wired
- Enterprise contact flow active
- **Pending**: Dedicated Payment Link creation (human handoff — Stripe Dashboard)

## [1.2.0] - 2026-04-27

### Changed
- CSP policy updated to include `'unsafe-inline'` for script-src/style-src
- Added Stripe domains (`js.stripe.com`, `api.stripe.com`, `buy.stripe.com`) to CSP
- Messaging pivot: client-protection framing per Heppner alignment
- Firebase Hosting deploy — clean 100/100/100 Lighthouse

## [1.1.0] - 2026-04-26

### Added
- UnusualChassis unified layout integration
- ContactModal with React-state focus trapping
- ScrollProgress component
- Skip navigation (WCAG 2.4.1 compliance)
- `prefers-reduced-motion` support

## [1.0.0] - 2026-04-25

### Initial Release
- KovelAI landing page deployed to Firebase Hosting
- 13 section components assembled
- Sovereign Architect design system applied
- Dark-mode-first, editorial aesthetic
