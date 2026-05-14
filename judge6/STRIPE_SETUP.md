# Stripe Setup Guide for Judge #6
## Complete Billing Integration in 15 Minutes

---

## STEP 1: Create Stripe Account (3 minutes)

1. Go to: https://dashboard.stripe.com/register
2. Sign up with your email
3. Verify email
4. Complete business profile (use "Pnkln" or your legal entity)

✅ **You now have a Stripe account**

---

## STEP 2: Get API Keys (2 minutes)

1. Go to: https://dashboard.stripe.com/test/apikeys
2. Copy **Publishable key** (starts with `pk_test_`)
3. Copy **Secret key** (starts with `sk_test_`)

**Add to `.env`:**
```bash
STRIPE_PUBLISHABLE_KEY="pk_test_YOUR_KEY_HERE"
STRIPE_SECRET_KEY="sk_test_YOUR_KEY_HERE"
```

⚠️ **Important**: Use TEST keys for now. Switch to LIVE keys after Show HN validation.

---

## STEP 3: Create Products & Prices (5 minutes)

### Product #1: Judge #6 Starter

1. Go to: https://dashboard.stripe.com/test/products
2. Click "Add product"
3. Fill in:
   - **Name**: Judge #6 - Starter
   - **Description**: 10,000 AI risk assessments per month
   - **Pricing model**: Standard pricing
   - **Price**: $99.00 USD
   - **Billing period**: Monthly
4. Click "Save product"
5. **Copy the Price ID** (starts with `price_`) → This is `STRIPE_PRICE_STARTER_MONTHLY`

6. Click "Add another price" on the same product
7. Fill in:
   - **Price**: $990.00 USD (2 months free = $99 × 10)
   - **Billing period**: Yearly
8. Click "Save price"
9. **Copy the Price ID** → This is `STRIPE_PRICE_STARTER_ANNUAL`

---

### Product #2: Judge #6 Professional

1. Click "Add product" again
2. Fill in:
   - **Name**: Judge #6 - Professional
   - **Description**: 100,000 AI risk assessments per month + priority support
   - **Pricing model**: Standard pricing
   - **Price**: $499.00 USD
   - **Billing period**: Monthly
3. Click "Save product"
4. **Copy the Price ID** → This is `STRIPE_PRICE_PROFESSIONAL_MONTHLY`

5. Click "Add another price"
6. Fill in:
   - **Price**: $4,990.00 USD ($499 × 10)
   - **Billing period**: Yearly
7. Click "Save price"
8. **Copy the Price ID** → This is `STRIPE_PRICE_PROFESSIONAL_ANNUAL`

---

**Add to `.env`:**
```bash
STRIPE_PRICE_STARTER_MONTHLY="price_YOUR_STARTER_MONTHLY_PRICE_ID"
STRIPE_PRICE_STARTER_ANNUAL="price_YOUR_STARTER_ANNUAL_PRICE_ID"
STRIPE_PRICE_PROFESSIONAL_MONTHLY="price_YOUR_PRO_MONTHLY_PRICE_ID"
STRIPE_PRICE_PROFESSIONAL_ANNUAL="price_YOUR_PRO_ANNUAL_PRICE_ID"
```

---

## STEP 4: Set Up Webhooks (5 minutes)

Webhooks notify Judge #6 when subscriptions are created, updated, or canceled.

### 4A: For Local Testing (Stripe CLI)

```bash
# Install Stripe CLI
brew install stripe/stripe-cli/stripe
# OR: Download from https://stripe.com/docs/stripe-cli

# Login
stripe login

# Forward webhooks to local server
stripe listen --forward-to http://localhost:8000/api/v1/billing/webhook
```

**Copy the webhook secret** (starts with `whsec_`) → Add to `.env`:
```bash
STRIPE_WEBHOOK_SECRET="whsec_YOUR_WEBHOOK_SECRET"
```

---

### 4B: For Production (After Deployment)

1. Go to: https://dashboard.stripe.com/test/webhooks
2. Click "Add endpoint"
3. Fill in:
   - **Endpoint URL**: `https://api.judgeasaservice.ai/api/v1/billing/webhook`
   - **Description**: Judge #6 Production Webhook
   - **Events to send**:
     - `checkout.session.completed`
     - `customer.subscription.created`
     - `customer.subscription.updated`
     - `customer.subscription.deleted`
     - `invoice.payment_failed`
     - `invoice.payment_succeeded`
4. Click "Add endpoint"
5. **Copy the signing secret** → Add to production `.env`

---

## STEP 5: Test the Integration (5 minutes)

### Start Judge #6 with Stripe

```bash
# Make sure .env has all Stripe keys
cd judge6
docker-compose up -d

# Check logs
docker-compose logs -f api
```

### Test Subscription Flow

```bash
# 1. Register a user
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123!",
    "full_name": "Test User"
  }'

# Save the API key from response

# 2. Create checkout session
curl -X POST "http://localhost:8000/api/v1/billing/checkout?tier=starter&annual=false" \
  -H "Authorization: Bearer YOUR_API_KEY_HERE"

# You'll get a checkout_url - open it in browser
```

### Test with Stripe Test Cards

Use these cards in checkout:
- **Success**: `4242 4242 4242 4242` (any future expiry, any CVC)
- **Decline**: `4000 0000 0000 0002`
- **3D Secure**: `4000 0025 0000 3155`

More test cards: https://stripe.com/docs/testing

---

## STEP 6: Verify Webhook Events

After completing checkout, check webhook events:

```bash
# In terminal running stripe listen
# You should see:
# ✔ checkout.session.completed [evt_...]
# → POST http://localhost:8000/api/v1/billing/webhook [200]
```

Check database:
```bash
# User should be upgraded
curl http://localhost:8000/api/v1/billing/subscription \
  -H "Authorization: Bearer YOUR_API_KEY_HERE"

# Response should show tier: "starter"
```

---

## STRIPE CUSTOMER PORTAL

Users can manage their subscriptions via Stripe Customer Portal:

```bash
curl -X POST http://localhost:8000/api/v1/billing/portal \
  -H "Authorization: Bearer YOUR_API_KEY_HERE"

# Returns portal_url - user can:
# - Update payment method
# - View invoices
# - Cancel subscription
# - Download receipts
```

---

## GOING LIVE (After Show HN Validation)

### Switch to Live Mode

1. Go to: https://dashboard.stripe.com/settings/api-keys
2. Toggle "View test data" OFF
3. Copy LIVE keys (start with `pk_live_` and `sk_live_`)
4. Update production `.env`:
   ```bash
   STRIPE_PUBLISHABLE_KEY="pk_live_YOUR_LIVE_KEY"
   STRIPE_SECRET_KEY="sk_live_YOUR_LIVE_KEY"
   ```

### Recreate Products in Live Mode

- Repeat STEP 3 (products & prices) in LIVE mode
- Update `.env` with LIVE price IDs

### Update Webhook Endpoint

- Point webhook to production URL
- Use LIVE webhook secret

---

## PRICING CONFIGURATION

Current pricing (configured in products above):

| Tier | Monthly | Annual | Requests | Savings |
|---|---|---|---|---|
| **Free** | $0 | $0 | 1,000 | - |
| **Starter** | $99 | $990 | 10,000 | 16.7% |
| **Professional** | $499 | $4,990 | 100,000 | 16.7% |
| **Enterprise** | Custom | Custom | Unlimited | Negotiated |

**Annual discount**: 2 months free (12 for the price of 10)

---

## OVERAGE BILLING (Optional - Week 2)

If you want to charge for requests beyond plan limit:

### Option A: Metered Billing

1. In Stripe product, change to "Metered pricing"
2. Set price per unit (e.g., $0.01 per request)
3. Report usage via API:
   ```python
   StripeService.create_usage_record(
       subscription_item_id=item_id,
       quantity=overage_requests
   )
   ```

### Option B: One-Time Charges

- Invoice customer for overages manually
- Or create one-time payment links

**Recommendation**: Start without overage billing. Add in Week 2 if needed.

---

## TROUBLESHOOTING

### "No such price" error
- Check price IDs in `.env` match Stripe Dashboard
- Make sure you're in TEST mode (not LIVE)

### Webhook not receiving events
- Check Stripe CLI is running (`stripe listen`)
- Verify endpoint URL is correct
- Check webhook signing secret in `.env`

### Subscription not updating in database
- Check application logs: `docker-compose logs api`
- Verify webhook handler is processing events
- Check database connection

---

## REVENUE TRACKING

View your revenue in Stripe Dashboard:
- **Metrics**: https://dashboard.stripe.com/test/dashboard
- **Customers**: https://dashboard.stripe.com/test/customers
- **Subscriptions**: https://dashboard.stripe.com/test/subscriptions
- **Revenue**: https://dashboard.stripe.com/test/revenue

---

## NEXT STEPS

✅ Stripe fully integrated
✅ Ready to accept payments

**Week 1 Goal**: Close 1-2 consulting deals ($5K-10K)
**Week 2 Goal**: First Judge #6 subscription ($99+)

Once you have paying customers, you can:
1. Build customer dashboard (shows usage + billing)
2. Add team collaboration features (Professional tier)
3. Implement overage billing
4. Create affiliate program

---

**Questions?** Check Stripe docs: https://stripe.com/docs

**Test your integration**: https://stripe.com/docs/testing

Ready to print money? Let's go.
