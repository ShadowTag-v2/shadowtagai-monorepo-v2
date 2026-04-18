# Beta Client Onboarding Sequence
## CounselConduit / KovelAI — Beta Program v1.0

**Target: First 10 firms, 50% off for 3 months (coupon `3wseBY7Z`)**

---

## Pre-Onboarding Checklist (Internal)

- [ ] Stripe Connect account active
- [ ] Cloud Run deployed with security stack
- [ ] Kovel attestation system tested
- [ ] GDPR deletion flow tested
- [ ] Oracle Studio pipeline wired to at least Gemini Flash
- [ ] Rate limiting verified in production
- [ ] Security headers verified via curl
- [ ] Webhook handler deployed and tested
- [ ] Client portal (ephemeral) build deployed
- [ ] Attorney dashboard deployed

---

## Onboarding Phases

### Phase 1: Discovery Call (Day 0)
1. **Demo**: Show Oracle Studio 7-prompt pipeline live
2. **Privilege Briefing**: Explain Kovel/Heppner doctrine and how attestation works
3. **Pricing**: Present Professional tier ($149/mo with 50% beta discount = $74.50/mo)
4. **Compliance**: Walk through SECURITY_DOD.md highlights (SOC 2 roadmap)
5. **Deliverable**: Signed LOI (Letter of Intent)

### Phase 2: Technical Setup (Day 1-3)
1. **Stripe Account**: Onboard firm to Stripe Connect
   - Attorney creates Stripe account (2 min)
   - We send Connect onboarding link
   - Attorney completes identity verification
2. **Firm Configuration**:
   - Create firm record in Firestore
   - Set model policy (which AI models allowed)
   - Configure billing attribution
   - Set up firm branding (logo, colors)
3. **Attorney Accounts**:
   - Create attorney accounts
   - Assign roles (admin, partner, associate)
   - Set per-attorney token budgets
4. **Integration** (optional):
   - Clio/PracticePanther API key setup
   - Matter import from existing PMS

### Phase 3: Training (Day 3-5)
1. **Attorney Training** (1 hour):
   - Oracle Studio walkthrough
   - Magic link generation for clients
   - Vent Mode intake fee setup
   - Dashboard and analytics overview
   - Attestation receipt verification
2. **Support Setup**:
   - Dedicated Slack channel (or Discord)
   - Emergency contact escalation path
   - Weekly 15-min check-in scheduled

### Phase 4: Soft Launch (Day 5-7)
1. **Pilot Client**: Attorney sends magic link to 1 real client
2. **Supervised Session**: Our team monitors the first Oracle Studio run
3. **Attestation Verification**: Verify receipt generation and HMAC integrity
4. **Feedback Collection**: Structured form for attorney and client

### Phase 5: Go-Live (Day 7+)
1. **Full Access**: Remove pilot restrictions
2. **Billing Active**: First invoice at end of month
3. **Monitoring**: Auto-alerts for payment failures, high error rates
4. **Review**: 30-day check-in for tier upgrade discussion

---

## Attorney Email Templates

### Welcome Email
```
Subject: Welcome to KovelAI Beta — Your Privileged AI Research Portal

Dear [Attorney Name],

Thank you for joining the KovelAI beta program. Your firm has been
selected as one of our first 10 partners.

Your login credentials:
- Portal: https://kovelai.web.app/dashboard
- Email: [attorney_email]
- Password: [temp_password] (you'll be prompted to change on first login)

Your beta pricing: $74.50/month (50% off Professional tier, 3 months)

What's included:
- Oracle Studio: 7-prompt legal research pipeline
- Multi-model AI (Gemini, Claude, GPT, Grok, Perplexity)
- Kovel attestation receipts for privilege protection
- Client portal with magic-link onboarding
- Vent Mode intake retainer system

Your dedicated support channel: [slack/discord link]

Best regards,
CounselConduit Team
```

### Client Magic Link Email
```
Subject: Secure Legal Research Portal — [Firm Name]

Dear [Client Name],

Your attorney at [Firm Name] has set up a secure AI research session
for your matter.

Click this link to access your portal:
[MAGIC_LINK]

Important:
- This link expires in 72 hours
- It can only be used once
- Your session will automatically end after [TTL] hours
- All communications are protected under attorney-client privilege

If you have questions, contact [Attorney Name] at [attorney_email].
```

---

## Success Metrics (30/60/90 day)

| Metric | 30 Day | 60 Day | 90 Day |
|--------|--------|--------|--------|
| Active firms | 3 | 7 | 10 |
| Oracle sessions/week | 15 | 40 | 100 |
| Vent Mode intakes | 5 | 20 | 50 |
| MRR | $223 | $521 | $745 |
| Churn | 0% | <10% | <15% |
| NPS | >50 | >50 | >60 |

---

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Attorney doesn't understand Kovel doctrine | Pre-call briefing doc + CLE credit partner |
| Client ignores magic link TTL | Dead-man's switch auto-logout + email reminder |
| Stripe Connect onboarding friction | Stripe Hosted Onboarding (embedded, 2 min) |
| Model hallucination in Oracle Memo | Judge #6 policy gate + mandatory citation verification |
| Privilege waiver accusation | Kovel attestation + immutable audit trail |
