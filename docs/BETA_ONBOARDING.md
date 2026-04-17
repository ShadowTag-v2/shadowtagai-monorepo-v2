# Beta Client Onboarding Prep

## Overview
This document outlines the beta client onboarding process for KovelAI Professional tier.

## Prerequisites for Beta Launch
- [x] Stripe Live: Products, prices, portal, webhook configured
- [x] Frontend: Chat, pricing, onboarding wizard deployed
- [x] Backend: CounselConduit API with Judge #6 governance
- [x] Auth: Firebase Auth JWT verification
- [ ] SMTP: Wire SendGrid/Google Workspace for emails
- [ ] Analytics: Wire Cloud Monitoring dashboards
- [ ] Legal: Terms of Service, Privacy Policy finalized

## Beta Program Terms
- **Coupon Code:** `3wseBY7Z` (50% off for 3 months, max 100 users)
- **Tier:** Professional ($74.50/mo with coupon, normally $149/mo)
- **Duration:** 3-month beta, auto-converts to standard pricing
- **Token Limit:** 100,000 tokens/month
- **Seats:** Up to 5 attorneys per firm
- **SLA:** 99.5% uptime target (no contractual obligation during beta)

## Onboarding Sequence

### Phase 1: Intake (Day 0)
1. Send beta invitation email with unique coupon link
2. Attorney visits `kovelai.web.app/pricing.html`
3. Clicks "Get Started" → Stripe Checkout with `3wseBY7Z` auto-applied
4. Post-payment redirect to `kovelai.web.app/onboarding.html`
5. 4-step wizard: identity, firm info, practice area, completion

### Phase 2: Configuration (Day 1-2)
1. Admin creates Firestore attorney record
2. Gemini RAG workspace initialized for practice area
3. Welcome email sent with dashboard link
4. Optional: Schedule 15-min demo call

### Phase 3: Activation (Day 3+)
1. Attorney accesses chat via `kovelai.web.app/chat.html`
2. First 5 queries monitored for Judge #6 calibration
3. Usage dashboard shows real-time token consumption
4. Weekly usage digest email begins

## Target Beta Cohort
| Category | Count | Practice Area |
|----------|-------|---------------|
| Solo Practitioners | 5-10 | Varied |
| Small Firms (2-5) | 3-5 | Corporate/IP |
| Mid-Size Firms (6-20) | 1-2 | Litigation |
| **Total Beta Seats** | **~30-50 attorneys** | |

## Success Metrics
- **Activation Rate:** % of sign-ups who complete onboarding (target: >80%)
- **Query Volume:** Avg queries per attorney per week (target: >10)
- **Retention:** 30-day retention rate (target: >70%)
- **NPS:** Net Promoter Score (target: >50)
- **Governance Accuracy:** Judge #6 false positive rate (target: <5%)

## Escalation Path
1. In-app: Help button → support@kovelai.com
2. Urgent: Discord #beta-support channel
3. Critical: Direct line to founder Erik

## Exit Criteria (End of Beta)
- Achieve 30+ active weekly users
- Zero data breaches or privilege violations
- NPS > 40
- Stripe MRR > $2,000 (after coupon)
- Cloud Run p95 latency < 3 seconds
