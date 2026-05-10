# Stripe Connect Onboarding E2E Test Plan

> Status: PLANNING | Implements: CounselConduit Dual-Billing Engine
> Stripe Account: `acct_1Syh9JEHnWpykeMi`

## Overview

End-to-end test plan for the Stripe Connect onboarding flow that enables
law firms to receive direct payments from clients while CounselConduit
auto-scales the firm's subscription tier.

## Test Scenarios

### 1. Standard Onboarding Flow
```
Lawyer → Create Account → Stripe Connect OAuth → Account Link → Dashboard
```

#### Steps:
1. POST `/billing/onboard` with firm details
2. Receive Stripe Connect account link URL
3. Complete Stripe-hosted onboarding (test mode)
4. Webhook: `account.updated` received
5. GET `/billing/status/{firm_id}` returns `charges_enabled: true`

#### Assertions:
- Connect account created in test mode
- Account link URL is valid and accessible
- Webhook signature verified via HMAC
- Firm billing status updated in Firestore

### 2. Subscription Auto-Scaling
```
Firm usage exceeds Solo tier → Auto-bump to Practice → Notification
```

#### Steps:
1. Seed firm with Solo tier (`price_1TNKSREHnWpykeMiRMDlVgLl`)
2. Simulate 500+ queries in billing period
3. System auto-bumps to Practice tier
4. Webhook: `customer.subscription.updated` received
5. Confirm new price in Stripe dashboard

#### Assertions:
- Tier transition logged in audit trail
- Email notification sent to firm admin
- No service interruption during transition
- Billing attributions correct in Firestore

### 3. Client → Lawyer Payment Flow
```
Client subscribes → Funds → Lawyer Stripe account → Platform fee
```

#### Steps:
1. Create test client payment intent
2. Use test card `4242424242424242`
3. Confirm payment routes to lawyer's Connect account
4. Verify platform fee (application_fee_amount)
5. Check Stripe balance for both accounts

#### Assertions:
- Payment intent status: `succeeded`
- Transfer to connected account visible
- Platform fee matches configured percentage
- Client receipt generated

### 4. Beta Coupon Application
```
Coupon: 3wseBY7Z → 50% off, 3 months, max 100 uses
```

#### Steps:
1. POST `/billing/apply-coupon` with code `3wseBY7Z`
2. Verify discount applied to next invoice
3. Verify coupon usage counter incremented
4. After 3 months, verify full price resumes

### 5. Webhook Security
```
Invalid signature → 400 | Missing signature → 400 | Valid → 200
```

#### Steps:
1. POST `/webhooks/stripe` with no signature → 400
2. POST with wrong signature → 400
3. POST with valid HMAC signature → 200
4. POST duplicate event (idempotency) → 200 (no re-processing)

### 6. Customer Portal
```
Portal: bpc_1TNKSjEHnWpykeMi0qQPoaHm
```

#### Steps:
1. GET `/billing/portal-session` → Stripe-hosted portal link
2. Verify link allows subscription management
3. Verify link allows invoice history access
4. Verify cancellation flow triggers GDPR cascade

## Test Data

| Resource | Test Mode ID |
|----------|-------------|
| Product (Trial) | `prod_UM2XwCF1byjegL` |
| Product (Pro) | `prod_UM2X10cpyay52e` |
| Product (Enterprise) | `prod_UM2XMVp9Er7A0i` |
| Pro Monthly | `price_1TNKSREHnWpykeMiRMDlVgLl` |
| Pro Annual | `price_1TNKSjEHnWpykeMi0S9GCVjy` |
| Enterprise | `price_1TNKSREHnWpykeMi8mrDf4rI` |
| Beta Coupon | `3wseBY7Z` |
| Portal Config | `bpc_1TNKSjEHnWpykeMi0qQPoaHm` |

## Prerequisites

- `STRIPE_SECRET_KEY` (test mode) in `.env`
- `STRIPE_WEBHOOK_SECRET` in `.env`
- Stripe CLI for local webhook forwarding: `stripe listen --forward-to localhost:8000/webhooks/stripe`
- `stripe trigger` for webhook simulation

## CI Integration

Add to `tests/e2e/test_stripe_connect_e2e.py`:
```python
@pytest.mark.e2e
@pytest.mark.stripe
class TestStripeConnect:
    """Stripe Connect onboarding E2E tests (test mode only)."""
    ...
```

Gate: Only run in CI with `STRIPE_SECRET_KEY` present (skip otherwise).
