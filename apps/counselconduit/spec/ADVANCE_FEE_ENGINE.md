# Advance Fee & Payment Engine — Jurisdiction Analysis

> **Status**: Research-backed product specification
> **Sources**: ABA Formal Opinion 505, California State Bar, Rule 1.15

---

## Core Insight: CounselConduit as Revenue-Enabling Infrastructure

CounselConduit does not just create AI usage. It **moves legal revenue earlier in time**.

If the platform helps firms confidently collect an advance flat fee or retainer before
the lawyer begins substantive work, it improves the firm's cash flow immediately.
This makes the software much easier to justify as a must-pay operating expense.

---

## The Legal Mechanics

### ABA Formal Opinion 505
Advance fees, including flat fees, generally **must go into a client trust account**
until earned. Labels like "nonrefundable" or "earned on receipt" do not automatically
eliminate trust-account obligations in most jurisdictions.

### California Exception (Rule 1.15)
California allows advance flat fees to go into **operating** if the lawyer gives
the required written disclosures. Client still remains entitled to a refund of
any unearned amount.

### Trust Account Rules
- Advances for fees ordinarily belong in trust
- State Bar guidance explains when funds must go to IOLTA vs. client-specific non-IOLTA
- The product should **never promise** a universal "earned on receipt" outcome

---

## Business Model Impact (4 Ways)

### 1. ROI Clarity for Law Firms
Software that helps lawyers "research with AI" is discretionary.
Software that converts a scared client into a paid engagement is **essential**.

> A criminal-defense lawyer capturing one additional $2,500 flat-fee engagement
> per month makes our subscription trivial.

### 2. Improved Cash Flow
Solos and small firms lack working capital. Getting paid earlier reduces sensitivity
to our monthly fee and supports a **higher ACV**.

### 3. Stronger Payments Product
Once we sit in the client engagement stream, we're adjacent to:
- Advance flat fees
- Evergreen retainers
- Replenishment rules
- Installment plans
- Jurisdiction-specific trust/operating routing

### 4. Deep Moat (Money is Sticky)
If CounselConduit is where the client converts from "worried prospect" to "paid matter,"
replacing us means changing **intake + compliance + payment + audit trail**.

---

## Product Framing

> ❌ "We help lawyers get paid up front no matter what."
>
> ✅ "We help firms capture advance fees and retainers earlier, with
> jurisdiction-aware trust-account handling, client disclosures, and a
> secure intake record."

---

## Pricing Strategy

| Component | Model |
|-----------|-------|
| **Base subscription** | $399–$3,500/mo (auto-scaling tiers) |
| **Payment processing** | Stripe Connect + platform margin |
| **Matter conversion** | Optional per-conversion fee |

The more directly we tie revenue to collected payments, the less our pricing
gets compared to commodity AI subscriptions.

---

## State-by-State Rules Engine (Required)

The product must support:
- Trust by default
- Operating only where state-specifically permitted (e.g., California)
- Required disclosures per jurisdiction
- Refund logic for unearned portions
- Audit logs for compliance

---

## The Best Version

> "Use my private system, tell me everything there, and if we're moving
> forward, we'll get you engaged and funded right there."

**That is where the business model becomes much more powerful.**
