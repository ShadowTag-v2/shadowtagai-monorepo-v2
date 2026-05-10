# ShadowTag-v2JR Judge Skill

**Purpose:** Enforce strategic decision gates before feature implementation
**Enforcement:** `"suggest"` - Shows warnings but doesn't block (human decides)
**Priority:** `"high"`
**Version:** 1.0.0

---

## Overview

This skill enforces the ShadowTag-v2JR decision framework (Purpose • Reasons • Brakes) to ensure every feature serves strategic goals and meets financial thresholds. It acts as your "160-IQ board" that automatically validates decisions before implementation.

**Auto-Activation Triggers:**
- Keywords: `feature`, `implement`, `build`, `architecture`, `plan`, `deploy`
- Files: `ARCHITECTURE.md`, `PLAN.md`, dev docs
- Content: Detects planning/design discussions

---

## The Three Gates Framework

```
┌─────────────────────────────────────────────────────────┐
│                    PURPOSE GATE                          │
│  "Does this serve founder goals?"                        │
│  ✓ Strategic alignment check                             │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                    REASONS GATE                          │
│  "Will this make money?"                                 │
│  ✓ ROI ≥3× in 18 months                                 │
│  ✓ LTV:CAC ≥4:1 in 12-18 months                         │
│  ✓ NPV ≥70% positive probability                        │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                    BRAKES GATE                           │
│  "Can we reverse this if it fails?"                      │
│  ✓ Rollback steps documented                             │
│  ✓ Blast radius assessed                                 │
│  ✓ Kill-switch triggers defined                          │
│  ✓ Security requirements met                             │
└─────────────────────────────────────────────────────────┘
                          ↓
                    [IMPLEMENT]
```

---

## Gate 1: Purpose

**Question:** Does this serve Pnkln's strategic goals?

### Checklist

- [ ] Aligns with **ActiveShield** exit (Y5-Y7) OR **PNKLN Holdings** long-term strategy
- [ ] Documented in Cor.X framework (specify which: Cor.17, Cor.21, etc.)
- [ ] Classification: **Mission-critical** / **High-value** / **Nice-to-have**

### Examples

```markdown
✅ PASS: "Implement ShadowTag cryptographic signing for ActiveShield"
- Aligns with: ActiveShield security vertical (core product)
- Cor.X Reference: Cor.17 (PNKLN Core Stack)
- Classification: Mission-critical

✅ PASS: "Add OAuth 2.0 authentication for PNKLN API"
- Aligns with: PNKLN Holdings long-term (platform security)
- Cor.X Reference: Cor.34 (Omega/AiY architecture)
- Classification: Mission-critical

⚠️ CONDITIONAL: "Build internal admin dashboard for team metrics"
- Aligns with: Internal tooling (productivity)
- Cor.X Reference: None (not strategic)
- Classification: Nice-to-have
- Recommendation: Defer until Q2 after ActiveShield launch

❌ FAIL: "Integrate with 15 social media platforms"
- Aligns with: Unknown (no strategic connection)
- Cor.X Reference: None
- Classification: Scope creep
- Recommendation: STOP - validate strategic value first
```

**See:** [resources/strategic-frameworks.md](resources/strategic-frameworks.md) for Cor.X references

---

## Gate 2: Reasons

**Question:** Will this make money? Can we quantify the ROI?

### Three Required Thresholds

#### 2.1 ROI ≥3× in 18 Months

**Formula:**
```
ROI = (Revenue - Investment) / Investment

Where:
- Revenue = Projected revenue over 18 months
- Investment = Dev time + AI compute + infrastructure + maintenance
```

**Example:**
```markdown
Feature: Add premium tier to ActiveShield
Investment: $50k (dev) + $10k (infra) = $60k
Revenue (18mo): $250k
ROI = ($250k - $60k) / $60k = 3.17× ✅ PASS
```

**Monte Carlo Scenarios:**
- **Base Case (50% prob):** ROI = 3.2×
- **Best Case (25% prob):** ROI = 5.1×
- **Worst Case (25% prob):** ROI = 1.8× ❌
- **Probability-Weighted:** (0.5 × 3.2) + (0.25 × 5.1) + (0.25 × 1.8) = 3.33× ✅

**See:** [resources/roi-calculation.md](resources/roi-calculation.md) for detailed formulas

#### 2.2 LTV:CAC ≥4:1 in 12-18 Months

**Formula:**
```
LTV = (Average Revenue Per Customer × Gross Margin) / Churn Rate
CAC = Total Acquisition Cost / Number of Customers Acquired

LTV:CAC Ratio = LTV / CAC (target ≥4:1)
```

**Example:**
```markdown
Feature: SEO optimization for ActiveShield landing pages
Avg Revenue Per Customer: $2,000/year
Gross Margin: 80%
Churn Rate: 10% annually
LTV = ($2,000 × 0.8) / 0.1 = $16,000

CAC (organic search): $3,500 per customer
LTV:CAC = $16,000 / $3,500 = 4.57:1 ✅ PASS
```

**See:** [resources/ltv-cac-models.md](resources/ltv-cac-models.md) for templates

#### 2.3 NPV ≥70% Positive Probability

**Formula:**
```
NPV = Σ (Cash Flow_t / (1 + r)^t) - Initial Investment

Where:
- Cash Flow_t = Net cash flow in period t
- r = Discount rate (typically 15% for startups)
- t = Time period (months)
```

**Monte Carlo Approach:**
```markdown
Run 1000 simulations with varying:
- Customer acquisition rate (±30%)
- Churn rate (±20%)
- Development timeline (±40%)
- Pricing (±15%)

Result: 782 simulations have positive NPV
Probability = 782 / 1000 = 78.2% ✅ PASS (≥70%)
```

**See:** [resources/monte-carlo-templates.md](resources/monte-carlo-templates.md) for spreadsheet templates

### Cost Breakdown Template

```markdown
## Investment Analysis

### Development Time
- Backend development: 120 hours @ $150/hr = $18,000
- Frontend development: 80 hours @ $150/hr = $12,000
- Testing & QA: 40 hours @ $150/hr = $6,000
- **Subtotal Dev:** $36,000

### Infrastructure (18 months)
- Cloud hosting: $500/mo × 18 = $9,000
- AI compute (GPT-4): $300/mo × 18 = $5,400
- Database: $200/mo × 18 = $3,600
- **Subtotal Infra:** $18,000

### Maintenance (annual)
- Bug fixes: $5,000/year
- Feature updates: $8,000/year
- **Subtotal Maintenance:** $13,000

**Total Investment (18mo):** $67,000

### Revenue Projection (18 months)
- Month 1-3: $5k/mo (ramp-up) = $15k
- Month 4-12: $15k/mo (growth) = $135k
- Month 13-18: $25k/mo (mature) = $150k
- **Total Revenue:** $300k

**ROI:** ($300k - $67k) / $67k = 3.48× ✅ PASS
```

---

## Gate 3: Brakes

**Question:** Can we reverse this if it fails? What's the blast radius?

### Checklist

- [ ] **Reversibility:** Rollback steps documented in plan
- [ ] **Blast Radius:** Impact analysis if feature fails
- [ ] **Kill-Switch Triggers:** Metrics that force abort defined
- [ ] **Test Coverage:** ≥98% required for production deployment
- [ ] **Security Review:** Passes security-enforcement skill checks

### Reversibility Requirements

```markdown
## Rollback Steps (Example)

1. **Immediate Rollback (< 5 minutes)**
   - Feature flag: Toggle `NEW_FEATURE_ENABLED=false` in env vars
   - Impact: New feature disabled, old flow resumes
   - Data: No data loss (new tables empty, old tables unchanged)

2. **Database Rollback (if needed)**
   - Run migration: `npm run db:migrate:rollback`
   - Restore backup: `pg_restore -d pnkln_prod backup_2025_11_14.sql`
   - Verify: `SELECT count(*) FROM users WHERE version='old'`

3. **Cleanup (< 1 hour)**
   - Remove new API endpoints from gateway
   - Archive new logs/metrics
   - Notify customers (if beta users affected)

4. **Post-Mortem**
   - Document what failed
   - Update kill-switch triggers
   - Refine gate thresholds
```

### Blast Radius Analysis

```markdown
## Impact Assessment

**If feature fails completely:**

- **Users Affected:** 500 (beta group only, isolated via feature flag)
- **Data Loss Risk:** None (separate tables, no foreign keys)
- **System Dependencies:** 2 internal services (auth, analytics)
- **Revenue Impact:** -$5k/mo if rolled back (lost beta subscriptions)
- **Reputation Risk:** Low (beta users expect issues)

**Blast Radius:** LOW ✅
- Isolated user group
- No data corruption risk
- Quick rollback (<5 min)
- Minimal revenue impact
```

### Kill-Switch Triggers

Auto-abort if ANY of these occur:

- [ ] **Security:** CVSS ≥7.0 vulnerability discovered
- [ ] **Cost:** Overrun >20% vs. budget ($67k → $80k)
- [ ] **Timeline:** Slip >30% vs. plan (12 weeks → 16 weeks)
- [ ] **Quality:** Test coverage drops <98%
- [ ] **Performance:** API latency >500ms (target: <200ms)
- [ ] **Adoption:** <10% of beta users activate feature in 30 days
- [ ] **Revenue:** <50% of projected revenue after 90 days
- [ ] **Consecutive Gates:** Fail 2× related features in same quarter

**See:** [resources/risk-management.md](resources/risk-management.md) for Army RM Stage IV protocols

---

## Decision Matrix

After running all three gates:

| Purpose | Reasons | Brakes | Decision | Action |
|---------|---------|--------|----------|--------|
| ✅ PASS | ✅ PASS | ✅ PASS | **GO** | Implement immediately |
| ✅ PASS | ✅ PASS | ⚠️ CONDITIONAL | **CONDITIONAL GO** | Fix brakes issues first |
| ✅ PASS | ⚠️ CONDITIONAL | ✅ PASS | **CONDITIONAL GO** | Validate financials, then proceed |
| ✅ PASS | ❌ FAIL | ✅ PASS | **NO-GO** | Pivot to higher ROI alternative |
| ⚠️ CONDITIONAL | ✅ PASS | ✅ PASS | **CONDITIONAL GO** | Document strategic alignment |
| ❌ FAIL | * | * | **STOP** | Does not serve founder goals |
| * | ❌ FAIL | ❌ FAIL | **STOP** | High risk, low return |

---

## Usage Examples

### Example 1: Feature Passes All Gates

```markdown
Feature: Add multi-factor authentication (MFA) to ActiveShield

PURPOSE GATE: ✅ PASS
- Strategic Alignment: ActiveShield security vertical (core offering)
- Cor.X Reference: Cor.17 (Zero-trust architecture)
- Classification: Mission-critical

REASONS GATE: ✅ PASS
- ROI: 4.2× in 18 months
  - Investment: $45k (dev + infra)
  - Revenue: $234k (premium tier sales)
- LTV:CAC: 5.1:1 (enterprise customers, low churn)
- NPV: 84% positive probability (Monte Carlo)

BRAKES GATE: ✅ PASS
- Rollback: Feature flag toggle, <5 min
- Blast Radius: Low (optional feature, no breaking changes)
- Kill-Switch: Drop if <30% adoption in 60 days
- Test Coverage: 99.2% (unit + integration)
- Security: Passes all checks (Argon2id, TLS 1.3, Sentry)

DECISION: **GO** - Implement immediately
Next Steps:
1. Create dev docs (/dev-docs MFA implementation)
2. Start Phase 1: Backend auth service
3. Target launch: 6 weeks
```

### Example 2: Feature Fails Reasons Gate

```markdown
Feature: Build custom CRM for lead management

PURPOSE GATE: ⚠️ CONDITIONAL
- Strategic Alignment: Internal tooling (not core product)
- Cor.X Reference: None
- Classification: Nice-to-have

REASONS GATE: ❌ FAIL
- ROI: 1.2× in 18 months (below 3× threshold)
  - Investment: $80k (custom dev)
  - Revenue: $16k (time savings × $150/hr)
- LTV:CAC: N/A (internal tool)
- NPV: 38% positive probability (high uncertainty)

BRAKES GATE: ✅ PASS
- Rollback: Use existing spreadsheets
- Blast Radius: None (no customer impact)

DECISION: **NO-GO** - Use off-the-shelf CRM instead
Alternative: HubSpot ($50/mo) or Pipedrive ($15/mo)
Savings: $79k vs. custom build
Recommendation: Defer custom CRM until Series A (if needed)
```

### Example 3: Feature Needs Gate Optimization

```markdown
Feature: AI-powered contract analysis for ActiveShield

PURPOSE GATE: ✅ PASS
- Strategic Alignment: ActiveShield premium feature
- Cor.X Reference: Cor.34 (AI architecture)
- Classification: High-value

REASONS GATE: ⚠️ CONDITIONAL
- ROI: 2.8× in 18 months (FAIL - below 3×)
  - Investment: $120k (AI dev + compute)
  - Revenue: $456k (projected)
- LTV:CAC: 6.2:1 (PASS - enterprise sales)
- NPV: 72% positive probability (PASS)

BRAKES GATE: ✅ PASS
- Rollback: Manual review process
- Blast Radius: Medium (customer contracts affected)
- Kill-Switch: Accuracy <95% triggers revert

DECISION: **CONDITIONAL GO** - Optimize to hit 3× ROI
Actions to Improve ROI:
1. Reduce AI compute costs (use GPT-4 mini for simple contracts)
2. Increase pricing ($500/mo → $600/mo for AI tier)
3. Target faster adoption (6 months → 4 months to breakeven)

Revised ROI: 3.4× ✅ PASS
Proceed with implementation
```

---

## Progressive Disclosure Resources

Load these files for specific topics:

- **[resources/crm-jr-framework.md](resources/crm-jr-framework.md)** - Enhanced decision framework (Context • Reasons • Mental Models • Judgment • Reversal)
- **[resources/mba-frameworks.md](resources/mba-frameworks.md)** - VRIO, Value Stick, Blue Ocean, McKinsey Three Horizons, Strategy Diamond, Porter's 5 Forces
- **[resources/monte-carlo-templates.md](resources/monte-carlo-templates.md)** - Scenario modeling spreadsheets (Base/Best/Worst cases)

**When to Use Each:**
- **Standard Features (<$50k):** Use ShadowTag-v2JR gates only (Purpose • Reasons • Brakes)
- **Strategic Decisions (>$50k):** Use CRM-JR framework (full analysis with mental models)
- **Complex Decisions:** Add MBA frameworks (VRIO for competitive advantage, Value Stick for pricing, Blue Ocean for positioning)

---

## Integration with Dev Docs

Every large feature should have dev docs with ShadowTag-v2JR gates embedded:

```bash
# Generate dev docs with gates
/dev-docs Add OAuth 2.0 authentication

# Claude creates:
dev/active/oauth-auth/
├── oauth-auth-plan.md      # Includes all three gates
├── oauth-auth-context.md   # Key decisions
└── oauth-auth-tasks.md     # Execution checklist
```

**See:** Slash command `/dev-docs` for automatic generation

---

## Troubleshooting

**Q: My feature failed the Reasons gate. Should I abandon it?**
A: Not necessarily. Options:
1. Optimize economics (reduce cost, increase revenue, faster timeline)
2. Defer to later phase (when CAC is lower)
3. Combine with other features (bundle for higher LTV)
4. Pivot to simpler version (MVP with lower investment)

**Q: Can I override a gate failure?**
A: Yes, but document why:
- Strategic imperative (e.g., regulatory compliance)
- Competitive threat (must match competitor feature)
- Founder decision (explicit override with rationale)

**Q: How often should I re-validate gates?**
A: Every sprint (2 weeks) for in-progress features. If metrics drift >20% from plan, re-run gates.

**Q: What if I'm building a prototype/experiment?**
A: Use "CONDITIONAL GO" with explicit validation criteria:
- Prototype budget: $5k max
- Timeline: 2 weeks max
- Decision criteria: User feedback ≥8/10 to proceed

---

## Success Metrics

Track these to measure gate effectiveness:

- **Gate Pass Rate:** % features passing all gates on first try (target: ≥70%)
- **ROI Accuracy:** Actual ROI vs. projected (review quarterly)
- **Kill-Switch Triggers:** Count of features aborted (lower is better if gates work)
- **Time Saved:** Avoided investment from early NO-GO decisions

---

**Last Updated:** 2025-11-15
**Maintained By:** Pnkln Strategy Team (Erik)
**Framework:** ShadowTag-v2JR (Purpose • Reasons • Brakes)
**Compliance:** Army RM Stage IV, Cor.X Strategic Frameworks
