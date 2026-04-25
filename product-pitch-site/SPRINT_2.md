# Sprint 2 — KovelAI Product Pitch Site

**Sprint Duration:** 2026-04-22 → 2026-05-06
**Goal:** First paid customer checkout, GA4 analytics live, Cloud Run API routes

## Backlog

### P0 — Must Ship
- [ ] Create GA4 property at analytics.google.com for kovelai.web.app
- [ ] Set `NEXT_PUBLIC_GA_MEASUREMENT_ID` once property is created
- [ ] Deploy Next.js standalone to Cloud Run for live API routes
- [ ] Register Stripe webhook: `https://kovelai.run.app/api/webhooks/stripe`
- [ ] Test end-to-end checkout flow with Stripe test mode
- [ ] Create Stripe prices matching $299/$599/$999 (if not using existing)
- [ ] Wire Google Apps Script endpoint for email capture form

### P1 — High Value
- [ ] Remotion video PR demo for investor deck
- [ ] About page: team bios with real headshots
- [ ] Blog scaffold (/blog) with MDX support
- [ ] Customer testimonial carousel component
- [ ] API rate limiting middleware

### P2 — Polish
- [ ] Dark/light mode toggle
- [ ] Cookie consent banner (GDPR)
- [ ] 404 page with branding
- [ ] Favicon update to match new og:image shield
- [ ] Performance optimization: lazy-load below-fold sections

## Completed (Sprint 1 → Sprint 2 Carryover)
- [x] Live Stripe payment links (price IDs wired)
- [x] Stripe webhook handler (5 events)
- [x] GA4 script integration (env-driven)
- [x] og:image social preview card
- [x] JSON-LD structured data
- [x] A/B hero headline rotation
- [x] Email capture form
- [x] Mobile hamburger animation polish
- [x] Lighthouse CI in GitHub Actions
- [x] Coupon auto-apply via URL params
- [x] Billing portal configuration
- [x] Gitleaks scan passed
- [x] Firebase Hosting deploy (kovelai.web.app)
