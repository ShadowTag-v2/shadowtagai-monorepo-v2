# Antigravity HoldCo — Spinout Structure

## Overview

Antigravity HoldCo is the parent entity for all ShadowTag-v2 operational assets.
The HoldCo owns the monorepo infrastructure, MCP fleet, sovereign compute stack,
and IP across all product lines.

---

## Entity Structure

```
Antigravity HoldCo, Inc. (Delaware C-Corp)
├── KovelAI, Inc. — Privilege-preserving legal AI
│   ├── kovelai.com / kovelai.web.app
│   ├── CounselConduit API (Cloud Run)
│   └── Oracle Studio pipeline
├── ShadowTag AI — Parent brand, portal
│   ├── shadowtagai.web.app
│   └── AiYou Stack (Apple Silicon ML runtime)
└── UphillSnowball Labs — R&D
    ├── Cinematic scroll engine
    ├── Media MCP server (Veo 3.1)
    └── Sovereign compute infrastructure
```

---

## Repo Skeleton

```
antigravity-holdco/
├── README.md
├── BUSINESS_CONTEXT_LOCKED.md
├── docs/
│   ├── cap-table.md           # Equity structure
│   ├── operating-agreement.md # LLC → C-Corp conversion
│   ├── ip-assignment.md       # Founder IP assignment
│   ├── vesting-schedule.md    # 4-year, 1-year cliff
│   └── board-resolutions/     # Corporate governance
├── financials/
│   ├── projections-3yr.xlsx   # Revenue model
│   ├── burn-rate.md           # Monthly burn
│   └── fundraise-tracker.md   # Investor pipeline
├── legal/
│   ├── articles-of-incorp.md  # Delaware C-Corp
│   ├── bylaws.md              # Corporate bylaws
│   ├── 83b-election.md        # Founder tax election
│   └── safe-template.md       # YC SAFE note
├── compliance/
│   ├── soc2-tracker.md        # SOC 2 progress
│   ├── privacy-policy.md      # Privacy
│   └── terms-of-service.md    # ToS
└── scripts/
    ├── setup-stripe.sh        # Stripe Connect onboarding
    ├── setup-gcp.sh           # GCP project provisioning
    └── cap-table-calc.py      # Cap table calculations
```

---

## Key Corporate Actions

### Immediate (Week 1)
1. File Delaware C-Corp articles ($89 + $300 filing fee)
2. Obtain EIN from IRS (Form SS-4)
3. Open Silicon Valley Bank or Mercury account
4. File 83(b) election (within 30 days of incorporation)
5. Execute IP assignment agreement (founder → HoldCo)

### YC Application (Week 2-4)
1. Complete W27 application (docs/yc-w27-application.md)
2. Record 60-second demo video
3. Prepare 3-minute pitch for interview
4. Financial projections for 3 years

### Post-Incorporation (Month 2)
1. Stripe Atlas or Clerky for corporate formation docs
2. Carta or Pulley for cap table management
3. SOC 2 platform onboarding (Vanta)
4. D&O insurance ($2-5K/year)

---

## Equity Structure (Pre-Seed)

| Holder | Shares | % |
|--------|--------|---|
| Erik Hanson (Founder) | 8,000,000 | 80% |
| Employee Option Pool | 1,500,000 | 15% |
| Advisor Pool | 500,000 | 5% |
| **Total Authorized** | **10,000,000** | **100%** |

### Vesting
- Founder: 4-year vesting, 1-year cliff, single trigger acceleration
- Employees: 4-year vesting, 1-year cliff, standard
- Advisors: 2-year vesting, no cliff

---

## Revenue Attribution

| Product | Year 1 | Year 2 | Year 3 |
|---------|--------|--------|--------|
| KovelAI SaaS | $300K | $3M | $15M |
| CLE Revenue | $50K | $200K | $500K |
| Enterprise | $0 | $2M | $10M |
| **Total** | **$350K** | **$5.2M** | **$25.5M** |
